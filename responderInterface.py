import json, os, json_tools, configparser
import time
from datetime import datetime
import AtomicityInterface
import SigmaParticleInterface
import ElGamalInterface
import file_tools
import price_tools
import config_tools
py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "

MIN_CLAIM_LOCKTIME_ERGOTESTNET = int(config_tools.valFromConf(".env", "MIN_CLAIM_LOCKTIME_ERGOTESTNET"))
MIN_REFUND_LOCKTIME_SEPOLIA = int(config_tools.valFromConf(".env", "MIN_REFUND_LOCKTIME_SEPOLIA"))
SEPOLIA_EVM_GAS_CONTROL = int(config_tools.valFromConf(".env", "SEPOLIA_EVM_GAS_CONTROL"))
SEPOLIA_EVM_GASMOD_CONTROL = int(config_tools.valFromConf(".env", "SEPOLIA_EVM_GASMOD_CONTROL"))

# we need to assume we have the ENC file saved already
def process_initiation(ENC_filepath, DEC_filepath, SenderPubKey, UserKeyFileName): #this is generic to any enc_message actually
    file_tools.clean_file_open(ENC_filepath, "r")
    decrypt = ElGamalInterface.ElGamal_Decrypt(ENC_filepath, SenderPubKey, UserKeyFileName) #TODO verify initiation details including json sanity
    file_tools.clean_file_open(DEC_filepath, "w", decrypt)


def response(DEC_initiation_filepath, responderMasterJSONPATH, response_filepath, SenderPubKey, UserKeyFileName):
    j_init = json.loads(file_tools.clean_file_open(DEC_initiation_filepath, "r"))
    ksG = j_init["ksG"]
    j_master = json.loads(file_tools.clean_file_open(responderMasterJSONPATH, "r"))
    swapName = j_master["swapName"]
    sr_filepath = swapName + "/sr"
    x_filepath = swapName + "/x"
    responderMessageContent = str(datetime.now())
    command = \
        py + AtomicSwapECCPath + "p2Respond " +\
        "'" + ksG  + "' " + "'" + responderMessageContent  + "' " + \
        sr_filepath + s_ + x_filepath 
    response = os.popen(command).read()
    file_tools.clean_file_open(response_filepath, "w", response)
    sr = file_tools.clean_file_open(sr_filepath, "r")
    x = file_tools.clean_file_open(x_filepath, "r")
    secretslist = [{"sr":sr}, {"x":x}]
    json_tools.keyVal_list_update(secretslist, responderMasterJSONPATH)

def GeneralizeENC_ResponseSubroutine(\
        swapName, responderCrossChainAccountName, responderLocalChainAccountName, \
        ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain, swapAmount):
    mi = {}
    if InitiatorChain == "TestnetErgo" and ResponderChain == "Sepolia":
        mi = {
                "responderErgoAccountName": responderCrossChainAccountName,
                "responderSepoliaAccountName": responderLocalChainAccountName,
                "ElGamalKey" : ElGamalKey,
                "ElGamalKeyPath" : ElGamalKeyPath,
                "swapName" : swapName,
                "InitiatorChain" : InitiatorChain,
                "ResponderChain" : ResponderChain,
                "responderLocalChain": ResponderChain,
                "responderJSONPath" : swapName + "/responder.json",
                "ResponderEVMAddr" : \
                        config_tools.valFromConf("EVM/Atomicity/" + responderLocalChainAccountName.replace('"', '') + "/.env", 'SepoliaSenderAddr').replace('"', ''),
                "ResponderEIP3Secret" : \
                        config_tools.valFromConf("Ergo/SigmaParticle/" + responderCrossChainAccountName.replace('"', '') + "/.env", 'senderEIP3Secret').replace('"', ''),
                "ResponderErgoAddr" : \
                        config_tools.valFromConf("Ergo/SigmaParticle/" + responderCrossChainAccountName.replace('"', '') + "/.env", 'senderPubKey').replace('"', ''),
                "ENC_Init_PATH" : swapName + "/ENC_init.bin", #responder needs to save ENC init to this path to proceed
                "DEC_Init_PATH" : swapName + "/DEC_init.json",
                "responsePATH" : swapName + "/response_path.json",
                "ENC_Response_PATH" : swapName + "/ENC_response_path.bin",
                "ENC_finalizationPATH" : swapName + "/ENC_finalization.bin",
                "DEC_finalizationPATH" : swapName + "/DEC_finalization.json",
            }
        file_tools.clean_mkdir(mi["swapName"])
        file_tools.clean_file_open(mi["responderJSONPath"], "w", json.dumps(mi))
        resp_J = json_tools.ojf(mi["responderJSONPath"])
        swapname = resp_J["swapName"]
        ENC_Init_PATH = resp_J["ENC_Init_PATH"]
        DEC_Init_PATH = resp_J["DEC_Init_PATH"]
        ElGamalKey = resp_J["ElGamalKey"]
        ElGamalKeyPath = resp_J["ElGamalKeyPath"]
        responsePATH = resp_J["responsePATH"]
        ENC_Response_PATH = resp_J["ENC_Response_PATH"]
        ResponderChain = resp_J["ResponderChain"]
        ResponderErgoAddr = resp_J["ResponderErgoAddr"]
        responderJSONPath = mi["responderJSONPath"]
        process_initiation(ENC_Init_PATH, DEC_Init_PATH, ElGamalKey, ElGamalKeyPath)
        r_initiation_keyValList = json_tools.json_to_keyValList(DEC_Init_PATH)
        json_tools.keyVal_list_update(r_initiation_keyValList, mi["responderJSONPath"])
        resp_J = json_tools.ojf(mi["responderJSONPath"])
    #    InitiatorEVMAddr = resp_J["InitiatorEVMAddr"] TODO generalize this
        temprenamelist = [{"InitiatorEVMAddr": resp_J["SepoliaChainPubkey"]}]
        json_tools.keyVal_list_update(temprenamelist, mi["responderJSONPath"])
        resp_J = json_tools.ojf(mi["responderJSONPath"])
        InitiatorEVMAddr = resp_J["InitiatorEVMAddr"]
        response(DEC_Init_PATH, responderJSONPath, \
                responsePATH, ElGamalKey, ElGamalKeyPath)
        #TODO: replace sr and x paths with master json update
        xG = json.loads(file_tools.clean_file_open(responsePATH, "r"))["xG"]
        AtomicityInterface.Atomicity_buildScalarContract(ResponderChain, InitiatorEVMAddr,  xG, MIN_REFUND_LOCKTIME_SEPOLIA, swapname)
        addr = AtomicityInterface.Atomicity_deployEVMContract(swapname, customGas=SEPOLIA_EVM_GAS_CONTROL, customGasMod=SEPOLIA_EVM_GASMOD_CONTROL)
        if addr != "fail":
            #ASSUMING ITS ENDING WITH \n
            addr  =  addr[:-1]
        else:
            print("fail: deployContract() didnt return a contract addr")
            exit()

        #add contract addr and chain name to response here then encrypt
        #convert swap amount to wei
        #0.00059eth
#        oneWei = 1000000000000000000
#        responderFundingAmountWei = int(float(swapAmount) * oneWei)
        responderFundingAmountWei = price_tools.EthToWei(swapAmount)

        AtomicityInterface.Atomicity_SendFunds(addr, responderFundingAmountWei, swapname, gas=SEPOLIA_EVM_GAS_CONTROL, gasMod=SEPOLIA_EVM_GASMOD_CONTROL)
        update_response_keyValList = [{"responderLocalChain":ResponderChain}, \
                {"responderContractAddr":addr},\
                {"ResponderErgoAddr":ResponderErgoAddr}]
        json_tools.keyVal_list_update(update_response_keyValList, responsePATH)
        j_response = json_tools.ojf(responsePATH)
        while int(AtomicityInterface.Atomicity_CheckContractFunds(swapname, j_response)) <= 0:
            print("contract not funded yet waiting...")
            time.sleep(5)
        responseLIST = json_tools.json_to_keyValList(responsePATH)
        json_tools.keyVal_list_update(responseLIST, responderJSONPath)
        encrypted_response = ElGamalInterface.ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, responsePATH, ENC_Response_PATH)
        return ENC_Response_PATH

def GeneralizedENC_ResponderClaimSubroutine(responderJSONPath):
 ############## RESPONDER #######################################################
    resp_J = json_tools.ojf(responderJSONPath)
    if resp_J["InitiatorChain"] == "TestnetErgo" and resp_J["ResponderChain"] == "Sepolia":
        swapName = resp_J["swapName"]
        ENC_finalizationPATH = resp_J["ENC_finalizationPATH"]
        ElGamalKey = resp_J["ElGamalKey"]
        ElGamalKeyPath = resp_J["ElGamalKeyPath"]
        DEC_finalizationPATH = resp_J["DEC_finalizationPATH"]
        responderErgoAccountName = resp_J["responderErgoAccountName"]
        DEC_finalization = ElGamalInterface.ElGamal_Decrypt(ENC_finalizationPATH, ElGamalKey, ElGamalKeyPath)
        file_tools.clean_file_open(DEC_finalizationPATH, "w", DEC_finalization)
        finalization_list = json_tools.json_to_keyValList(DEC_finalizationPATH)
        json_tools.keyVal_list_update(finalization_list, responderJSONPath)
        boxID = json.loads(DEC_finalization)["boxId"]
        boxValue = SigmaParticleInterface.checkBoxValue(boxID, swapName + "/testBoxValPath.bin", swapName, role="responder")
        j_response = json_tools.ojf(resp_J["responsePATH"])
        if boxValue == 0:
            print("refund tried, swap aborting")
            while True:
                if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName) <= 0:
                    AtomicityInterface.Atomicity_Refund(swapName, "responder", gas=SEPOLIA_EVM_GAS_CONTROL, gasMod=SEPOLIA_EVM_GASMOD_CONTROL)
                    break
                time.sleep(3)
            exit()
        #other than just the box value responder should verify the scalars in the contract match those expected
        remoteLockTime = SigmaParticleInterface.SigmaParticle_CheckLockTimeAtomicSchnorr(swapName, boxID)
        if remoteLockTime < MIN_CLAIM_LOCKTIME_ERGOTESTNET:
            while True:
                if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName) <= 0:
                    AtomicityInterface.Atomicity_Refund(swapName, "responder",  gas=SEPOLIA_EVM_GAS_CONTROL, gasMod=SEPOLIA_EVM_GASMOD_CONTROL)
                    break
                time.sleep(3)
            print("lock time is below safe minimum for claiming, refunding swap")
            exit()
        minBoxValue = 1123841 #1123841
        if int(boxValue) < int(minBoxValue):
            while True:
                if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName) <= 0:
                    AtomicityInterface.Atomicity_Refund(swapName, "responder",  gas=SEPOLIA_EVM_GAS_CONTROL, gasMod=SEPOLIA_EVM_GASMOD_CONTROL)
                    break
                time.sleep(3)
            print("not enough nanoerg in contract, refunging swap")
            exit()
        SigmaParticleInterface.SigmaParticle_newFrame(swapName)
        SigmaParticleInterface.SigmaParticle_updateKeyEnv(swapName, responderErgoAccountName)
        SigmaParticleInterface.responderGenerateAtomicSchnorr(swapName, DEC_finalizationPATH, responderJSONPath, boxValue)
        expectedErgoTree = SigmaParticleInterface.SigmaParticle_getTreeFromBox(boxID)
        if SigmaParticleInterface.responderVerifyErgoScript(swapName, expectedErgoTree) == False:
            print("ergoScript verification returned false, wont fulfil swap")
            exit()
    #    print("ergo contract verification status:", responderVerifyErgoScript(swapName, expectedErgoTree))
        SigmaParticleInterface.responderClaimAtomicSchnorr(swapName, 2500)
    ################################################################################

def Responder_CheckLockTimeRefund(swapName):
    resp_J = json_tools.ojf(swapName + "/responder.json")
    j_response = json_tools.ojf(resp_J["responsePATH"])
    swapName = resp_J["swapName"]
    while True:
        if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName) <= 0 and int(AtomicityInterface.Atomicity_CheckContractFunds(j_response)) != 0:
            print(AtomicityInterface.Atomicity_Refund(swapName, "responder"))
            time.sleep(10)
            #we may want to alter the smart contract to enforce that funds are in the 
            #contract before sender reclaim can be called
            #will completely prevent fee waste on mainnet
            print("lock time expired, refund attempted")
        else:
            if int(AtomicityInterface.Atomicity_CheckContractFunds(j_response)) != 0:
                time.sleep(3)
                continue
            else:
                break
    print("contract empty / timelock expired")

