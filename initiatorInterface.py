import os
import json
from file_tools import *
py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "

def initiation(crossChainPubKey, initiatorChain): #returns an initiation JSON object #TODO link between selected chain and atomic ECC
    return os.popen(py + AtomicSwapECCPath + "p1Initiate " + crossChainPubKey + s_ + initiatorChain).read()

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

def inspectResponse(DEC_response_filepath, responderinfo_filepath):
    j_response = json.loads(clean_file_open(DEC_response_filepath, "r"))
    if "chain" not in j_response or "contractAddr" not in j_response:
        return print("Error: response does not have expected keys")
    else:
        fundedAmount = Atomicity_CheckContractFunds(j_response)




def Atomicity_CheckContractFunds(j_response):
    chain = j_response["chain"]
    contractAddr = j_response["contractAddr"]
    
