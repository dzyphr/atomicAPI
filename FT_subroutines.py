import sys
import ast
import json
import shutil
import configparser
from initiatorInterface import *
from responderInterface import *
from ElGamalInterface import *
from AtomicityInterface import * 
from SigmaParticleInterface import *
import json_tools
import time



def FT_ErgoToSepolia_SUB_ENC_Initiation(initiatorJSONPath):
    ############### INITIATOR #####################################################
    init_J = json_tools.ojf(initiatorJSONPath)
    swapname = init_J["swapName"]
    InitiatorEVMAddr = init_J["InitiatorEVMAddr"]
    InitiatorChain = init_J["InitiatorChain"]
    ResponderChain = init_J["ResponderChain"]
    privateInitPATH = init_J["privateInitPATH"]
    publicInitPATH = init_J["publicInitPATH"]
    ElGamalKey = init_J["ElGamalKey"]
    ElGamalKeyPath = init_J["ElGamalKeyPath"]
    ENC_Init_PATH = init_J["ENC_Init_PATH"]
    privateInit = initiation(InitiatorEVMAddr, InitiatorChain, ResponderChain) #create a local initiation
    clean_file_open(privateInitPATH, "w", privateInit) #write initiation contents into private file
    initiation_keyValList = json_tools.json_to_keyValList(privateInitPATH) #backup the keys and values from this file
    json_tools.keyVal_list_update(initiation_keyValList, initiatorJSONPath) #update the initiators store file with the values
    publicInit = sanitizeInitiation(privateInit) #remove the private variables from the json
    clean_file_open(publicInitPATH, "w", publicInit) #write the public variables into a public file
    encrypt = ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, publicInitPATH, ENC_Init_PATH) #encrypt the public file to receiver's pub
    return ENC_Init_PATH
    ################################################################################

    #note: the arguments are getting to be a bit much, we will pack pretty much everything into masterJSONs from now on
def FT_ErgoToSepolia_SUB_ENC_Response(responderJSONPath):
    ############## RESPONDER #######################################################
    resp_J = json_tools.ojf(responderJSONPath)
    swapname = resp_J["swapName"]
    ENC_Init_PATH = resp_J["ENC_Init_PATH"]
    DEC_Init_PATH = resp_J["DEC_Init_PATH"]
    ElGamalKey = resp_J["ElGamalKey"]
    ElGamalKeyPath = resp_J["ElGamalKeyPath"]
    responsePATH = resp_J["responsePATH"]
    ENC_Response_PATH = resp_J["ENC_Response_PATH"]
    InitiatorEVMAddr = resp_J["InitiatorEVMAddr"]
    ResponderChain = resp_J["ResponderChain"]
    ResponderErgoAddr = resp_J["ResponderErgoAddr"]

    process_initiation(ENC_Init_PATH, DEC_Init_PATH, ElGamalKey, ElGamalKeyPath)
    r_initiation_keyValList = json_tools.json_to_keyValList(DEC_Init_PATH)
    json_tools.keyVal_list_update(r_initiation_keyValList, responderJSONPath)
    response(DEC_Init_PATH, responderJSONPath, \
            responsePATH, ElGamalKey, ElGamalKeyPath)
    #TODO: replace sr and x paths with master json update
    xG = json.loads(clean_file_open(responsePATH, "r"))["xG"]
    Atomicity_buildScalarContract(ResponderChain, InitiatorEVMAddr,  xG, 100, swapname)

    addr = Atomicity_deployEVMContract(swapname, customGasMod=2)
    if addr != "fail":
        #ASSUMING ITS ENDING WITH \n
        addr  =  addr[:-1]
    else:
        print("fail: deployContract() didnt return a contract addr")
        exit()
    #add contract addr and chain name to response here then encrypt 
    responderFundingAmountWei = 2000000000
    Atomicity_SendFunds(addr, responderFundingAmountWei, swapname)
    update_response_keyValList = [{"responderLocalChain":ResponderChain}, \
            {"responderContractAddr":addr},\
            {"ResponderErgoAddr":ResponderErgoAddr}]
    json_tools.keyVal_list_update(update_response_keyValList, responsePATH)
    responseLIST = json_tools.json_to_keyValList(responsePATH)
    json_tools.keyVal_list_update(responseLIST, responderJSONPath)
    encrypted_response = ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, responsePATH, ENC_Response_PATH)
    return ENC_Response_PATH
    ################################################################################

def FT_ErgoToSepolia_SUB_ENC_Finalization(initiatorJSONPath):
    ############### INITIATOR ######################################################
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
    inspect_json = inspectResponse(DEC_Response_PATH)
    if inspect_json == "Error: response does not have expected keys":
        print("fail")
        exit()
    clean_file_open(swapName + "/inspectContractTest.json", "w", inspect_json)
    inspect_list = json_tools.json_to_keyValList(swapName + "/inspectContractTest.json")
    json_tools.keyVal_list_update(inspect_list, initiatorJSONPath)
    minimum_wei = 0 #this is practically set for existential transfer calculations due to variable fee rates
    if int(json.loads(clean_file_open(initiatorJSONPath, "r"))["counterpartyContractFundedAmount"]) < int(minimum_wei):
        print("not enough wei in contract, fail")
        exit()
#    print("checkcoords:", Atomicity_compareScalarContractCoords(swapName, addr, xG[0], xG[1]))
    if Atomicity_compareScalarContractCoords(swapName, addr, xG[0], xG[1]) == False:
        print("on chain contract does not meet offchain contract spec, do not fulfil this swap!")
        exit()
    finalizeOBJ = finalizeSwap(initiatorJSONPath)
    clean_file_open(finalizationPATH, "w", finalizeOBJ)
    finalizeOBJ_LIST = json_tools.json_to_keyValList(finalizationPATH)
    json_tools.keyVal_list_update(finalizeOBJ_LIST, initiatorJSONPath)
    BuildAtomicSchnorrContract(initiatorJSONPath, 25, swapName, 123841)
    deployErgoContract(swapName)
    boxId = getBoxID(swapName)
    InitiatorAtomicSchnorrLockHeight = clean_file_open("Ergo/SigmaParticle/" + swapName + "/lockHeight", "r")
    contractKeyValList = [{"boxId":boxId, "InitiatorAtomicSchnorrLockHeight":InitiatorAtomicSchnorrLockHeight, \
            "InitiatorErgoAddr":InitiatorErgoAddr}]
    json_tools.keyVal_list_update(contractKeyValList, initiatorJSONPath)
    json_tools.keyVal_list_update(contractKeyValList, finalizationPATH)
    ENC_finalization =  ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, finalizationPATH, ENC_finalizationPATH)
    return ENC_finalizationPATH
    ################################################################################
    
def FT_ErgoToSepolia_SUB_ENC_ResponderClaim(responderJSONPath):
    ############## RESPONDER #######################################################
    resp_J = json_tools.ojf(responderJSONPath)
    swapName = resp_J["swapName"]
    ENC_finalizationPATH = resp_J["ENC_finalizationPATH"]
    ElGamalKey = resp_J["ElGamalKey"]
    ElGamalKeyPath = resp_J["ElGamalKeyPath"]
    DEC_finalizationPATH = resp_J["DEC_finalizationPATH"]
    responderErgoAccountName = resp_J["responderErgoAccountName"]
    DEC_finalization = ElGamal_Decrypt(ENC_finalizationPATH, ElGamalKey, ElGamalKeyPath)
    clean_file_open(DEC_finalizationPATH, "w", DEC_finalization)
    finalization_list = json_tools.json_to_keyValList(DEC_finalizationPATH)
    json_tools.keyVal_list_update(finalization_list, responderJSONPath)
    boxID = json.loads(DEC_finalization)["boxId"]
    boxValue = checkBoxValue(boxID, swapName + "/testBoxValPath.bin")
    #other than just the box value responder should verify the scalars in the contract match those expected 
    minBoxValue = 1123841 #1123841
    if int(boxValue) < int(minBoxValue):
        print("not enough nanoerg in contract")
        exit()
    SigmaParticle_newFrame(swapName)
    SigmaParticle_updateKeyEnv(swapName, responderErgoAccountName) 
    responderGenerateAtomicSchnorr(swapName, DEC_finalizationPATH, responderJSONPath, boxValue)
    expectedErgoTree = SigmaParticle_getTreeFromBox(boxID)
    if responderVerifyErgoScript(swapName, expectedErgoTree) == False:
        print("ergoScript verification returned false, wont fulfil swap")
        exit()
#    print("ergo contract verification status:", responderVerifyErgoScript(swapName, expectedErgoTree))
    responderClaimAtomicSchnorr(swapName, 2500)
    ################################################################################

def FT_ErgoToSepolia_SUB_ENC_InitiatorClaim(initiatorJSONPath):
    ############## INITIATOR #######################################################
    init_J = json.loads(clean_file_open(initiatorJSONPath, "r"))
    swapName = init_J["swapName"]
    boxID = init_J["boxId"]
    initiatorSepoliaAccountName = init_J["initiatorSepoliaAccountName"]
    checkSchnorrTreeForClaim(boxID, swapName, initiatorJSONPath) 
    deduceX_fromAtomicSchnorrClaim(initiatorJSONPath, swapName)
    Atomicity_updateKeyEnv(swapName, initiatorSepoliaAccountName)
    Atomicity_claimScalarContract(initiatorJSONPath, swapName)
    ################################################################################
#    print("success!")

