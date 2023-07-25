import sys
import json
from initiatorInterface import *
from ElGamalInterface import *
args = sys.argv


def test():
    privateInit = initiation("0xFe4cc19ea6472582028641B2633d3adBB7685C69", "Ergo")
    print(privateInit)
    publicInit = sanitizeInitiation(privateInit)
    print(publicInit)
    testkey = "688344026718772736449750175203366052782498205293898002465375827258042277361951460658218874759221293994168145022574766874751338527256700500579101512082414055194093613376114567923022297129476978722630282962906957224675125386874494158492157124310481876254258350563100432848938338097941551681473725391869419801716664372453775554757712481751968704577158437846771260413284009770218290762832891954510055886590737"
    encrypt = ElGamal_Encrypt(testkey, "Key0.ElGamalKey", publicInit, "Test_Encryption.bin")
    decrypt = ElGamal_Decrypt("Test_Encryption.bin", testkey, "Key0.ElGamalKey")
    print(decrypt)
    

if len(args) >= 1:
    if args[1] == "test":
        test()
