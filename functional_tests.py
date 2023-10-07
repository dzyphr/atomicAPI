import sys
import json
import shutil
import configparser
from initiatorInterface import *
from responderInterface import *
from ElGamalInterface import *
from AtomicityInterface import * 
from SigmaParticleInterface import *
from FT_subroutines import *
import json_tools
import time
from enum import Enum
from enum_tools import *
import file_tools

def valFromConf(confPath, val):
    confParser = configparser.ConfigParser()
    confParser.read(confPath)
    return confParser['default'][val]

def FT_ErgoToSepolia(initiatorErgoAccountName, initiatorSepoliaAccountName, responderErgoAccountName, responderSepoliaAccountName):
    #test input data
    fileTransferProtocols = [
        "localCopy-linux"
    ]
    fileTransferProtocol = fileTransferProtocols[fileTransferProtocols.index("localCopy-linux")]
    swapName = "swapName"
    mi = {
            "initiatorErgoAccountName": initiatorErgoAccountName,
            "initiatorSepoliaAccountName": initiatorSepoliaAccountName,
            "responderErgoAccountName": responderErgoAccountName,
            "responderSepoliaAccountName": responderSepoliaAccountName,
            "ElGamalKey" : "688344026718772736449750175203366052782498205293898002465375827258042277361951460658218874759221293994168145022574766874751338527256700500579101512082414055194093613376114567923022297129476978722630282962906957224675125386874494158492157124310481876254258350563100432848938338097941551681473725391869419801716664372453775554757712481751968704577158437846771260413284009770218290762832891954510055886590737",
            "ElGamalKeyPath" : "Key0.ElGamalKey",
            "swapName" : swapName,
            "InitiatorChain" : "Ergo",
            "ResponderChain" : "Sepolia",
            "initiatorJSONPath" : swapName + "/initiator_test.json", #initiators local swap session json state
            "responderJSONPath" : swapName + "/responder_test.json",
            "ResponderEVMAddr" : \
                    valFromConf("EVM/Atomicity/" + responderSepoliaAccountName + "/.env", 'SepoliaSenderAddr').replace('"', ''),
            "InitiatorEVMAddr" : \
                    valFromConf("EVM/Atomicity/" + initiatorSepoliaAccountName + "/.env", 'SepoliaSenderAddr').replace('"', ''),
            "InitiatorEIP3Secret" : \
                    valFromConf("Ergo/SigmaParticle/" + initiatorErgoAccountName  + "/.env", 'senderEIP3Secret').replace('"', ''),
            "InitiatorErgoAddr" : \
                    valFromConf("Ergo/SigmaParticle/" + initiatorErgoAccountName + "/.env", 'senderPubKey').replace('"', ''),
            "ResponderEIP3Secret" : \
                    valFromConf("Ergo/SigmaParticle/" + responderErgoAccountName + "/.env", 'senderEIP3Secret').replace('"', ''),
            "ResponderErgoAddr" : \
                    valFromConf("Ergo/SigmaParticle/" + responderErgoAccountName + "/.env", 'senderPubKey').replace('"', ''),
            "privateInitPATH" : swapName + "/priv_init_test.json",
            "publicInitPATH" : swapName + "/public_init_test.json",
            "ENC_Init_PATH" : swapName + "/ENC_init_test.bin",
            "DEC_Init_PATH" : swapName + "/DEC_init_test.json",
            "responsePATH" : swapName + "/response_path_test.json",
            "ENC_Response_PATH" : swapName + "/ENC_response_path_test.bin",
            "DEC_Response_PATH" : swapName + "/DEC_response_test.json",
            "finalizationPATH" : swapName + "/finalization_test.json",
            "ENC_finalizationPATH" : swapName + "/ENC_finalization_test.bin",
            "DEC_finalizationPATH" : swapName + "/DEC_finalization_test.json",        
    }
    clean_mkdir("Initiator_" + mi["swapName"])
    clean_mkdir("Responder_" + mi["swapName"]) #make all testing folders
    #concept:
    #each function will return a path to the public round data to be sent to the counterparty
    #this will make it easy to change the file transfer protocol agnostically of test-cases
    clean_file_open("Initiator_" + mi["initiatorJSONPath"], "w", "{}")
    class initiatorInputEnum(Enum):
        initiatorErgoAccountName = mi["initiatorErgoAccountName"]
        initiatorSepoliaAccountName = mi["initiatorSepoliaAccountName"]
        ElGamalKey = mi["ElGamalKey"]
        ElGamalKeyPath = mi["ElGamalKeyPath"]
        swapName = "Initiator_" + mi["swapName"]
        InitiatorChain = mi["InitiatorChain"]
        ResponderChain = mi["ResponderChain"]
        initiatorJSONPath = "Initiator_" + mi["initiatorJSONPath"] #initiators local swap session json state
        InitiatorEVMAddr = mi["InitiatorEVMAddr"]
        InitiatorEIP3Secret = mi["InitiatorEIP3Secret"]
        InitiatorErgoAddr = mi["InitiatorErgoAddr"]
        privateInitPATH = "Initiator_" + mi["privateInitPATH"]
        publicInitPATH = "Initiator_" + mi["publicInitPATH"]
        ENC_Init_PATH = "Initiator_" + mi["ENC_Init_PATH"]
        ENC_Response_PATH = "Initiator_" + mi["ENC_Response_PATH"]
        DEC_Response_PATH = "Initiator_" + mi["DEC_Response_PATH"]
        finalizationPATH = "Initiator_" + mi["finalizationPATH"]
        ENC_finalizationPATH = "Initiator_" + mi["ENC_finalizationPATH"]
    json_tools.keyVal_list_update(keynum(initiatorInputEnum), "Initiator_" + mi["initiatorJSONPath"])
    initPath = FT_ErgoToSepolia_SUB_ENC_Initiation("Initiator_" + mi["initiatorJSONPath"])
    
    if fileTransferProtocol == 'localCopy-linux':
        file_tools.copy(initPath, file_tools.switchdirpath(initPath, "Responder_" + mi["swapName"])) 
    clean_file_open( "Responder_" + mi["responderJSONPath"], "w", "{}")
    class responderInputEnum(Enum):
        responderErgoAccountName = mi["responderErgoAccountName"]
        responderSepoliaAccountName = mi["responderSepoliaAccountName"]
        swapName = "Responder_" + mi["swapName"]
        InitiatorEVMAddr = mi["InitiatorEVMAddr"]
        ENC_Init_PATH = "Responder_" + mi["ENC_Init_PATH"]
        DEC_Init_PATH = "Responder_" + mi["DEC_Init_PATH"]
        ElGamalKey = mi["ElGamalKey"]
        ElGamalKeyPath = mi["ElGamalKeyPath"]
        responsePATH = "Responder_" + mi["responsePATH"]
        ENC_Response_PATH = "Responder_" + mi["ENC_Response_PATH"]
        ResponderChain = mi["ResponderChain"]
        ResponderErgoAddr = mi["ResponderErgoAddr"]
        ENC_finalizationPATH = "Responder_" + mi["ENC_finalizationPATH"]
        DEC_finalizationPATH = "Responder_" + mi["DEC_finalizationPATH"]
    json_tools.keyVal_list_update(keynum(responderInputEnum), "Responder_" + mi["responderJSONPath"])
    responsePath = FT_ErgoToSepolia_SUB_ENC_Response("Responder_" + mi["responderJSONPath"])

    if fileTransferProtocol == 'localCopy-linux':
        file_tools.copy(responsePath, file_tools.switchdirpath(responsePath, "Initiator_" + mi["swapName"]))

    finalizationPath = FT_ErgoToSepolia_SUB_ENC_Finalization("Initiator_" + mi["initiatorJSONPath"])
    if fileTransferProtocol == 'localCopy-linux':
        file_tools.copy(finalizationPath, file_tools.switchdirpath(finalizationPath, "Responder_" + mi["swapName"]))

    FT_ErgoToSepolia_SUB_ENC_ResponderClaim("Responder_" + mi["responderJSONPath"])

    FT_ErgoToSepolia_SUB_ENC_InitiatorClaim("Initiator_" + mi["initiatorJSONPath"])
