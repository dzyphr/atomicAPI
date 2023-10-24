import json, os, json_tools, configparser
from datetime import datetime
from AtomicityInterface import *
from SigmaParticleInterface import *
from ElGamalInterface import *
from file_tools import *
from config_tools import *
py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "




# we need to assume we have the ENC file saved already
def process_initiation(ENC_filepath, DEC_filepath, SenderPubKey, UserKeyFileName): #this is generic to any enc_message actually
    clean_file_open(ENC_filepath, "r")
    decrypt = ElGamal_Decrypt(ENC_filepath, SenderPubKey, UserKeyFileName) #TODO verify initiation details including json sanity
    clean_file_open(DEC_filepath, "w", decrypt)


def response(DEC_initiation_filepath, responderMasterJSONPATH, response_filepath, SenderPubKey, UserKeyFileName):
    j_init = json.loads(clean_file_open(DEC_initiation_filepath, "r"))
    ksG = j_init["ksG"]
    j_master = json.loads(clean_file_open(responderMasterJSONPATH, "r"))
    swapName = j_master["swapName"]
    sr_filepath = swapName + "/sr"
    x_filepath = swapName + "/x"
    responderMessageContent = str(datetime.now())
    command = \
        py + AtomicSwapECCPath + "p2Respond " +\
        "'" + ksG  + "' " + "'" + responderMessageContent  + "' " + \
        sr_filepath + s_ + x_filepath 
    response = os.popen(command).read()
    clean_file_open(response_filepath, "w", response)
    sr = clean_file_open(sr_filepath, "r")
    x = clean_file_open(x_filepath, "r")
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
                "responderJSONPath" : swapName + "/responder.json",
                "ResponderEVMAddr" : \
                        valFromConf("EVM/Atomicity/" + responderLocalChainAccountName.replace('"', '') + "/.env", 'SepoliaSenderAddr').replace('"', ''),
                "ResponderEIP3Secret" : \
                        valFromConf("Ergo/SigmaParticle/" + responderCrossChainAccountName.replace('"', '') + "/.env", 'senderEIP3Secret').replace('"', ''),
                "ResponderErgoAddr" : \
                        valFromConf("Ergo/SigmaParticle/" + responderCrossChainAccountName.replace('"', '') + "/.env", 'senderPubKey').replace('"', ''),
                "ENC_Init_PATH" : swapName + "/ENC_init.bin", #responder needs to save ENC init to this path to proceed
                "DEC_Init_PATH" : swapName + "/DEC_init.json",
                "responsePATH" : swapName + "/response_path.json",
                "ENC_Response_PATH" : swapName + "/ENC_response_path.bin",
                "ENC_finalizationPATH" : swapName + "/ENC_finalization.bin",
                "DEC_finalizationPATH" : swapName + "/DEC_finalization.json",
            }
        clean_mkdir(mi["swapName"])
        clean_file_open(mi["responderJSONPath"], "w", json.dumps(mi))
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
        xG = json.loads(clean_file_open(responsePATH, "r"))["xG"]
        Atomicity_buildScalarContract(ResponderChain, InitiatorEVMAddr,  xG, 100, swapname)
        addr = Atomicity_deployEVMContract(swapname, customGasMod=3)
        if addr != "fail":
            #ASSUMING ITS ENDING WITH \n
            addr  =  addr[:-1]
        else:
            print("fail: deployContract() didnt return a contract addr")
            exit()
        #add contract addr and chain name to response here then encrypt
        #convert swap amount to wei
        #0.00059eth
        oneWei = 1000000000000000000
        responderFundingAmountWei = int(float(swapAmount) * oneWei)

        Atomicity_SendFunds(addr, responderFundingAmountWei, swapname, gasMod=3)
        update_response_keyValList = [{"responderLocalChain":ResponderChain}, \
                {"responderContractAddr":addr},\
                {"ResponderErgoAddr":ResponderErgoAddr}]
        json_tools.keyVal_list_update(update_response_keyValList, responsePATH)
        responseLIST = json_tools.json_to_keyValList(responsePATH)
        json_tools.keyVal_list_update(responseLIST, responderJSONPath)
        encrypted_response = ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, responsePATH, ENC_Response_PATH)
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
        DEC_finalization = ElGamal_Decrypt(ENC_finalizationPATH, ElGamalKey, ElGamalKeyPath)
        clean_file_open(DEC_finalizationPATH, "w", DEC_finalization)
        finalization_list = json_tools.json_to_keyValList(DEC_finalizationPATH)
        json_tools.keyVal_list_update(finalization_list, responderJSONPath)
        boxID = json.loads(DEC_finalization)["boxId"]
        boxValue = checkBoxValue(boxID, swapName + "/testBoxValPath.bin")
        #other than just the box value responder should verify the scalars in the contract match those expected
        minBoxValue = 1123841 #1123841
        if int(boxValue) < int(minBoxValue):
            print("not enough nanoerg in contract")
            exit()
        SigmaParticle_newFrame(swapName)
        SigmaParticle_updateKeyEnv(swapName, responderErgoAccountName)
        responderGenerateAtomicSchnorr(swapName, DEC_finalizationPATH, responderJSONPath, boxValue)
        expectedErgoTree = SigmaParticle_getTreeFromBox(boxID)
        if responderVerifyErgoScript(swapName, expectedErgoTree) == False:
            print("ergoScript verification returned false, wont fulfil swap")
            exit()
    #    print("ergo contract verification status:", responderVerifyErgoScript(swapName, expectedErgoTree))
        responderClaimAtomicSchnorr(swapName, 2500)
    ################################################################################


