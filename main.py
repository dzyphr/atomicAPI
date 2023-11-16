import sys
import ast
import json
import shutil
import configparser
from configparser import *
from initiatorInterface import *
from responderInterface import *
import responderInterface
from ElGamalInterface import *
from AtomicityInterface import * 
from SigmaParticleInterface import *
from functional_tests import *
import json_tools
import time
import file_tools
from config_tools import firstRunCheck
args = sys.argv

def publishNewOrderType_ServerEndpoint(url, CoinA, CoinB, CoinA_price, CoinB_price, MaxVolCoinA, MinVolCoinA, auth):
    import requests, uuid
    ID = str(uuid.uuid4())
    headers = {"Authorization": "Bearer " + auth}
    requestobj = {
        "id": ID,
        "request_type": "publishNewOrderType",
        "OrderTypeUUID": ID,
        "CoinA": CoinA,
        "CoinB": CoinB,
        "CoinA_price": CoinA_price,
        "CoinB_price": CoinB_price,
        "MaxVolCoinA": MaxVolCoinA,
        "MinVolCoinA": MinVolCoinA
    }
    print(requests.post(url, headers=headers,  json = requestobj).text)

def submitEncryptedResponse_ClientEndpoint(url, SwapTicketID, ENC_response_path):
    import requests, uuid
    ID = str(uuid.uuid4())
    headers = {"Authorization": "None"}
    resp = clean_file_open(ENC_response_path, "r")
    requestobj = {
        "id": ID,
        "request_type":"submitEncryptedResponse",
        "SwapTicketID":SwapTicketID,
        "encryptedResponseBIN":  resp
    }
    respStr = requests.post(url, headers=headers, json = requestobj).text.replace("\"", "").replace("\\", "\n").replace("n", "")
    clean_file_open(SwapTicketID + "/ENC_finalization.bin", "w", respStr)
    responderJSONPath = SwapTicketID + "/responder.json"
    GeneralizedENC_ResponderClaimSubroutine(responderJSONPath)

def requestEncryptedInitiation_ClientEndpoint(url, OrderTypeUUID, ElGamalPubkey):
    import requests, uuid
    ID = str(uuid.uuid4())
    headers = {"Authorization": "None"}
    requestobj = {
        "id": ID,
        "request_type":"requestEncryptedInitiation",
        "OrderTypeUUID":OrderTypeUUID,
        "ElGamalKey":ElGamalPubkey,
    }
    respStr = requests.post(url, headers=headers, json = requestobj).text
    respObj = json.loads(respStr[1:-1].encode().decode('unicode_escape'))
    swapname = respObj["SwapTicketID"]
    clean_mkdir(swapname) #swapname
    clean_file_open(respObj["SwapTicketID"] + "/ENC_init.bin", "w", respObj["ENC_init.bin"])


def test2pAtomicSwap(p1Chain1, p1Chain2, p2Chain1, p2Chain2):
    FT_ErgoToSepolia(p1Chain1, p1Chain2, p2Chain1, p2Chain2) 

if len(args) == 2:
    if args[1] == "firstRunCheck":
        firstRunCheck()
        exit()
    if args[1] == "generateNewElGamalPubKey":
        ElGamalInterface.generateNewElGamalPubKey()
        exit()
elif len(args) == 3:
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine":
        GeneralizedENC_ResponderClaimSubroutine(args[2])
        exit()
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        GeneralizedENC_InitiatorClaimSubroutine(args[2])
        exit()
    if args[1] == "Responder_CheckLockTimeRefund":
        responderInterface.Responder_CheckLockTimeRefund(args[2])
        exit()
elif len(args) == 4:
    if args[1] == "init":
        accountName = args[2]
        chain = args[3]
        initializeAccount(accountName, chain)
        exit()
    if args[1] == "generateNewElGamalPubKey":
        q = args[2]
        g = args[3]
        ElGamalInterface.generateNewElGamalPubKey(q=q, g=g)
        exit()
elif len(args) == 5:
    if args[1] == "requestEncryptedInitiation_ClientEndpoint":
        requestEncryptedInitiation_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "submitEncryptedResponse_ClientEndpoint":
        submitEncryptedResponse_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        GeneralizedENC_FinalizationSubroutine(args[2], args[3], args[4])
    exit()
elif len(args) == 6:
    if args[1] == "test2pAtomicSwap":
        test2pAtomicSwap(args[2], args[3], args[4], args[5])
    exit()
elif len(args) == 9:
    if args[1] == "GeneralizedENCInitiationSubroutine":    
        GeneralizedENC_InitiationSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8])
    exit()
elif len(args) == 10:
    if args[1] == "publishNewOrderType_ServerEndpoint":
        publishNewOrderType_ServerEndpoint(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "GeneralizeENC_ResponseSubroutine":
        print("response")
        GeneralizeENC_ResponseSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    exit()

