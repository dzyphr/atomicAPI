import sys, configparser, json, shutil, json_tools, time, os, ast, ElGamalInterface, SigmaParticleInterface
import AtomicityInterface, enum_tools, price_tools, file_tools, config_tools
from enum import Enum
from swap_tools import setSwapState
from passwordFileEncryption import get_val_from_envdata_key, decrypt_file_return_contents
from LOG import LOG
py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "


MINIMUM_CLAIM_LOCKTIME_SEPOLIA = config_tools.valFromConf(".env", "MINIMUM_CLAIM_LOCKTIME_SEPOLIA") #TODO fine tuning
MINIMUM_REFUND_LOCKTIME_ERGO = config_tools.valFromConf(".env", "MINIMUM_REFUND_LOCKTIME_ERGO")

def initiation(crossChainPubKey, initiatorChain, crossChain): #returns an initiation JSON object #TODO link between selected chain and atomic ECC
    LOG('initiation')
    initiation = os.popen(py + AtomicSwapECCPath + "p1Initiate " + crossChainPubKey + s_ + initiatorChain + s_ + crossChain).read()
    LOG(f'initiation output: {initiation}') #TODO classify as sensitive data
    return initiation

def sanitizeInitiation(initiationJSON): #this can be done at the SigmaParticle framework level easily instead of here
    LOG('sanitizeInitiation')
    #TODO redo this with cleaner json framework
    j = json.loads(initiationJSON)
    ksG = j["ksG"]
    ks = j["ks"]
    rs = j["rs"] #Returns the same JSON with ks and rs (Private Variables) removed
    strip0 = initiationJSON.replace("\"ks\": " + str(ks) + ",", "")\
            .replace("\"rs\": " + str(rs) , "")\
            .replace("\"rs\": " + str(rs) + ",", "")\
            .replace("\"ks\": " + str(ks), "")
    #get rid of last comma and newlines
    strip1 = strip0.replace("\"ksG\": \"" + str(ksG) + "\",", "\"ksG\": \"" + str(ksG) + "\"")\
            .replace("}", "")\
            .rstrip()\
            .replace("\"ksG\": \"" + str(ksG) + "\"", "\"ksG\": \"" + str(ksG) + "\"\n}")\
            .rstrip()
    LOG(f'sanitizeInitiation ouput: {strip1}')
    return strip1

def inspectResponse(DEC_response_filepath, swapName, password=""):
    LOG('inspectResponse')
    j_response = json.loads(file_tools.clean_file_open(DEC_response_filepath, "r"))
    if "responderLocalChain" not in j_response or "responderContractAddr" not in j_response:
        print("Error: response does not have expected keys")
        return "Error: response does not have expected keys"
    else: 
        '''
        if password == "": #password doesnt have an effect when empty might not need logic to pass it into functions
            fundedAmount = AtomicityInterface.Atomicity_CheckContractFunds(swapName, j_response)
            remainingLockTime = AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName)
            if fundedAmount == "" or fundedAmount == None:
                fundedAmount = 0
    #        print("contractAmount: ", fundedAmount, " wei")
            inspectScalarContractObject = {
                    "counterpartyContractFundedAmount": fundedAmount,
                    "remainingLockTime": remainingLockTime
            }
            return json.dumps(inspectScalarContractObject)
        else:
        '''
        fundedAmount = AtomicityInterface.Atomicity_CheckContractFunds(swapName, j_response, password=password)
        remainingLockTime = \
                AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName, password=password)
        if fundedAmount == "" or fundedAmount == None:
            fundedAmount = 0
#        print("contractAmount: ", fundedAmount, " wei")
        inspectScalarContractObject = {
                "counterpartyContractFundedAmount": fundedAmount,
                "remainingLockTime": remainingLockTime
        }
        output =  json.dumps(inspectScalarContractObject)
        LOG(f'inspectResponse output: {output}')
        return output

def finalizeSwap(initiatorMasterJSONPath):
    LOG('finalizeSwap')
    j = json.loads(file_tools.clean_file_open(initiatorMasterJSONPath, "r"))
    sr_ = j["sr_"]
    xG = j["xG"]
    srG = j["srG"]
    e = j["e"]
    ks = j["ks"]
    rs = j["rs"]
    cmd  = py + AtomicSwapECCPath + "p1Finalize " + \
            "\"" + str(sr_) + "\"" + " \"" + xG.replace(" ", "") + "\" \"" + srG.replace(" ", "") + "\" \"" + str(e) + "\" " + \
            "\"" + str(ks) + "\"" + " \"" + str(rs) + "\""
    finalizeJSON = os.popen(cmd).read()
    LOG(f'finalizeSwap output: {finalizeJSON}')
    return finalizeJSON

#Generalized function to create initiation commitments
def GeneralizedENC_InitiationSubroutine(\
        swapName, LocalChainAccountName, CrossChainAccountName, \
        ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain,\
        localChainAccountPassword="", crossChainAccountPassword=""
):
    LOG('GeneralizedENC_InitiationSubroutine')
    def setup(swapName, LocalChainAccountName, CrossChainAccountName, \
        ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain,\
        localChainAccountPassword="", crossChainAccountPassword=""):
        LOG('setup')
        mi = {} #master input json
        localChainAccountEnvData = ""
        crossChainAccountEnvData = ""
        crossChainEncAccount = False
        localChainEncAccount = False
        InitiatorChain = InitiatorChain.strip("\"").rstrip()
        ResponderChain = ResponderChain.strip("\"").rstrip()
        ErgoPath = "Ergo/SigmaParticle/" + LocalChainAccountName + "/.env.encrypted"
        SepoliaPath = "EVM/Atomicity/" + CrossChainAccountName + "/.env.encrypted"
        if os.path.isfile(ErgoPath):
            if InitiatorChain == "TestnetErgo":
                if localChainAccountPassword != "":
                    localChainAccountEnvData = decrypt_file_return_contents(ErgoPath, localChainAccountPassword) 
                    localChainEncAccount = True
                else:
                    print("password required for encrypted env file!")
                    exit()
        if os.path.isfile(SepoliaPath):
            if ResponderChain == "Sepolia":
                if crossChainAccountPassword != "":
                    crossChainAccountEnvData = decrypt_file_return_contents(SepoliaPath, crossChainAccountPassword)
                    crossChainEncAccount = True
                else:
                    print("password required for encrypted env file!")
                    exit()
            #sepolia encrypted
        #if InitiatorChain.strip("\"") == "TestnetErgo" and ResponderChain.strip("\"") == "Sepolia":
        if localChainEncAccount == False and crossChainEncAccount == False:
                mi = {
                    "ElGamalKey" : ElGamalKey.strip("\"").rstrip(),
                    "ElGamalKeyPath" : ElGamalKeyPath.strip("\"").rstrip(),
                    "swapName" : swapName.strip("\"").rstrip(),
                    "InitiatorChain" : InitiatorChain.strip("\"").rstrip(),
                    "ResponderChain" : ResponderChain.strip("\"").rstrip(),
                    "initiatorJSONPath" : swapName.strip("\"").rstrip() + "/initiator.json", #initiators local swap session json state
                    "initiatorEVMAddr" : \
                        config_tools.valFromConf("EVM/Atomicity/" + CrossChainAccountName + "/.env", 'SepoliaSenderAddr'),
                    "InitiatorEIP3Secret".replace('"', '').rstrip() : \
                        config_tools.valFromConf("Ergo/SigmaParticle/" + \
                        LocalChainAccountName.strip("\"").rstrip()  + "/.env", 'senderEIP3Secret').replace('"', '').rstrip(),
                    "InitiatorErgoAddr" : \
                        config_tools.valFromConf("Ergo/SigmaParticle/" + \
                        LocalChainAccountName.strip("\"").rstrip() + "/.env", 'senderPubKey').replace('"', '').rstrip(),
                    "privateInitPATH" : swapName.strip("\"").rstrip() + "/priv_init.json",
                    "publicInitPATH" : swapName.strip("\"").rstrip() + "/public_init.json",
                    "ENC_Init_PATH" : swapName.strip("\"").rstrip()+ "/ENC_init.bin",
                    "ENC_Response_PATH" : swapName.strip("\"").rstrip() + "/ENC_response_path.bin",
                    "DEC_Response_PATH" : swapName.strip("\"").rstrip() + "/DEC_response.json",
                    "finalizationPATH" : swapName.strip("\"").rstrip() + "/finalization.json",
                    "ENC_finalizationPATH" : swapName.strip("\"").rstrip() + "/ENC_finalization.bin",
                    "InitiatorEVMAccountName": CrossChainAccountName,
                    "InitiatorErgoAccountName": LocalChainAccountName
                }
        elif localChainEncAccount == True and crossChainEncAccount == False:
            mi = {
                    "ElGamalKey" : ElGamalKey.strip("\"").rstrip(),
                    "ElGamalKeyPath" : ElGamalKeyPath.strip("\"").rstrip(),
                    "swapName" : swapName.strip("\"").rstrip(),
                    "InitiatorChain" : InitiatorChain.strip("\"").rstrip(),
                    "ResponderChain" : ResponderChain.strip("\"").rstrip(),
                    "initiatorJSONPath" : swapName.strip("\"").rstrip() + "/initiator.json", #initiators local swap session json state
                    "initiatorEVMAddr" : \
                    config_tools.valFromConf("EVM/Atomicity/" + CrossChainAccountName + "/.env", 'SepoliaSenderAddr'),
                    "InitiatorEIP3Secret".replace('"', '').rstrip() : \
                    get_val_from_envdata_key('senderEIP3Secret', localChainAccountEnvData).replace('"', '').rstrip(),
                        "InitiatorErgoAddr" : \
                    get_val_from_envdata_key('senderPubKey', localChainAccountEnvData).replace('"', '').rstrip(),
                    "privateInitPATH" : swapName.strip("\"").rstrip() + "/priv_init.json",
                    "publicInitPATH" : swapName.strip("\"").rstrip() + "/public_init.json",
                    "ENC_Init_PATH" : swapName.strip("\"").rstrip()+ "/ENC_init.bin",
                    "ENC_Response_PATH" : swapName.strip("\"").rstrip() + "/ENC_response_path.bin",
                    "DEC_Response_PATH" : swapName.strip("\"").rstrip() + "/DEC_response.json",
                    "finalizationPATH" : swapName.strip("\"").rstrip() + "/finalization.json",
                    "ENC_finalizationPATH" : swapName.strip("\"").rstrip() + "/ENC_finalization.bin",
                    "InitiatorEVMAccountName": CrossChainAccountName,
                    "InitiatorErgoAccountName": LocalChainAccountName
                }
        elif localChainEncAccount == False and crossChainEncAccount == True:
                mi = {
                    "ElGamalKey" : ElGamalKey.strip("\"").rstrip(),
                    "ElGamalKeyPath" : ElGamalKeyPath.strip("\"").rstrip(),
                    "swapName" : swapName.strip("\"").rstrip(),
                    "InitiatorChain" : InitiatorChain.strip("\"").rstrip(),
                    "ResponderChain" : ResponderChain.strip("\"").rstrip(),
                    "initiatorJSONPath" : swapName.strip("\"").rstrip() + "/initiator.json", #initiators local swap session json state
                    "initiatorEVMAddr" : \
                    get_val_from_envdata_key('SepoliaSenderAddr', crossChainAccountEnvData),
                    "InitiatorEIP3Secret".replace('"', '').rstrip() : \
                    config_tools.valFromConf("Ergo/SigmaParticle/" + \
                        LocalChainAccountName.strip("\"").rstrip()  + "/.env", 'senderEIP3Secret').replace('"', '').rstrip(),
                    "InitiatorErgoAddr" : \
                        config_tools.valFromConf("Ergo/SigmaParticle/" + \
                        LocalChainAccountName.strip("\"").rstrip() + "/.env", 'senderPubKey').replace('"', '').rstrip(),
                    "privateInitPATH" : swapName.strip("\"").rstrip() + "/priv_init.json",
                    "publicInitPATH" : swapName.strip("\"").rstrip() + "/public_init.json",
                    "ENC_Init_PATH" : swapName.strip("\"").rstrip()+ "/ENC_init.bin",
                    "ENC_Response_PATH" : swapName.strip("\"").rstrip() + "/ENC_response_path.bin",
                    "DEC_Response_PATH" : swapName.strip("\"").rstrip() + "/DEC_response.json",
                    "finalizationPATH" : swapName.strip("\"").rstrip() + "/finalization.json",
                    "ENC_finalizationPATH" : swapName.strip("\"").rstrip() + "/ENC_finalization.bin",
                    "InitiatorEVMAccountName": CrossChainAccountName,
                    "InitiatorErgoAccountName": LocalChainAccountName
                }
        elif localChainEncAccount == True and crossChainEncAccount == True:
                mi = {
                    "ElGamalKey" : ElGamalKey.strip("\"").rstrip(),
                    "ElGamalKeyPath" : ElGamalKeyPath.strip("\"").rstrip(),
                    "swapName" : swapName.strip("\"").rstrip(),
                    "InitiatorChain" : InitiatorChain.strip("\"").rstrip(),
                    "ResponderChain" : ResponderChain.strip("\"").rstrip(),
                    "initiatorJSONPath" : swapName.strip("\"").rstrip() + "/initiator.json", #initiators local swap session json state
                    "initiatorEVMAddr" : \
                    get_val_from_envdata_key('SepoliaSenderAddr', crossChainAccountEnvData),
                    "InitiatorEIP3Secret".replace('"', '').rstrip() : \
                    get_val_from_envdata_key('senderEIP3Secret', localChainAccountEnvData).replace('"', '').rstrip(),
                        "InitiatorErgoAddr" : \
                    get_val_from_envdata_key('senderPubKey', localChainAccountEnvData).replace('"', '').rstrip(),
                    "privateInitPATH" : swapName.strip("\"").rstrip() + "/priv_init.json",
                    "publicInitPATH" : swapName.strip("\"").rstrip() + "/public_init.json",
                    "ENC_Init_PATH" : swapName.strip("\"").rstrip()+ "/ENC_init.bin",
                    "ENC_Response_PATH" : swapName.strip("\"").rstrip() + "/ENC_response_path.bin",
                    "DEC_Response_PATH" : swapName.strip("\"").rstrip() + "/DEC_response.json",
                    "finalizationPATH" : swapName.strip("\"").rstrip() + "/finalization.json",
                    "ENC_finalizationPATH" : swapName.strip("\"").rstrip() + "/ENC_finalization.bin",
                    "InitiatorEVMAccountName": CrossChainAccountName,
                    "InitiatorErgoAccountName": LocalChainAccountName
                }
        print("swapName:", mi["swapName"]);
        file_tools.clean_mkdir(mi["swapName"])
        return mi

    mi = setup(swapName, LocalChainAccountName, CrossChainAccountName, \
        ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain,\
        localChainAccountPassword=localChainAccountPassword, crossChainAccountPassword=crossChainAccountPassword)
    def init(mi):
        LOG('init')
#        setSwapState(swapName, "initiating", setMap=True) #should be set by REST API 
        file_tools.clean_file_open(mi["initiatorJSONPath"], "w", "{}")
        class initiatorInputEnum(Enum):
            ElGamalKey = mi["ElGamalKey"]
            ElGamalKeyPath = mi["ElGamalKeyPath"]
            swapName = mi["swapName"]
            InitiatorChain = mi["InitiatorChain"]
            ResponderChain = mi["ResponderChain"]
            initiatorJSONPath = mi["initiatorJSONPath"] #initiators local swap session json state
            InitiatorEVMAddr = mi["initiatorEVMAddr"]
            InitiatorEIP3Secret = mi["InitiatorEIP3Secret"]
            InitiatorErgoAddr = mi["InitiatorErgoAddr"]
            privateInitPATH = mi["privateInitPATH"]
            publicInitPATH = mi["publicInitPATH"]
            ENC_Init_PATH = mi["ENC_Init_PATH"]
            ENC_Response_PATH = mi["ENC_Response_PATH"]
            DEC_Response_PATH = mi["DEC_Response_PATH"]
            finalizationPATH = mi["finalizationPATH"]
            ENC_finalizationPATH = mi["ENC_finalizationPATH"]
            InitiatorEVMAccountName = mi["InitiatorEVMAccountName"]
            InitiatorErgoAccountName = mi["InitiatorErgoAccountName"]
        iean = [{"InitiatorErgoAccountName": LocalChainAccountName}, {"InitiatorEVMAccountName": CrossChainAccountName}]
        json_tools.keyVal_list_update(iean, mi["initiatorJSONPath"])
        json_tools.keyVal_list_update(enum_tools.keynum(initiatorInputEnum), mi["initiatorJSONPath"])
        privateInit = initiation(mi["initiatorEVMAddr"], InitiatorChain, ResponderChain)
        file_tools.clean_file_open(mi["privateInitPATH"], "w", privateInit)
        initiation_keyValList = json_tools.json_to_keyValList(mi["privateInitPATH"])
        json_tools.keyVal_list_update(initiation_keyValList, mi["initiatorJSONPath"])
        publicInit = sanitizeInitiation(privateInit)
        file_tools.clean_file_open(mi["publicInitPATH"], "w", publicInit)
        encrypt = ElGamalInterface.ElGamal_Encrypt(mi["ElGamalKey"], mi["ElGamalKeyPath"], mi["publicInitPATH"], mi["ENC_Init_PATH"])
        setSwapState(swapName, "initiated_unsubmitted", setMap=True)
    init(mi)
    return mi["ENC_Init_PATH"]



def GeneralizedENC_FinalizationSubroutine( \
        initiatorJSONPath, CoinA_Price, CoinB_Price, localchainpassword="", crosschainpassword="", swapStateReload="" \
):
    LOG('GeneralizedENC_FinalizationSubroutine')
    init_J = json_tools.ojf(initiatorJSONPath)
    if init_J["InitiatorChain"] == "TestnetErgo" and init_J["ResponderChain"] == "Sepolia":
        if swapStateReload == [4]:#verifying_response
            addr = init_J["responderContractAddr"]
            DEC_Response_PATH = init_J["DEC_Response_PATH"]
            xG = ast.literal_eval(init_J["xG"])
            contractFunds = verifyResponse(swapName, DEC_Response_PATH, crosschainpassword, initiatorJSONPath, addr, xG)
            finalizationPATH = init_J["finalizationPATH"]
            InitiatorErgoAddr = init_J["InitiatorErgoAddr"]
            ElGamalKey = init_J["ElGamalKey"]
            ElGamalKeyPath = init_J["ElGamalKeyPath"]
            ENC_finalizationPATH = init_J["ENC_finalizationPATH"]
            finalize(
                    swapName, contractFunds, 
                    CoinA_Price, CoinB_Price, 
                    initiatorJSONPath, finalizationPATH, 
                    InitiatorErgoAddr, ElGamalKey, ElGamalKeyPath, ENC_finalizationPATH
            )
            return
        if swapStateReload == [5]:#verified_response
            contractFunds = json.loads(file_tools.clean_file_open(initiatorJSONPath, "r"))["counterpartyContractFundedAmount"]
            finalizationPATH = init_J["finalizationPATH"]
            InitiatorErgoAddr = init_J["InitiatorErgoAddr"]
            ElGamalKey = init_J["ElGamalKey"]
            ElGamalKeyPath = init_J["ElGamalKeyPath"]
            ENC_finalizationPATH = init_J["ENC_finalizationPATH"]
            finalize(
                    swapName, contractFunds,
                    CoinA_Price, CoinB_Price,
                    initiatorJSONPath, finalizationPATH,
                    InitiatorErgoAddr, ElGamalKey, ElGamalKeyPath, ENC_finalizationPATH
            )
            return
        if swapStateReload == [6]:#finalizing
            #may want to check if we already uploaded something to mempool here TODO
            contractFunds = json.loads(file_tools.clean_file_open(initiatorJSONPath, "r"))["counterpartyContractFundedAmount"]
            finalizationPATH = init_J["finalizationPATH"]
            InitiatorErgoAddr = init_J["InitiatorErgoAddr"]
            ElGamalKey = init_J["ElGamalKey"]
            ElGamalKeyPath = init_J["ElGamalKeyPath"]
            ENC_finalizationPATH = init_J["ENC_finalizationPATH"]
            finalize(
                    swapName, contractFunds,
                    CoinA_Price, CoinB_Price,
                    initiatorJSONPath, finalizationPATH,
                    InitiatorErgoAddr, ElGamalKey, ElGamalKeyPath, ENC_finalizationPATH
            )
            return

        def init(init_J, initiatorJSONPath, CoinA_Price, CoinB_Price, localchainpassword="", crosschainpassword=""):
            LOG('init')
            swapName = init_J["swapName"]
            setSwapState(swapName, "responded", setMap=True)
            ENC_Response_PATH = init_J["ENC_Response_PATH"]
            ElGamalKey = init_J["ElGamalKey"]
            ElGamalKeyPath = init_J["ElGamalKeyPath"]
            DEC_Response_PATH = init_J["DEC_Response_PATH"]
            finalizationPATH = init_J["finalizationPATH"]
            InitiatorEIP3Secret = init_J["InitiatorEIP3Secret"]
            ENC_finalizationPATH = init_J["ENC_finalizationPATH"]
            InitiatorErgoAddr = init_J["InitiatorErgoAddr"]
            initiatorEVMAccountName = init_J["InitiatorEVMAccountName"]
            decrypted_response = ElGamalInterface.ElGamal_Decrypt(ENC_Response_PATH, ElGamalKey, ElGamalKeyPath)
            file_tools.clean_file_open(DEC_Response_PATH, "w", decrypted_response)
            response_list = json_tools.json_to_keyValList(DEC_Response_PATH)
            json_tools.keyVal_list_update(response_list, initiatorJSONPath)
            init_J = json_tools.ojf(initiatorJSONPath)
            addr = init_J["responderContractAddr"]
            responderLocalChain = init_J["responderLocalChain"]
            xG = ast.literal_eval(init_J["xG"])
                    #TODO check for existing swapfile
            #if yes check for finalization / funded contract
            AtomicityInterface.Atomicity_newFrame(swapName, responderLocalChain)
            AtomicityInterface.Atomicity_updateKeyEnv(swapName, initiatorEVMAccountName)
            waittime = 30
            LOG(f'waiting {waittime} seconds for contract upload and funding')
            print("wait for contract upload and funding")
            time.sleep(waittime) #TODO make this better to avoid non uploaded or non funded related errors
            return swapName, ENC_Response_PATH, ElGamalKey, ElGamalKeyPath, DEC_Response_PATH, finalizationPATH, InitiatorEIP3Secret, ENC_finalizationPATH, InitiatorErgoAddr, addr, responderLocalChain, xG

        swapName, ENC_Response_PATH, ElGamalKey, ElGamalKeyPath, DEC_Response_PATH, finalizationPATH, InitiatorEIP3Secret, ENC_finalizationPATH, InitiatorErgoAddr, addr, responderLocalChain, xG = init(init_J, initiatorJSONPath, CoinA_Price, CoinB_Price, localchainpassword, crosschainpassword)

        def verifyResponse(swapName, DEC_Response_PATH, crosschainpassword, initiatorJSONPath, addr, xG):
            LOG('verifyResponse')
            setSwapState(swapName, "verifying_response", setMap=True)
            inspect_json = inspectResponse(DEC_Response_PATH, swapName, password=crosschainpassword)
            if inspect_json == "Error: response does not have expected keys":
                print("fail")
                LOG("Error: response does not have expected keys")
                exit()
            file_tools.clean_file_open(swapName + "/inspectContractTest.json", "w", inspect_json)
            inspect_list = json_tools.json_to_keyValList(swapName + "/inspectContractTest.json")
            json_tools.keyVal_list_update(inspect_list, initiatorJSONPath)
            minimum_wei = 0 #this is practically set for existential transfer calculations due to variable fee rates
            contractFunds = json.loads(file_tools.clean_file_open(initiatorJSONPath, "r"))["counterpartyContractFundedAmount"]
            remainingLockTime = json.loads(file_tools.clean_file_open(initiatorJSONPath, "r"))["remainingLockTime"]
            if int(remainingLockTime) < int(MINIMUM_CLAIM_LOCKTIME_SEPOLIA):
                print("remaining locktime is lower than", MINIMUM_CLAIM_LOCKTIME_SEPOLIA, "swap is at risk of double spending")
                LOG(f'remaining locktime is lower than {MINIMUM_CLAIM_LOCKTIME_SEPOLIA}, swap is at risk of double spending')
                exit()
            if int(contractFunds) < int(minimum_wei):
                print("not enough wei in contract, fail")
                LOG('Failure! Contract funds are lower than minimum wei!')
                exit()
            if AtomicityInterface.Atomicity_compareScalarContractCoords( \
                    swapName, addr, xG[0], xG[1], password=crosschainpassword \
            ) == False:
                LOG("on chain contract does not meet offchain contract spec, will not fulfil this swap!")
                print("on chain contract does not meet offchain contract spec, will not fulfil this swap!")
                exit()
            setSwapState(swapName, "verified_response", setMap=True)
            return contractFunds

        contractFunds = verifyResponse(swapName, DEC_Response_PATH, crosschainpassword, initiatorJSONPath, addr, xG)
        
        def finalize( \
                swapName, contractFunds, CoinA_Price, CoinB_Price, initiatorJSONPath, finalizationPATH, \
                InitiatorErgoAddr, ElGamalKey, ElGamalKeyPath, ENC_finalizationPATH \
        ):
            LOG('finalize')
            convList = price_tools.getPriceConversions(price_tools.weiToEth(contractFunds), CoinA_Price, CoinB_Price)
            setSwapState(swapName, "finalizing", setMap=True)
            #TODO if we re enter this section due to a state reload, we should check if we already sent something to the mempool
            #or potentially it uploaded already if we hit the deploy function before state break
            finalizeOBJ = finalizeSwap(initiatorJSONPath)
            file_tools.clean_file_open(finalizationPATH, "w", finalizeOBJ)
            finalizeOBJ_LIST = json_tools.json_to_keyValList(finalizationPATH)
            json_tools.keyVal_list_update(finalizeOBJ_LIST, initiatorJSONPath)
            #TODO impl passwords in sigmaparticleinterface fns
            SigmaParticleInterface.BuildAtomicSchnorrContract(
                    initiatorJSONPath, MINIMUM_REFUND_LOCKTIME_ERGO, swapName, \
                    price_tools.ErgToNanoErg(convList[1]) \
            )
            init_J = json_tools.ojf(initiatorJSONPath)
            InitiatorErgoAccountName = init_J["InitiatorErgoAccountName"]
            SigmaParticleInterface.SigmaParticle_updateKeyEnv(swapName, InitiatorErgoAccountName)
            SigmaParticleInterface.deployErgoContract(swapName, password=localchainpassword) #TODO generalize based on chain
            boxId = SigmaParticleInterface.getBoxID(swapName)
            InitiatorAtomicSchnorrLockHeight = file_tools.clean_file_open("Ergo/SigmaParticle/" + swapName + "/lockHeight", "r")
            contractKeyValList = [{"boxId":boxId, "InitiatorAtomicSchnorrLockHeight":InitiatorAtomicSchnorrLockHeight, \
                    "InitiatorErgoAddr":InitiatorErgoAddr}]
            json_tools.keyVal_list_update(contractKeyValList, initiatorJSONPath)
            json_tools.keyVal_list_update(contractKeyValList, finalizationPATH)
            ENC_finalization =  ElGamalInterface.ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, finalizationPATH, ENC_finalizationPATH)
            setSwapState(swapName, "finalized_unsubmitted", setMap=True)
        
        finalize(swapName, contractFunds, CoinA_Price, CoinB_Price, initiatorJSONPath, finalizationPATH, InitiatorErgoAddr, ElGamalKey, ElGamalKeyPath, ENC_finalizationPATH)
    #GeneralizedENC_InitiatorClaimSubroutine(init_J["initiatorJSONPath"])

def GeneralizedENC_InitiatorClaimSubroutine(initiatorJSONPath, localchainpassword="", crosschainpassword=""):
    ############## INITIATOR #######################################################
    LOG('GeneralizedENC_InitiatorClaimSubroutine')
    init_J = json.loads(file_tools.clean_file_open(initiatorJSONPath, "r"))
    if init_J["InitiatorChain"] == "TestnetErgo" and init_J["ResponderChain"] == "Sepolia":
        swapName = init_J["swapName"]
        setSwapState(swapName, "claiming", setMap=True)
        boxID = init_J["boxId"]
        initiatorEVMAccountName = init_J["InitiatorEVMAccountName"] 
        if SigmaParticleInterface.checkSchnorrTreeForClaim(boxID, swapName, initiatorJSONPath, password=localchainpassword) == False:
            LOG('refund attempted due to timelock expiry')
            print("refund attempted due to timelock expiry")
            exit()
        SigmaParticleInterface.deduceX_fromAtomicSchnorrClaim(initiatorJSONPath, swapName)
#        AtomicityInterface.Atomicity_updateKeyEnv(swapName, initiatorEVMAccountName)
        AtomicityInterface.Atomicity_claimScalarContract(initiatorJSONPath, swapName, gasMod=3, password=crosschainpassword)
        LOG('Swap Claimed')
        setSwapState(swapName, "claimed", setMap=True)
    ################################################################################

