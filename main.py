import sys
import json
import shutil
from initiatorInterface import *
from responderInterface import *
from ElGamalInterface import *
from AtomicityInterface import * 
import json_tools
import time
args = sys.argv


def test():
    def clearPaths():
        if os.path.isdir("EVM/Atomicity/testswapname"):
            shutil.rmtree("EVM/Atomicity/testswapname")
    clearPaths()
    testkey = "688344026718772736449750175203366052782498205293898002465375827258042277361951460658218874759221293994168145022574766874751338527256700500579101512082414055194093613376114567923022297129476978722630282962906957224675125386874494158492157124310481876254258350563100432848938338097941551681473725391869419801716664372453775554757712481751968704577158437846771260413284009770218290762832891954510055886590737"
    testkeypath = "Key0.ElGamalKey"
    testswapname = "testswapname"
    testInitiatorChain = "Ergo"
    testResponderChain = "Sepolia"
    initiatorJSONPath = "initiator_test.json" #initiators local swap session json state
    responderJSONPath = "responder_test.json"
    EVMAddr1 = "0xFe4cc19ea6472582028641B2633d3adBB7685C69"

    ############### INITIATOR #####################################################
    clean_file_open(initiatorJSONPath, "w", "{}") #open initiators store file
    privateInit = initiation(EVMAddr1, testInitiatorChain, testResponderChain) #create a local initiation
    privateInitPATH = "priv_init_test.json"
    clean_file_open(privateInitPATH, "w", privateInit) #write initiation contents into private file
    initiation_keyValList = json_tools.json_to_keyValList(privateInitPATH) #backup the keys and values from this file
    json_tools.keyVal_list_update(initiation_keyValList, initiatorJSONPath) #update the initiators store file with the values

    publicInit = sanitizeInitiation(privateInit) #remove the private variables from the json
    publicInitPATH = "public_init_test.json"
    clean_file_open(publicInitPATH, "w", publicInit) #write the public variables into a public file

    encrypt = ElGamal_Encrypt(testkey, testkeypath, publicInitPATH, "ENC_init_test.bin") #encrypt the public file to receiver's pub
    ################################################################################


    ############## RESPONDER #######################################################
    ENC_Init_PATH = "ENC_init_test.bin"
    DEC_Init_PATH = "DEC_init_test.json"
    process_initiation(ENC_Init_PATH, DEC_Init_PATH, testkey, testkeypath)
    clean_file_open(responderJSONPath, "w", "{}")
    r_initiation_keyValList = json_tools.json_to_keyValList(DEC_Init_PATH)
    json_tools.keyVal_list_update(r_initiation_keyValList, responderJSONPath)
    responsePATH = "response_path_test.json"
    response("TestInitiationDecryptedPath.bin", "sr_path_test.bin", "x_path_test.bin", \
            responsePATH, testkey, testkeypath)
    xG = json.loads(clean_file_open(responsePATH, "r"))["xG"]
    buildScalarContract(testResponderChain, "0xFe4cc19ea6472582028641B2633d3adBB7685C69",  xG, 100, testswapname)
    addr = deployEVMContract(testswapname)
    if addr != "fail":
        #ASSUMING ITS ENDING WITH \n
        addr  =  addr[:-1]
        clean_file_open("ScalarContractAddrTest.bin", "w", addr.rstrip())
    else:
        print("fail: deployContract() didnt return a contract addr")
        exit()
    #add contract addr and chain name to response here then encrypt 
    update_response_keyValList = [{"responderLocalChain":testResponderChain}, {"responderContractAddr":addr}]
    json_tools.keyVal_list_update(update_response_keyValList, responsePATH)
    responseLIST = json_tools.json_to_keyValList(responsePATH)
    json_tools.keyVal_list_update(responseLIST, responderJSONPath)
    encrypted_response = ElGamal_Encrypt(testkey, testkeypath, responsePATH, "ENC_response_path_test.bin")
    ################################################################################

    ############### INITIATOR #####################################################
    decrypted_response = ElGamal_Decrypt("ENC_response_path_test.bin", testkey, testkeypath)
    print("self decrypted response:", decrypted_response)
    DEC_response_PATH = "DEC_response_test.json"
    clean_file_open(DEC_response_PATH, "w", decrypted_response)
    time.sleep(10)
    inspect_json = inspectResponse(DEC_response_PATH)
    if inspect_json == "Error: response does not have expected keys":
        print("fail")
        exit()
    clean_file_open("inspectContractTest.json", "w", inspect_json)
    inspect_list = json_tools.json_to_keyValList("inspectContractTest.json")
    json_tools.keyVal_list_update(inspect_list, initiatorJSONPath)
    response_list = json_tools.json_to_keyValList("DEC_response_path_test.bin")
    json_tools.keyVal_list_update(response_list, initiatorJSONPath)
    minimum_wei = 0
    if int(json.loads(clean_file_open(initiatorJSONPath, "r"))["counterpartyContractFundedAmount"]) < int(minimum_wei):
        print("not enough wei in contract, fail")
        exit()

    ###############################################################################
    print("success!")

if len(args) >= 1:
    if args[1] == "test":
        test()
