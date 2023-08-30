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
        print("contractAmount: ", fundedAmount, " wei")
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



     
