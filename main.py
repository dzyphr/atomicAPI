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
from ServerEndpoints import logInToPasswordEncryptedAccount_ServerEndpoint, publishNewOrderType_ServerEndpoint
from ClientEndpoints import submitEncryptedResponse_ClientEndpoint, requestEncryptedInitiation_ClientEndpoint, logInToPasswordEncryptedAccount_ClientEndpoint
from config_tools import firstRunCheck, updateMainEnv, initErgoAccountNonInteractive, initSepoliaAccountNonInteractive 
from bearerRESTAPIkeygen import generate_bearer_RESTAPI_key, add_RESTAPI_key_to_private_accepted_keys_JSON, starterAPIKeys, add_RESTAPI_key_to_public_accepted_keys_JSON
from passwordFileEncryption import proveEncEnvFilePasswordKnowledge
args = sys.argv

def test2pAtomicSwap(p1Chain1, p1Chain2, p2Chain1, p2Chain2):
    FT_ErgoToSepolia(p1Chain1, p1Chain2, p2Chain1, p2Chain2) 


#print("argslen: ", len(args))

if len(args) == 2:
    if args[1] == "firstRunCheck":
        firstRunCheck()
    if args[1] == "generateNewElGamalPubKey": #random q and g
        ElGamalInterface.generateNewElGamalPubKey()
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
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(args[2])
    if args[1] == "Responder_CheckLockTimeRefund":
        responderInterface.Responder_CheckLockTimeRefund(args[2])
    if args[1] == "SigmaParticle_box_to_addr":
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2]))
    if args[1] == "generateNewElGamalPubKey": #specific q
        ElGamalInterface.generateNewElGamalPubKey(q=args[2])
elif len(args) == 4:
    if args[1] == "SigmaParticle_box_to_addr":
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2], args[3]))
    if args[1] == "Responder_CheckLockTimeRefund":
        responderInterface.Responder_CheckLockTimeRefund(args[2], password=args[3])
    if args[1] == "updateMainEnv":
        updateMainEnv(args[2], args[3])
    if args[1] == "init":
        accountName = args[2]
        chain = args[3]
        config_tools.initializeAccount(accountName, chain)
    if args[1] == "generateNewElGamalPubKey": #specific q and g
        q = args[2]
        g = args[3]
        ElGamalInterface.generateNewElGamalPubKey(q=q, g=g)
    if args[1] == "proveEncEnvFilePasswordKnowledge":
        proveEncEnvFilePasswordKnowledge(args[2], args[3])
elif len(args) == 5:
    if args[1] == "SigmaParticle_box_to_addr":
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2], args[3], password=args[4]))
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(args[2], localchainpassword=args[3], crosschainpassword=args[4])
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine":
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(\
                args[2], \
                localChainAccountPassword=args[3], \
                crossChainAccountPassword=args[4]\
        )

    if args[1] == "requestEncryptedInitiation_ClientEndpoint":
        requestEncryptedInitiation_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "submitEncryptedResponse_ClientEndpoint":
        submitEncryptedResponse_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(args[2], args[3], args[4])
    if args[1] == "ElGamal_decrypt":
        sys.stdout.write(ElGamalInterface.ElGamal_Decrypt(args[2], args[3], args[4]))#subjectFilePath, senderPubKey, userKeyFileName
    if args[1] == "checkBoxValue":
        sys.stdout.write(SigmaParticleInterface.checkBoxValue(args[2], args[3], args[4]))#boxID, boxValPATH, swapName
elif len(args) == 6:
    if args[1] == "logInToPasswordEncryptedAccount_Server":
        logInToPasswordEncryptedAccount_ServerEndpoint(args[2], args[3], args[4], args[5])
    if args[1] == "logInToPasswordEncryptedAccount_Client":
        logInToPasswordEncryptedAccount_ClientEndpoint(args[2], args[3], args[4], args[5])
    if args[1] == "test2pAtomicSwap":
        test2pAtomicSwap(args[2], args[3], args[4], args[5])
elif len(args) == 7:
    if args[1] == "checkBoxValue":
        sys.stdout.write(SigmaParticleInterface.checkBoxValue(\
                args[2], args[3], args[4], ergopassword=args[5], \
                otherchainpassword=args[6]\
        ))#boxID, boxValPATH, swapName, password
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(args[2], args[3], args[4], args[5], args[6])
elif len(args) == 9:
    if args[1] == "GeneralizedENCInitiationSubroutine":    
        initiatorInterface.GeneralizedENC_InitiationSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8])
elif len(args) == 10:
    if args[1] == "initSepoliaAccountNonInteractive":
        initSepoliaAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "publishNewOrderType_ServerEndpoint":
        publishNewOrderType_ServerEndpoint(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "initErgoAccountNonInteractive":
        initErgoAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7],  args[8], args[9])
    if args[1] == "GeneralizeENC_ResponseSubroutine":
        responderInterface.GeneralizeENC_ResponseSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
elif len(args) == 11:
    if args[1] == "GeneralizedENCInitiationSubroutine":
        initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                args[2], args[3], args[4], args[5], \
                args[6], args[7], args[8], localChainAccountPassword=args[9], crossChainAccountPassword=args[10])
    if args[1] == "initSepoliaAccountNonInteractive_ENC": #TODO get rid of ID scan and compiler version args
        initSepoliaAccountNonInteractive(
            args[2], args[3], args[4], args[5], args[6], args[7],
            args[8], args[9], enc=True, password=args[10]
        )
    if args[1] == "initErgoAccountNonInteractive_ENC":
        initErgoAccountNonInteractive(
            args[2], args[3], args[4], args[5], args[6], args[7], \
            args[8], args[9], enc=True, password=args[10]
        )
elif len(args) == 12:
    if args[1] == "GeneralizeENC_ResponseSubroutine":
        responderInterface.GeneralizeENC_ResponseSubroutine(
                args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9],
                localChainAccountPassword=args[10], crossChainAccountPassword=args[11]
        )
