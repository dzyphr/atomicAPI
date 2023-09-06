import json, os, json_tools
from datetime import datetime
from ElGamalInterface import *
from file_tools import *
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
    command = \
        py + AtomicSwapECCPath + "p2Respond " +\
        "'" + ksG  + "' " + "'" + str(datetime.now()) + "' " + \
        sr_filepath + s_ + x_filepath 
    response = os.popen(command).read()
    clean_file_open(response_filepath, "w", response)
    sr = clean_file_open(sr_filepath, "r")
    x = clean_file_open(x_filepath, "r")
    secretslist = [{"sr":sr}, {"x":x}]
    json_tools.keyVal_list_update(secretslist, responderMasterJSONPATH)


