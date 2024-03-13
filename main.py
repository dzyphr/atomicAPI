import sys
import ast
import json
import shutil
import configparser
import initiatorInterface
import responderInterface
import ElGamalInterface
import AtomicityInterface 
import SigmaParticleInterface 
import functional_tests
import json_tools
import time
import file_tools
from config_tools import firstRunCheck, updateMainEnv, initErgoAccountNonInteractive, initSepoliaAccountNonInteractive 
from bearerRESTAPIkeygen import generate_bearer_RESTAPI_key, add_RESTAPI_key_to_private_accepted_keys_JSON, starterAPIKeys, add_RESTAPI_key_to_public_accepted_keys_JSON
from passwordFileEncryption import proveEncEnvFilePasswordKnowledge
args = sys.argv

def logInToPasswordEncryptedAccount_ServerEndpoint(Chain, AccountName, Password, auth):
    import requests, uuid
    url = "http://localhost:3030/v0.0.1/requests/" #server private requests url
    ID = str(uuid.uuid4())
    headers = {"Authorization": "Bearer " + auth}
    requestobj = {
            "id": ID,
            "request_type": "logInToPasswordEncryptedAccount",
            "Chain": Chain,
            "AccountName": AccountName,
            "Password": Password
    }
    print(requests.post(url, headers=headers,  json = requestobj).text)

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
    resp = file_tools.clean_file_open(ENC_response_path, "r")
    requestobj = {
        "id": ID,
        "request_type":"submitEncryptedResponse",
        "SwapTicketID":SwapTicketID,
        "encryptedResponseBIN":  resp
    }
    respStr = requests.post(url, headers=headers, json = requestobj).text.replace("\"", "").replace("\\", "\n").replace("n", "")
    file_tools.clean_file_open(SwapTicketID + "/ENC_finalization.bin", "w", respStr)
    responderJSONPath = SwapTicketID + "/responder.json"
    responderInterface.GeneralizedENC_ResponderClaimSubroutine(responderJSONPath)

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
    file_tools.clean_mkdir(swapname) #swapname
    file_tools.clean_file_open(respObj["SwapTicketID"] + "/ENC_init.bin", "w", respObj["ENC_init.bin"])


def test2pAtomicSwap(p1Chain1, p1Chain2, p2Chain1, p2Chain2):
    FT_ErgoToSepolia(p1Chain1, p1Chain2, p2Chain1, p2Chain2) 

if len(args) == 2:
    if args[1] == "firstRunCheck":
        firstRunCheck()
        exit()
    if args[1] == "generateNewElGamalPubKey": #random q and g
        ElGamalInterface.generateNewElGamalPubKey()
        exit()
    if args[1] == "generate_bearer_RESTAPI_key":
        generate_bearer_RESTAPI_key()
    if args[1] == "generate_bearer_RESTAPI_key_add_to_private_accepted":
        add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if args[1] == "generate_bearer_RESTAPI_key_add_to_public_accepted":
        add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if args[1] == "generate_starter_RESTAPI_key":
        starterAPIKeys(add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key()))

elif len(args) == 3:
    if args[1] == "generate_bearer_RESTAPI_key":
        generate_bearer_RESTAPI_key(length=args[2])
    if args[1] == "generate_bearer_RESTAPI_key_add_to_private_accepted":
        add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key(length=args[2]))
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine":
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(args[2])
        exit()
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(args[2])
        exit()
    if args[1] == "Responder_CheckLockTimeRefund":
        responderInterface.Responder_CheckLockTimeRefund(args[2])
        exit()
    if args[1] == "SigmaParticle_box_to_addr":
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2]))
        exit()
    if args[1] == "generateNewElGamalPubKey": #specific q
        ElGamalInterface.generateNewElGamalPubKey(q=args[2])
elif len(args) == 4:
    if args[1] == "updateMainEnv":
        updateMainEnv(args[2], args[3])

    if args[1] == "init":
        accountName = args[2]
        chain = args[3]
        config_tools.initializeAccount(accountName, chain)
        exit()
    if args[1] == "generateNewElGamalPubKey": #specific q and g
        q = args[2]
        g = args[3]
        ElGamalInterface.generateNewElGamalPubKey(q=q, g=g)
        exit()
    if args[1] == "proveEncEnvFilePasswordKnowledge":
        proveEncEnvFilePasswordKnowledge(args[2], args[3])
elif len(args) == 5:
    if args[1] == "requestEncryptedInitiation_ClientEndpoint":
        requestEncryptedInitiation_ClientEndpoint(args[2], args[3], args[4])
        exit()
    if args[1] == "submitEncryptedResponse_ClientEndpoint":
        submitEncryptedResponse_ClientEndpoint(args[2], args[3], args[4])
        exit()
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(args[2], args[3], args[4])
        exit()
    if args[1] == "ElGamal_decrypt":
        sys.stdout.write(ElGamalInterface.ElGamal_Decrypt(args[2], args[3], args[4]))#subjectFilePath, senderPubKey, userKeyFileName
    if args[1] == "checkBoxValue":
        sys.stdout.write(SigmaParticleInterface.checkBoxValue(args[2], args[3], args[4]))#boxID, boxValPATH, swapName
        exit()
elif len(args) == 6:
    if args[1] == "logInToPasswordEncryptedAccount":
        print("logInToPasswordEncryptedAccount_ServerEndpoint")
        logInToPasswordEncryptedAccount_ServerEndpoint(args[2], args[3], args[4], args[5])
    if args[1] == "test2pAtomicSwap":
        test2pAtomicSwap(args[2], args[3], args[4], args[5])
        exit()
elif len(args) == 9:
    if args[1] == "GeneralizedENCInitiationSubroutine":    
        initiatorInterface.GeneralizedENC_InitiationSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8])
        exit()
elif len(args) == 10:
    if args[1] == "initSepoliaAccountNonInteractive":
        initSepoliaAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
        exit()
    if args[1] == "publishNewOrderType_ServerEndpoint":
        publishNewOrderType_ServerEndpoint(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
        exit()
    if args[1] == "initErgoAccountNonInteractive":
        initErgoAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7],  args[8], args[9])
        exit()
    if args[1] == "GeneralizeENC_ResponseSubroutine":
        print("response")
        responderInterface.GeneralizeENC_ResponseSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
        exit()

