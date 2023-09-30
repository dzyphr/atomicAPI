import os
import json
from file_tools import *
from AtomicityInterface import *
py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "

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


def generalizedENCInitiationSubroutine(swapName, AccountName, ElGamalKey, ElGamalKeyPath, InitiatorChain, ResponderChain): #generalized function to create initiation commitments
    mi = {} #master input json
    if InitiatorChain == "Ergo" && ResponderChain == "Sepolia"
        mi = {
            "ElGamalKey" : ElGamalKey,
            "ElGamalKeyPath" : ElGamalKeyPath,
            "swapName" : swapName,
            "InitiatorChain" : InitiatorChain,
            "ResponderChain" : ResponderChain,
            "initiatorJSONPath" : swapName + "/initiator.json", #initiators local swap session json state
            "InitiatorEVMAddr" : \
            valFromConf("EVM/Atomicity/" + AccountName + "/.env", 'SepoliaSenderAddr').replace('"', ''),
            "InitiatorEIP3Secret" : \
            valFromConf("Ergo/SigmaParticle/" + AccountName  + "/.env", 'senderEIP3Secret').replace('"', ''),
                "InitiatorErgoAddr" : \
            valFromConf("Ergo/SigmaParticle/" + AccountName + "/.env", 'senderPubKey').replace('"', ''),
            "privateInitPATH" : swapName + "/priv_init.json",
            "publicInitPATH" : swapName + "/public_init.json",
            "ENC_Init_PATH" : swapName + "/ENC_init.bin",
            "ENC_Response_PATH" : swapName + "/ENC_response_path.bin",
            "DEC_Response_PATH" : swapName + "/DEC_response.json",
            "finalizationPATH" : swapName + "/finalization.json",
            "ENC_finalizationPATH" : swapName + "/ENC_finalization.bin",
        }
    clean_mkdir(mi["swapName"])
    clean_file_open(mi["initiatorJSONPath"], "w", "{}")
    class initiatorInputEnum(Enum):
        ElGamalKey = mi["ElGamalKey"]
        ElGamalKeyPath = mi["ElGamalKeyPath"]
        swapName = mi["swapName"]
        InitiatorChain = mi["InitiatorChain"]
        ResponderChain = mi["ResponderChain"]
        initiatorJSONPath = mi["initiatorJSONPath"] #initiators local swap session json state
        InitiatorEVMAddr = mi["InitiatorEVMAddr"]
        InitiatorEIP3Secret = mi["InitiatorEIP3Secret"]
        InitiatorErgoAddr = mi["InitiatorErgoAddr"]
        privateInitPATH = mi["privateInitPATH"]
        publicInitPATH = mi["publicInitPATH"]
        ENC_Init_PATH = mi["ENC_Init_PATH"]
        ENC_Response_PATH = mi["ENC_Response_PATH"]
        DEC_Response_PATH = mi["DEC_Response_PATH"]
        finalizationPATH = mi["finalizationPATH"]
        ENC_finalizationPATH = mi["ENC_finalizationPATH"]
    json_tools.keyVal_list_update(keynum(initiatorInputEnum), mi["initiatorJSONPath"])
    privateInit = initiation(mi["InitiatorEVMAddr"], InitiatorChain, ResponderChain)
    clean_file_open(mi["privateInitPATH"], "w", privateInit)
    initiation_keyValList = json_tools.json_to_keyValList(mi["privateInitPATH"])
    json_tools.keyVal_list_update(initiation_keyValList, mi["initiatorJSONPath"])
    publicInit = sanitizeInitiation(privateInit)
    clean_file_open(publicInitPATH, "w", publicInit)
    encrypt = ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, mi["publicInitPATH"], mi["ENC_Init_PATH"])
    return mi["ENC_Init_PATH"]



