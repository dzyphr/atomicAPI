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
def clearDirPath(path):
    if os.path.isdir(path):
        shutil.rmtree(path)

def valFromConf(confPath, val):
    confParser = configparser.ConfigParser()
    confParser.read(confPath)
    return confParser['default'][val]

def FT_ErgoToSepolia():
    #test input data
    swapName = "swapName"
    mi = {
            "ElGamalKey" : "688344026718772736449750175203366052782498205293898002465375827258042277361951460658218874759221293994168145022574766874751338527256700500579101512082414055194093613376114567923022297129476978722630282962906957224675125386874494158492157124310481876254258350563100432848938338097941551681473725391869419801716664372453775554757712481751968704577158437846771260413284009770218290762832891954510055886590737",
            "ElGamalKeyPath" : "Key0.ElGamalKey",
            "swapName" : swapName,
            "InitiatorChain" : "Ergo",
            "ResponderChain" : "Sepolia",
            "initiatorJSONPath" : swapName + "/initiator_test.json", #initiators local swap session json state
            "responderJSONPath" : swapName + "/responder_test.json",
            "ResponderEVMAddr" : "0xFe4cc19ea6472582028641B2633d3adBB7685C69",
            "InitiatorEVMAddr" : "0x01225869F695b4b7F0af5d75381Fe340A4d27593",
            "InitiatorEIP3Secret" : valFromConf("Ergo/SigmaParticle/" + "basic_framework/.env", 'senderEIP3Secret'),
            "InitiatorErgoAddr" : "3WwS8bSAhXuTu5xR5CxCrcfvUemQ7fqoPcNMLd8SagSWbcAbrE1S",
            "ResponderEIP3Secret" : valFromConf("Ergo/SigmaParticle/" + "responderEnv/.env", 'senderEIP3Secret'),
            "ResponderErgoAddr" : "3WwGZfTh3uur3g1dSUdHFXtRfGKtRJUPhiAwNWDuf2LGpcjRzC3y",
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
    clean_mkdir(mi["swapName"])
    clean_file_open(mi["initiatorJSONPath"], "w", "{}")
    class initiatorInputEnum(Enum):
        ElGamalKey = mi["ElGamalKey"]
        ElGamalKeyPath = mi["ElGamalKeyPath"]
        swapName = mi["swapName"]
        InitiatorChain = mi["InitiatorChain"]
        ResponderChain = mi["ResponderChain"]
        initiatorJSONPath = mi["initiatorJSONPath"] #initiators local swap session json state
        InitiatorEVMAddr = mi["InitiatorEVMAddr"]
        InitiatorEIP3Secret = mi["InitiatorEIP3Secret"]
        InitiatorErgoAddr = mi["InitiatorErgoAddr"]
        privateInitPATH = mi["privateInitPATH"]
        publicInitPATH = mi["publicInitPATH"]
        ENC_Init_PATH = mi["ENC_Init_PATH"]
        ENC_Response_PATH = mi["ENC_Response_PATH"]
        DEC_Response_PATH = mi["DEC_Response_PATH"]
        finalizationPATH = mi["finalizationPATH"]
        ENC_finalizationPATH = mi["ENC_finalizationPATH"]
    json_tools.keyVal_list_update(keynum(initiatorInputEnum), mi["initiatorJSONPath"])
    FT_ErgoToSepolia_SUB_ENC_Initiation(mi["initiatorJSONPath"])

    clean_mkdir(swapName) #formality for now, needed for real p2p tests / impls
    clean_file_open(mi["responderJSONPath"], "w", "{}")
    class responderInputEnum(Enum):
        swapName = mi["swapName"]
        InitiatorEVMAddr = mi["InitiatorEVMAddr"]
        ENC_Init_PATH = mi["ENC_Init_PATH"]
        DEC_Init_PATH = mi["DEC_Init_PATH"]
        ElGamalKey = mi["ElGamalKey"]
        ElGamalKeyPath = mi["ElGamalKeyPath"]
        responsePATH = mi["responsePATH"]
        ENC_Response_PATH = mi["ENC_Response_PATH"]
        ResponderChain = mi["ResponderChain"]
        ResponderErgoAddr = mi["ResponderErgoAddr"]
        ENC_finalizationPATH = mi["ENC_finalizationPATH"]
        DEC_finalizationPATH = mi["DEC_finalizationPATH"]
    json_tools.keyVal_list_update(keynum(responderInputEnum), mi["responderJSONPath"])
    FT_ErgoToSepolia_SUB_ENC_Response(mi["responderJSONPath"])

    FT_ErgoToSepolia_SUB_ENC_Finalization(mi["initiatorJSONPath"])
    
    FT_ErgoToSepolia_SUB_ENC_ResponderClaim(mi["responderJSONPath"])

    FT_ErgoToSepolia_SUB_ENC_InitiatorClaim(mi["initiatorJSONPath"])

