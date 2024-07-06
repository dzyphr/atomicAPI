import json, os, json_tools, configparser
import time
from datetime import datetime
import AtomicityInterface
import SigmaParticleInterface
import ElGamalInterface
import file_tools
import price_tools
import config_tools
import swap_tools
from LOG import LOG
from passwordFileEncryption import get_val_from_envdata_key, decrypt_file_return_contents
py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "



MIN_CLAIM_LOCKTIME_ERGOTESTNET = int(config_tools.valFromConf(".env", "MIN_CLAIM_LOCKTIME_ERGOTESTNET"))
MIN_REFUND_LOCKTIME_SEPOLIA = int(config_tools.valFromConf(".env", "MIN_REFUND_LOCKTIME_SEPOLIA"))
SEPOLIA_EVM_GAS_CONTROL = int(config_tools.valFromConf(".env", "SEPOLIA_EVM_GAS_CONTROL"))
SEPOLIA_EVM_GASMOD_CONTROL = int(config_tools.valFromConf(".env", "SEPOLIA_EVM_GASMOD_CONTROL"))

# we need to assume we have the ENC file saved already
def process_initiation(ENC_filepath, DEC_filepath, SenderPubKey, UserKeyFileName): #this is generic to any enc_message actually
    LOG('process_initiation')
    file_tools.clean_file_open(ENC_filepath, "r")
    decrypt = ElGamalInterface.ElGamal_Decrypt(ENC_filepath, SenderPubKey, UserKeyFileName) #TODO verify initiation details including json sanity
    LOG(f'initiation: {decrypt}')
    file_tools.clean_file_open(DEC_filepath, "w", decrypt)


def response(DEC_initiation_filepath, responderMasterJSONPATH, response_filepath, SenderPubKey):
    LOG('response')
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
    LOG('response: {response}')
    file_tools.clean_file_open(response_filepath, "w", response)
    sr = file_tools.clean_file_open(sr_filepath, "r")
    x = file_tools.clean_file_open(x_filepath, "r")
    secretslist = [{"sr":sr}, {"x":x}]
    json_tools.keyVal_list_update(secretslist, responderMasterJSONPATH)

def GeneralizeENC_ResponseSubroutine(\
        swapName, responderCrossChainAccountName, responderLocalChainAccountName, \
        ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain, swapAmount, \
        localChainAccountPassword="", crossChainAccountPassword="", reloadSwapState="" \
):
    LOG('GeneralizeENC_ResponseSubroutine')
    def setup(
            swapName, responderCrossChainAccountName, responderLocalChainAccountName, \
            ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain, swapAmount,
            localChainAccountPassword="", crossChainAccountPassword=""
        ):
        LOG('setup')
        mi = {}
        localChainAccountEnvData = ""
        crossChainAccountEnvData = ""
        crossChainEncAccount = False
        localChainEncAccount = False
        ErgoPath = "Ergo/SigmaParticle/" + responderCrossChainAccountName + "/.env.encrypted"
        SepoliaPath = "EVM/Atomicity/" + responderLocalChainAccountName + "/.env.encrypted"
        if os.path.isfile(ErgoPath):
            if InitiatorChain == "TestnetErgo":
                if crossChainAccountPassword != "":
                    crossChainAccountEnvData = decrypt_file_return_contents(ErgoPath, crossChainAccountPassword)
                    crossChainEncAccount = True
                else:
                    print("password required for encrypted env file!")
                    return
            #ergo encrypted
        if os.path.isfile(SepoliaPath):
            if ResponderChain == "Sepolia":
                if localChainAccountPassword != "":
                    localChainAccountEnvData = decrypt_file_return_contents(SepoliaPath, localChainAccountPassword)
                    localChainEncAccount = True
                else:
                    print("password required for encrypted env file!")
                    return
            #sepolia encrypted
        if localChainEncAccount == False and crossChainEncAccount == False:
            if InitiatorChain.strip("\"") == "TestnetErgo" and ResponderChain.strip("\"") == "Sepolia":
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
                        "SwapAmount" : swapAmount
                    }
        if localChainEncAccount == True and crossChainEncAccount == False:
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
                                get_val_from_envdata_key('SepoliaSenderAddr', localChainAccountEnvData).replace('"', ''),
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
                        "SwapAmount" : swapAmount
                    }
        if localChainEncAccount == False and crossChainEncAccount == True:
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
                                get_val_from_envdata_key('senderEIP3Secret', crossChainAccountEnvData).replace('"', ''),
                        "ResponderErgoAddr" : \
                                get_val_from_envdata_key('senderPubKey', crossChainAccountEnvData).replace('"', ''),
                        "ENC_Init_PATH" : swapName + "/ENC_init.bin", #responder needs to save ENC init to this path to proceed
                        "DEC_Init_PATH" : swapName + "/DEC_init.json",
                        "responsePATH" : swapName + "/response_path.json",
                        "ENC_Response_PATH" : swapName + "/ENC_response_path.bin",
                        "ENC_finalizationPATH" : swapName + "/ENC_finalization.bin",
                        "DEC_finalizationPATH" : swapName + "/DEC_finalization.json",
                        "SwapAmount" : swapAmount
                    }
        elif localChainEncAccount == True and crossChainEncAccount == True:
            if InitiatorChain.strip("\"") == "TestnetErgo" and ResponderChain.strip("\"") == "Sepolia":
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
                                get_val_from_envdata_key('SepoliaSenderAddr', localChainAccountEnvData).replace('"', ''),
                        "ResponderEIP3Secret" : \
                                get_val_from_envdata_key('senderEIP3Secret', crossChainAccountEnvData).replace('"', ''),
                        "ResponderErgoAddr" : \
                                get_val_from_envdata_key('senderPubKey', crossChainAccountEnvData).replace('"', ''),
                        "ENC_Init_PATH" : swapName + "/ENC_init.bin", #responder needs to save ENC init to this path to proceed
                        "DEC_Init_PATH" : swapName + "/DEC_init.json",
                        "responsePATH" : swapName + "/response_path.json",
                        "ENC_Response_PATH" : swapName + "/ENC_response_path.bin",
                        "ENC_finalizationPATH" : swapName + "/ENC_finalization.bin",
                        "DEC_finalizationPATH" : swapName + "/DEC_finalization.json",
                        "SwapAmount" : swapAmount
                    }

        file_tools.clean_mkdir(mi["swapName"])
        file_tools.clean_file_open(mi["responderJSONPath"], "w", json.dumps(mi))
        resp_J = json_tools.ojf(mi["responderJSONPath"])
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
        swap_tools.setSwapState(swapName, "initiated", setMap=True) #set swap state to initiated
        return ENC_Init_PATH, DEC_Init_PATH, ElGamalKey, \
                ElGamalKeyPath, responsePATH, ENC_Response_PATH, \
                ResponderChain, ResponderErgoAddr, responderJSONPath, \
                resp_J, InitiatorEVMAddr

    def startResponse(
            DEC_Init_PATH, responderJSONPath, responsePATH,
            ElGamalKey, ResponderChain, InitiatorEVMAddr,
            swapName, localChainAccountPassword=""
        ):
        LOG('startResponse')
        response(
                DEC_Init_PATH, responderJSONPath, \
                responsePATH, ElGamalKey
        ) #ElGamalKeyPath)
        #TODO: replace sr and x paths with master json update
        respJ = json_tools.ojf(responderJSONPath)
        responderLocalChainAccountName = resp_J["responderSepoliaAccountName"]
        xG = json.loads(file_tools.clean_file_open(responsePATH, "r"))["xG"]
        AtomicityInterface.Atomicity_buildScalarContract(ResponderChain, InitiatorEVMAddr,  xG, MIN_REFUND_LOCKTIME_SEPOLIA, swapName)
        AtomicityInterface.Atomicity_updateKeyEnv(swapName, responderLocalChainAccountName)
        swap_tools.setSwapState(swapName, "uploadingResponseContract", setMap=True)
        addr = AtomicityInterface.Atomicity_deployEVMContract(
                swapName, customGas=SEPOLIA_EVM_GAS_CONTROL,
                customGasMod=SEPOLIA_EVM_GASMOD_CONTROL, password=localChainAccountPassword
        )
        if addr != "fail":
            #ASSUMING ITS ENDING WITH \n
            addr  =  addr[:-1]
            LOG(f'addr: {addr}')
        else:
            LOG(f'fail: deployContract() didnt return a contract addr')
            print("fail: deployContract() didnt return a contract addr")
            return
        swapAmount = json_tools.ojf(responderJSONPath)["SwapAmount"]
        responderFundingAmountWei = price_tools.EthToWei(swapAmount)
        #TODO save to resp_J?
        swap_tools.setSwapState(swapName, "uploadedResponseContract", setMap=True)
        return addr, responderFundingAmountWei
        
    def fund(
            addr, responderFundingAmountWei, ResponderChain, ResponderErgoAddr, responsePATH
        ):
        LOG('fund')
        swap_tools.setSwapState(swapName, "fundingResponseContract", setMap=True)
        update_response_keyValList = [{"responderLocalChain":ResponderChain}, \
                {"responderContractAddr":addr},\
                {"ResponderErgoAddr":ResponderErgoAddr}]
        json_tools.keyVal_list_update(update_response_keyValList, responsePATH)
        j_response = json_tools.ojf(responsePATH)
        AtomicityInterface.Atomicity_SendFunds(
                addr, responderFundingAmountWei, swapName,
                gas=SEPOLIA_EVM_GAS_CONTROL, gasMod=SEPOLIA_EVM_GASMOD_CONTROL, password=localChainAccountPassword
        )
        while int(AtomicityInterface.Atomicity_CheckContractFunds(swapName, j_response, password=localChainAccountPassword)) <= 0:
            waittime = 5
            print("contract not funded yet waiting...")
            LOG(f'contract not funded yet waiting {waittime} seconds')
            time.sleep(waittime)
        swap_tools.setSwapState(swapName, "fundedResponseContract", setMap=True)

    def completeResponse(
            addr, swapAmount,
            responsePATH, responderJSONPath, ElGamalKey, ElGamalKeyPath,
            ENC_Response_PATH, localChainAccountPassword=""
        ):
        LOG('completeResponse')
        swap_tools.setSwapState(swapName, "responding", setMap=True)
        responseLIST = json_tools.json_to_keyValList(responsePATH)
        json_tools.keyVal_list_update(responseLIST, responderJSONPath)
        encrypted_response = ElGamalInterface.ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, responsePATH, ENC_Response_PATH)
        swap_tools.setSwapState(swapName, "responded_unsubmitted", setMap=True)

    if reloadSwapState != "":
        print("reloading swap: ", swapName)
        if reloadSwapState in [swap_tools.PossibleSwapStates[0], swap_tools.PossibleSwapStates[1]]: 
            #initiated or uploadingResponseContract 

            #TODO if uploading make sure its not in progress aka that its a failed tx and ensure it should continue:
            #things that might influence that are the time elapsed since the initiation and feedback from the responder's UI
            resp_J = json_tools.ojf(swapName + "/responder.json")
            DEC_Init_PATH = resp_J["DEC_Init_PATH"]
            responderJSONPath = swapName + "/responder.json"
            responsePATH = resp_J["responsePATH"]
            ElGamalKey = resp_J["ElGamalKey"]
            ElGamalKeyPath = resp_J["ElGamalKeyPath"]
            ResponderChain = resp_J["ResponderChain"]
            InitiatorEVMAddr = resp_J["InitiatorEVMAddr"]
            ResponderErgoAddr = resp_J["ResponderErgoAddr"]
            ENC_Response_PATH = resp_J["ENC_Response_PATH"]
            addr, responderFundingAmountWei = startResponse(
                    DEC_Init_PATH, responderJSONPath, responsePATH, 
                    ElGamalKey, ResponderChain, InitiatorEVMAddr, 
                    swapName, localChainAccountPassword=localChainAccountPassword
            )
            fund(addr, responderFundingAmountWei, ResponderChain, ResponderErgoAddr,
                    responsePATH)

            completeResponse(
                    addr, swapAmount,  responsePATH, responderJSONPath, ElGamalKey, ElGamalKeyPath,
                    ENC_Response_PATH, localChainAccountPassword=localChainAccountPassword
            )

            return
            #TODO return some data to indicate that this swap needs to be resumed from its next step
            #inform UI or rest server that it needs to keep track of its state from that point forward
            #maybe just give feedback to ui while running the claim loop after a response reload
        if reloadSwapState in [swap_tools.PossibleSwapStates[2], swap_tools.PossibleSwapStates[3]]  : #funding response contract #TODO verify it hasnt been funded yet
                                                                                        #w a contract balance call
            resp_J = json_tools.ojf(swapName + "/responder.json")
            addr = resp_J["responderContractAddr"]
            swapAmount = resp_J["swapAmount"]
            ResponderChain = resp_J["ResponderChain"]
            ResponderErgoAddr = resp_J["ResponderErgoAddr"]
            responsePATH = resp_J["responsePATH"]
            responderJSONPath = resp_J["responderJSONPath"]
            ElGamalKey = resp_J["ElGamalKey"]
            ElGamalKeyPath = resp_J["ElGamalKeyPath"]
            ENC_Response_PATH = resp_J["ENC_Response_PATH"]
            responderFundingAmountWei = price_tools.EthToWei(swapAmount)
            j_response = json.tools.ojf(responsePATH)
            if int(AtomicityInterface.Atomicity_CheckContractFunds(swapName, j_response, password=localChainAccountPassword)) <= 0:
                #TODO check against specific funding amount
                fund(addr, responderFundingAmountWei, ResponderChain, ResponderErgoAddr,
                        responsePATH)

            completeResponse(
                    addr, swapAmount,  responsePATH, responderJSONPath, ElGamalKey, ElGamalKeyPath,
                    ENC_Response_PATH, localChainAccountPassword=localChainAccountPassword
            )
            return
        if reloadSwapState in [swap_tools.PossibleSwapStates[4], swap_tools.PossibleSwapStates[5]]: #funded or responding
            resp_J = json_tools.ojf(swapName + "/responder.json")
            addr = resp_J["responderContractAddr"]
            swapAmount = resp_J["swapAmount"]
            ResponderChain = resp_J["ResponderChain"]
            ResponderErgoAddr = resp_J["ResponderErgoAddr"]
            responsePATH = resp_J["responsePATH"]
            responderJSONPath = resp_J["responderJSONPath"]
            ElGamalKey = resp_J["ElGamalKey"]
            ElGamalKeyPath = resp_J["ElGamalKeyPath"]
            ENC_Response_PATH = resp_J["ENC_Response_PATH"]
            completeResponse(
                    addr, swapAmount,  responsePATH, responderJSONPath, ElGamalKey, ElGamalKeyPath,
                    ENC_Response_PATH, localChainAccountPassword=localChainAccountPassword
            )
            return


    ENC_Init_PATH, \
        DEC_Init_PATH, \
        ElGamalKey, \
        ElGamalKeyPath, \
        responsePATH, \
        ENC_Response_PATH, \
        ResponderChain, \
        ResponderErgoAddr, \
        responderJSONPath, \
        resp_J, \
        InitiatorEVMAddr = \
            setup(\
                swapName, responderCrossChainAccountName, responderLocalChainAccountName, \
                ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain, swapAmount,
                localChainAccountPassword=localChainAccountPassword, crossChainAccountPassword=crossChainAccountPassword\
            )

    addr, responderFundingAmountWei = \
            startResponse(
                    DEC_Init_PATH, responderJSONPath, responsePATH, 
                    ElGamalKey, ResponderChain, InitiatorEVMAddr, 
                    swapName, localChainAccountPassword=localChainAccountPassword
            )

    fund(addr, responderFundingAmountWei, ResponderChain, ResponderErgoAddr,
            responsePATH)

    completeResponse(
            addr, swapAmount,  responsePATH, responderJSONPath, ElGamalKey, ElGamalKeyPath, 
            ENC_Response_PATH, localChainAccountPassword=localChainAccountPassword
    )
    return ENC_Response_PATH

def GeneralizedENC_ResponderClaimSubroutine(
        responderJSONPath, localChainAccountPassword="", crossChainAccountPassword="", reloadSwapState=""
    ):
    LOG('GeneralizedENC_ResponderClaimSubroutine')
    resp_J = json_tools.ojf(responderJSONPath)
    if resp_J["InitiatorChain"] == "TestnetErgo" and resp_J["ResponderChain"] == "Sepolia":
        def setup(resp_J):
            LOG('setup')
            swapName = resp_J["swapName"]
            ENC_finalizationPATH = resp_J["ENC_finalizationPATH"]
            ElGamalKey = resp_J["ElGamalKey"]
            ElGamalKeyPath = resp_J["ElGamalKeyPath"]
            DEC_finalizationPATH = resp_J["DEC_finalizationPATH"]
            responderErgoAccountName = resp_J["responderErgoAccountName"]
            DEC_finalization = ElGamalInterface.ElGamal_Decrypt(ENC_finalizationPATH, ElGamalKey, ElGamalKeyPath)
            file_tools.clean_file_open(DEC_finalizationPATH, "w", DEC_finalization)
            swap_tools.setSwapState(swapName, "finalized", setMap=True)
            return swapName, ENC_finalizationPATH, ElGamalKey, \
                    ElGamalKeyPath, DEC_finalizationPATH, responderErgoAccountName, DEC_finalization

        def verify(\
                DEC_finalizationPATH, responderJSONPath, DEC_finalization,\
                swapName, responderErgoAccountName, localChainAccountPassword="", crossChainAccountPassword=""\
            ):
            LOG('verify')
            swap_tools.setSwapState(swapName, "verifyingFinalizedContractValues", setMap=True)
            finalization_list = json_tools.json_to_keyValList(DEC_finalizationPATH)
            json_tools.keyVal_list_update(finalization_list, responderJSONPath)
            boxID = json.loads(DEC_finalization)["boxId"]
            SigmaParticleInterface.SigmaParticle_box_to_addr(boxID, swapName)
            boxValue = SigmaParticleInterface.checkBoxValue(
                    boxID,
                    swapName + "/boxVal",
                    swapName,
                    role="responder",
                    ergopassword=crossChainAccountPassword,
                    otherchainpassword=localChainAccountPassword
            )
            j_response = json_tools.ojf(resp_J["responsePATH"])
            if boxValue == 0:
                print("boxValue = 0, swap aborting")
                LOG('boxValue = 0, swap aborting')
                while True:
                    if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(\
                            j_response, swapName, password=localChainAccountPassword\
                    ) <= 0:
                        AtomicityInterface.Atomicity_Refund(\
                                swapName, "responder", gas=SEPOLIA_EVM_GAS_CONTROL, \
                                gasMod=SEPOLIA_EVM_GASMOD_CONTROL, password=localChainAccountPassword
                                  )
                        break
                    time.sleep(3)
                return
            #other than just the box value responder should verify the scalars in the contract match those expected
            SigmaParticleInterface.SigmaParticle_newFrame(swapName)
            remoteLockTime = SigmaParticleInterface.SigmaParticle_CheckLockTimeAtomicSchnorr(\
                    swapName, boxID, password=crossChainAccountPassword\
            )
            if type(remoteLockTime) != int:
                print("error in remoteLockTime value: ", remoteLockTime)
                LOG(f'error in remoteLockTime value: {remoteLockTime}')
                return
            if remoteLockTime < MIN_CLAIM_LOCKTIME_ERGOTESTNET:
                while True:
                    if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(
                            j_response, swapName, password=localChainAccountPassword
                    ) <= 0:
                        AtomicityInterface.Atomicity_Refund(
                                swapName, "responder",  \
                                gas=SEPOLIA_EVM_GAS_CONTROL, gasMod=SEPOLIA_EVM_GASMOD_CONTROL, \
                                password=localChainAccountPassword
                        )
                        break
                    time.sleep(3)
                print("lock time is below safe minimum for claiming, refunding swap")
                LOG('lock time is below safe minimum for claiming, refunding swap')
                return
            minBoxValue = 1123841 #1123841
            if int(boxValue) < int(minBoxValue):
                while True:
                    if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(\
                            j_response, swapName, password=localChainAccountPassword\
                    ) <= 0:
                        AtomicityInterface.Atomicity_Refund(\
                                swapName, "responder",  \
                                gas=SEPOLIA_EVM_GAS_CONTROL, gasMod=SEPOLIA_EVM_GASMOD_CONTROL\
                        )
                        break
                    time.sleep(3)
                print("not enough nanoerg in contract, refunging swap")
                LOG('not enough nanoerg in contract, refunging swap')
                return
            SigmaParticleInterface.SigmaParticle_updateKeyEnv(swapName, responderErgoAccountName)
            SigmaParticleInterface.responderGenerateAtomicSchnorr(swapName, DEC_finalizationPATH, responderJSONPath, boxValue)
            expectedErgoTree = SigmaParticleInterface.SigmaParticle_getTreeFromBox(boxID, swapName, password=crossChainAccountPassword)
            if SigmaParticleInterface.responderVerifyErgoScript(swapName, expectedErgoTree, password=crossChainAccountPassword) == False:
                print("ergoScript verification returned false, wont fulfil swap")
                LOG('ergoScript verification returned false, wont fulfil swap')
                return False
            swap_tools.setSwapState(swapName, "verifiedFinalizedContractValues", setMap=True)

        def claim():
            LOG('claim')
            swap_tools.setSwapState(swapName, "claiming", setMap=True)
            SigmaParticleInterface.responderClaimAtomicSchnorr(swapName, 2500, password=crossChainAccountPassword)
            swap_tools.setSwapState(swapName, "claimed", setMap=True) #TODO ensure it was claimed w contract balance call

        if reloadSwapState != "":
            if reloadSwapState == swap_tools.PossibleSwapStates[7]: #responded_submitted
                swapName, ENC_finalizationPATH, ElGamalKey, \
                ElGamalKeyPath, DEC_finalizationPATH, \
                responderErgoAccountName, DEC_finalization = \
                            setup(resp_J)
                #    print("ergo contract verification status:", responderVerifyErgoScript(swapName, expectedErgoTree))
                verify(\
                        DEC_finalizationPATH, responderJSONPath, \
                        DEC_finalization, swapName, responderErgoAccountName, \
                        localChainAccountPassword=localChainAccountPassword, crossChainAccountPassword=crossChainAccountPassword\
                    )
                claim()
                return
            if reloadSwapState in [swap_tools.PossibleSwapStates[8], swap_tools.PossibleSwapStates[9]]: #finalized or verifying
                DEC_finalizationPATH = resp_J["DEC_finalizationPATH"]
                responderJSONPath = resp_J["responderJSONPath"]
                DEC_finalization = file_tools.clean_file_open(DEC_finalizationPATH, "r")
                swapName = resp_J["swapName"]
                responderErgoAccountName = resp_J["responderErgoAccountName"]
                verify(\
                    DEC_finalizationPATH, responderJSONPath, \
                    DEC_finalization, swapName, responderErgoAccountName, \
                    localChainAccountPassword=localChainAccountPassword, crossChainAccountPassword=crossChainAccountPassword\
                )
                claim()
                return
            if reloadSwapState in [swap_tools.PossibleSwapStates[10], swap_tools.PossibleSwapStates[11]]: #verified or claiming
                claim()
                return
        else:            
            swapName, ENC_finalizationPATH, ElGamalKey, \
            ElGamalKeyPath, DEC_finalizationPATH, \
            responderErgoAccountName, DEC_finalization = \
                setup(resp_J)
            #    print("ergo contract verification status:", responderVerifyErgoScript(swapName, expectedErgoTree))
            status = verify(\
                    DEC_finalizationPATH, responderJSONPath, \
                    DEC_finalization, swapName, responderErgoAccountName, \
                    localChainAccountPassword=localChainAccountPassword, crossChainAccountPassword=crossChainAccountPassword\
                )
            if status == False:
                return False
            claim()

def Responder_CheckLockTimeRefund(swapName, password=""):
    LOG('ergoScript verification returned false, wont fulfil swa')
    resp_J = json_tools.ojf(swapName + "/responder.json")
    j_response = json_tools.ojf(resp_J["responsePATH"])
    swapName = resp_J["swapName"]
    while True:
        if \
                AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName, password=password) <= 0 and \
                int(AtomicityInterface.Atomicity_CheckContractFunds(swapName, j_response, password=password)) != 0:
            swap_tools.setSwapState(swapName, "refunding", setMap=True)
            refund = AtomicityInterface.Atomicity_Refund(swapName, "responder", password=password)
            LOG(f'refund response: {refund}')
            swap_tools.setSwapState(swapName, "refunded", setMap=True) #TODO verify it was refunded w a contract balance call
            time.sleep(10)
            #we may want to alter the smart contract to enforce that funds are in the 
            #contract before sender reclaim can be called
            #will completely prevent fee waste on mainnet
            LOG('lock time expired, refund attempted')
            print("lock time expired, refund attempted")
        else:#TODO this part is weird needs to be clarified
            if int(AtomicityInterface.Atomicity_CheckContractFunds(swapName, j_response, password=password)) != 0:
                time.sleep(3)
                continue
            else:
                break
    print("contract empty / timelock expired")

