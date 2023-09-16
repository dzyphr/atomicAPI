import sys
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



def FT_ErgoToSepolia_SUB_ENC_Initiation(\
        swapname, initiatorJSONPath, InitiatorEVMAddr, initiatorChain, \
        responderChain, publicInitPATH, privateInitPATH, ElGamalKey, ElGamalKeyPath, ENC_Init_PATH):
    ############### INITIATOR #####################################################
    clean_mkdir(swapname)
    clean_file_open(initiatorJSONPath, "w", "{}") #open initiators store file
    privateInit = initiation(InitiatorEVMAddr, initiatorChain, responderChain) #create a local initiation
    clean_file_open(privateInitPATH, "w", privateInit) #write initiation contents into private file
    initiation_keyValList = json_tools.json_to_keyValList(privateInitPATH) #backup the keys and values from this file
    json_tools.keyVal_list_update(initiation_keyValList, initiatorJSONPath) #update the initiators store file with the values
    swapnamelist = [{"swapName":swapname}]
    json_tools.keyVal_list_update(swapnamelist, initiatorJSONPath)
    publicInit = sanitizeInitiation(privateInit) #remove the private variables from the json
    clean_file_open(publicInitPATH, "w", publicInit) #write the public variables into a public file
    encrypt = ElGamal_Encrypt(ElGamalKey, ElGamalKeyPath, publicInitPATH, ENC_Init_PATH) #encrypt the public file to receiver's pub
    ################################################################################

    '''
    ############## RESPONDER #######################################################
    clean_file_open(responderJSONPath, "w", "{}")
    clean_mkdir(testswapname)
    swapnamelist = [{"swapName":testswapname}]
    json_tools.keyVal_list_update(swapnamelist, responderJSONPath)
    process_initiation(ENC_Init_PATH, DEC_Init_PATH, testElGamalKey, testElGamalKeyPath)
    r_initiation_keyValList = json_tools.json_to_keyValList(DEC_Init_PATH)
    json_tools.keyVal_list_update(r_initiation_keyValList, responderJSONPath)
    response(DEC_Init_PATH, responderJSONPath, \
            responsePATH, testElGamalKey, testElGamalKeyPath)
    #TODO: replace sr and x paths with master json update
    xG = json.loads(clean_file_open(responsePATH, "r"))["xG"]
    Atomicity_buildScalarContract(testResponderChain, InitiatorEVMAddr,  xG, 100, testswapname)

    addr = Atomicity_deployEVMContract(testswapname, customGasMod=2)
    if addr != "fail":
        #ASSUMING ITS ENDING WITH \n
        addr  =  addr[:-1]
    else:
        print("fail: deployContract() didnt return a contract addr")
        exit()
    #add contract addr and chain name to response here then encrypt 
    responderFundingAmountWei = 2000000000
    Atomicity_SendFunds(addr, responderFundingAmountWei, testswapname)
    update_response_keyValList = [{"responderLocalChain":testResponderChain}, \
            {"responderContractAddr":addr}, \
            {"responderErgoChainPubKey":ResponderErgoAddr}]
    json_tools.keyVal_list_update(update_response_keyValList, responsePATH)
    responseLIST = json_tools.json_to_keyValList(responsePATH)
    json_tools.keyVal_list_update(responseLIST, responderJSONPath)
    encrypted_response = ElGamal_Encrypt(testElGamalKey, testElGamalKeyPath, responsePATH, ENC_Response_PATH)
    ################################################################################

    ############### INITIATOR ######################################################
    decrypted_response = ElGamal_Decrypt(ENC_Response_PATH, testElGamalKey, testElGamalKeyPath)
    clean_file_open(DEC_Response_PATH, "w", decrypted_response)
    time.sleep(10)
    inspect_json = inspectResponse(DEC_Response_PATH)
    if inspect_json == "Error: response does not have expected keys":
        print("fail")
        exit()
    clean_file_open(testswapname + "/inspectContractTest.json", "w", inspect_json)
    inspect_list = json_tools.json_to_keyValList(testswapname + "/inspectContractTest.json")
    json_tools.keyVal_list_update(inspect_list, initiatorJSONPath)
    response_list = json_tools.json_to_keyValList(DEC_Response_PATH)
    json_tools.keyVal_list_update(response_list, initiatorJSONPath)
    minimum_wei = 0 #this is practically set for existential transfer calculations due to variable fee rates
    if int(json.loads(clean_file_open(initiatorJSONPath, "r"))["counterpartyContractFundedAmount"]) < int(minimum_wei):
        print("not enough wei in contract, fail")
        exit()
    finalizeOBJ = finalizeSwap(initiatorJSONPath)
    clean_file_open(finalizationPATH, "w", finalizeOBJ)
    finalizeOBJ_LIST = json_tools.json_to_keyValList(finalizationPATH)
    json_tools.keyVal_list_update(finalizeOBJ_LIST, initiatorJSONPath)
    EIP3list = [{"initiatorEIP3Secret":InitiatorEIP3Secret}]
    json_tools.keyVal_list_update(EIP3list, initiatorJSONPath)
    BuildAtomicSchnorrContract(initiatorJSONPath, 25, testswapname, 123841)
    deployErgoContract(testswapname)
    boxId = getBoxID(testswapname)
    boxIdKeyValList = [{"boxId":boxId}]
    json_tools.keyVal_list_update(boxIdKeyValList, initiatorJSONPath)
    json_tools.keyVal_list_update(boxIdKeyValList, finalizationPATH)
    ENC_finalization =  ElGamal_Encrypt(testElGamalKey, testElGamalKeyPath, finalizationPATH, ENC_finalizationPATH)
    ################################################################################


    ############## RESPONDER #######################################################
    DEC_finalization = ElGamal_Decrypt(ENC_finalizationPATH, testElGamalKey, testElGamalKeyPath)
    clean_file_open(DEC_finalizationPATH, "w", DEC_finalization)
    boxID = json.loads(DEC_finalization)["boxId"]
    boxValue = checkBoxValue(boxID, testswapname + "/testBoxValPath.bin")
    #other than just the box value responder should verify the scalars in the contract match those expected 
    minBoxValue = 1123841 #1123841
    if int(boxValue) < int(minBoxValue):
        print("not enough nanoerg in contract")
        exit()
    SigmaParticle_updateKeyEnv(testswapname, "responderEnv")  
    responderClaimAtomicSchnorr(testswapname, DEC_finalizationPATH, responderJSONPath, boxValue)
    ################################################################################

    ############## INITIATOR #######################################################
    j = json.loads(clean_file_open(initiatorJSONPath, "r"))
    boxID = j["boxId"]
    checkSchnorrTreeForClaim(boxID, testswapname, initiatorJSONPath) 
    deduceX_fromAtomicSchnorrClaim(initiatorJSONPath, testswapname)
    Atomicity_updateKeyEnv(testswapname, "p2ENV")
    Atomicity_claimScalarContract(initiatorJSONPath, testswapname)
    ################################################################################
    print("success!")
    '''

