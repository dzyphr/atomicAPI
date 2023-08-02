import sys
import json
from initiatorInterface import *
from responderInterface import *
from ElGamalInterface import *
args = sys.argv


def test():
    testkey = "688344026718772736449750175203366052782498205293898002465375827258042277361951460658218874759221293994168145022574766874751338527256700500579101512082414055194093613376114567923022297129476978722630282962906957224675125386874494158492157124310481876254258350563100432848938338097941551681473725391869419801716664372453775554757712481751968704577158437846771260413284009770218290762832891954510055886590737"
    testkeypath = "Key0.ElGamalKey"

    privateInit = initiation("0xFe4cc19ea6472582028641B2633d3adBB7685C69", "Ergo")
    print(privateInit)
    publicInit = sanitizeInitiation(privateInit)
    print(publicInit)
    encrypt = ElGamal_Encrypt(testkey, testkeypath, publicInit, "Test_Encryption.bin")
    ENC_init = clean_file_open("Test_Encryption.bin", "r")
    process_initiation(ENC_init, "TestResponseEncryptedPath.bin", "TestResponseDecryptedPath.bin", testkey, testkeypath)
    response("TestResponseDecryptedPath.bin", "sr_path_test.bin", "x_path_test.bin", \
            "response_path_test.bin",  "ENC_response_path_test.bin", testkey, testkeypath)
    decrypted_response = ElGamal_Decrypt("ENC_response_path_test.bin", testkey, testkeypath)
    print(decrypted_response)
    clean_file_open("DEC_response_path_test.bin", "w", decrypted_response)
    inspectResponse("DEC_response_path_test.bin", "responderinfo_test.json")
    

if len(args) >= 1:
    if args[1] == "test":
        test()
