import sys
import json
import shutil
from ElGamalInterface import *
from AtomicityInterface import *
from SigmaParticleInterface import *
import json_tools
import time
from enum import Enum
from enum_tools import *
import file_tools


import os
from enum import Enum
from enum_tools import *
from price_tools import *
import configparser
import json
from file_tools import *
from AtomicityInterface import *
py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "

def valFromConf(confPath, val):
    confParser = configparser.ConfigParser()
    confParser.read(confPath)
    return confParser['default'][val]


def initiation(crossChainPubKey, initiatorChain, crossChain): #returns an initiation JSON object #TODO link between selected chain and atomic ECC
    return os.popen(py + AtomicSwapECCPath + "p1Initiate " + crossChainPubKey + s_ + initiatorChain + s_ + crossChain).read()

def sanitizeInitiation(initiationJSON): #this can be done at the SigmaParticle framework level easily instead of here
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
    return strip1

def inspectResponse(DEC_response_filepath):
    j_response = json.loads(clean_file_open(DEC_response_filepath, "r"))
    if "responderLocalChain" not in j_response or "responderContractAddr" not in j_response:
        print("Error: response does not have expected keys")
        return "Error: response does not have expected keys"
    else:
        fundedAmount = Atomicity_CheckContractFunds(j_response)
        if fundedAmount == "" or fundedAmount == None:
            fundedAmount = 0
#        print("contractAmount: ", fundedAmount, " wei")
        inspectScalarContractObject = {
                "counterpartyContractFundedAmount": fundedAmount
        }
        return json.dumps(inspectScalarContractObject)

def finalizeSwap(initiatorMasterJSONPath):
    j = json.loads(clean_file_open(initiatorMasterJSONPath, "r"))
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
    return finalizeJSON


def GeneralizedENC_InitiationSubroutine(swapName, LocalChainAccountName, CrossChainAccountName, ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain): #generalized function to create initiation commitments
#    print("InitiatorChain:", InitiatorChain)
#    print("ResponderChain:", ResponderChain)
#    print("swapName:", swapName)
    mi = {} #master input json
    if InitiatorChain.strip("\"") == "TestnetErgo" and ResponderChain.strip("\"") == "Sepolia":
        mi = {
            "ElGamalKey" : ElGamalKey.strip("\"").rstrip(),
            "ElGamalKeyPath" : ElGamalKeyPath.strip("\"").rstrip(),
            "swapName" : swapName.strip("\"").rstrip(),
            "InitiatorChain" : InitiatorChain.strip("\"").rstrip(),
            "ResponderChain" : ResponderChain.strip("\"").rstrip(),
            "initiatorJSONPath" : swapName.strip("\"").rstrip() + "/initiator.json", #initiators local swap session json state
            "initiatorEVMAddr" : \
            valFromConf("EVM/Atomicity/" + CrossChainAccountName + "/.env", 'SepoliaSenderAddr'),
            "InitiatorEIP3Secret".replace('"', '').rstrip() : \
            valFromConf("Ergo/SigmaParticle/" + LocalChainAccountName.strip("\"").rstrip()  + "/.env", 'senderEIP3Secret').replace('"', '').rstrip(),
                "InitiatorErgoAddr" : \
            valFromConf("Ergo/SigmaParticle/" + LocalChainAccountName.strip("\"").rstrip() + "/.env", 'senderPubKey').replace('"', '').rstrip(),
            "privateInitPATH" : swapName.strip("\"").rstrip() + "/priv_init.json",
            "publicInitPATH" : swapName.strip("\"").rstrip() + "/public_init.json",
            "ENC_Init_PATH" : swapName.strip("\"").rstrip()+ "/ENC_init.bin",
            "ENC_Response_PATH" : swapName.strip("\"").rstrip() + "/ENC_response_path.bin",
            "DEC_Response_PATH" : swapName.strip("\"").rstrip() + "/DEC_response.json",
            "finalizationPATH" : swapName.strip("\"").rstrip() + "/finalization.json",
            "ENC_finalizationPATH" : swapName.strip("\"").rstrip() + "/ENC_finalization.bin",
            "InitiatorEVMAccountName": CrossChainAccountName
        }
    print("swapName:", mi["swapName"]);
    clean_mkdir(mi["swapName"])
    clean_file_open(mi["initiatorJSONPath"], "w", "{}")
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
    json_tools.keyVal_list_update(keynum(initiatorInputEnum), mi["initiatorJSONPath"])
    privateInit = initiation(mi["initiatorEVMAddr"], InitiatorChain, ResponderChain)
    clean_file_open(mi["privateInitPATH"], "w", privateInit)
    initiation_keyValList = json_tools.json_to_keyValList(mi["privateInitPATH"])
    json_tools.keyVal_list_update(initiation_keyValList, mi["initiatorJSONPath"])
    publicInit = sanitizeInitiation(privateInit)
    clean_file_open(mi["publicInitPATH"], "w", publicInit)
    encrypt = ElGamal_Encrypt(mi["ElGamalKey"], mi["ElGamalKeyPath"], mi["publicInitPATH"], mi["ENC_Init_PATH"])
    return mi["ENC_Init_PATH"]



def GeneralizedENC_FinalizationSubroutine(initiatorJSONPath, CoinA_Price, CoinB_Price):
    init_J = json_tools.ojf(initiatorJSONPath)
    swapName = init_J["swapName"]
    ENC_Response_PATH = init_J["ENC_Response_PATH"]
    ElGamalKey = init_J["ElGamalKey"]
    ElGamalKeyPath = init_J["ElGamalKeyPath"]
    DEC_Response_PATH = init_J["DEC_Response_PATH"]
    finalizationPATH = init_J["finalizationPATH"]
    InitiatorEIP3Secret = init_J["InitiatorEIP3Secret"]
    ENC_finalizationPATH = init_J["ENC_finalizationPATH"]
    InitiatorErgoAddr = init_J["InitiatorErgoAddr"]
    decrypted_response = ElGamal_Decrypt(ENC_Response_PATH, ElGamalKey, ElGamalKeyPath)
    clean_file_open(DEC_Response_PATH, "w", decrypted_response)
    response_list = json_tools.json_to_keyValList(DEC_Response_PATH)
    json_tools.keyVal_list_update(response_list, initiatorJSONPath)
    init_J = json_tools.ojf(initiatorJSONPath)
    addr = init_J["responderContractAddr"]
    responderLocalChain = init_J["responderLocalChain"]
    xG = ast.literal_eval(init_J["xG"])
    Atomicity_newFrame(swapName, responderLocalChain)
    print("wait for contract upload and funding")
    time.sleep(30)
    inspect_json = inspectResponse(DEC_Response_PATH)
    if inspect_json == "Error: response does not have expected keys":
        print("fail")
        exit()
    clean_file_open(swapName + "/inspectContractTest.json", "w", inspect_json)
    inspect_list = json_tools.json_to_keyValList(swapName + "/inspectContractTest.json")
    json_tools.keyVal_list_update(inspect_list, initiatorJSONPath)
    minimum_wei = 0 #this is practically set for existential transfer calculations due to variable fee rates
    contractFunds = json.loads(clean_file_open(initiatorJSONPath, "r"))["counterpartyContractFundedAmount"]
    if int(contractFunds) < int(minimum_wei):
        print("not enough wei in contract, fail")
        exit()
#    print("checkcoords:", Atomicity_compareScalarContractCoords(swapName, addr, xG[0], xG[1]))
    if Atomicity_compareScalarContractCoords(swapName, addr, xG[0], xG[1]) == False:
        print("on chain contract does not meet offchain contract spec, do not fulfil this swap!")
        exit()
    convList = getPriceConversions(weiToEth(contractFunds), CoinA_Price, CoinB_Price)
    finalizeOBJ = finalizeSwap(initiatorJSONPath)
    clean_file_open(finalizationPATH, "w", finalizeOBJ)
    finalizeOBJ_LIST = json_tools.json_to_keyValList(finalizationPATH)
    json_tools.keyVal_list_update(finalizeOBJ_LIST, initiatorJSONPath)
    BuildAtomicSchnorrContract(initiatorJSONPath, 25, swapName, ErgToNanoErg(convList[1]))
    deployErgoContract(swapName) #TODO generalize based on chain
    boxId = getBoxID(swapName)
    InitiatorAtomicSchnorrLockHeight = clean_file_open("Ergo/SigmaParticle/" + swapName + "/lockHeight", "r")
    contractKeyValList = [{"boxId":boxId, "InitiatorAtomicSchnorrLockHeight":InitiatorAtomicSchnorrLockHeight, \
            "InitiatorErgoAddr":InitiatorErgoAddr}]
    json_tools.keyVal_list_update(contractKeyValList, initiatorJSONPath)
    json_tools.keyVal_list_update(contractKeyValList, finalizationPATH)
    ENC_finalization =  ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, finalizationPATH, ENC_finalizationPATH)
   
    #GeneralizedENC_InitiatorClaimSubroutine(init_J["initiatorJSONPath"])

def GeneralizedENC_InitiatorClaimSubroutine(initiatorJSONPath):
    ############## INITIATOR #######################################################
    init_J = json.loads(clean_file_open(initiatorJSONPath, "r"))
    swapName = init_J["swapName"]
    boxID = init_J["boxId"]
    initiatorEVMAccountName = init_J["InitiatorEVMAccountName"] 
    checkSchnorrTreeForClaim(boxID, swapName, initiatorJSONPath)
    deduceX_fromAtomicSchnorrClaim(initiatorJSONPath, swapName)
    Atomicity_updateKeyEnv(swapName, initiatorEVMAccountName)
    Atomicity_claimScalarContract(initiatorJSONPath, swapName, gasMod=3)
    ################################################################################

