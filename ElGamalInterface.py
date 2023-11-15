import os
import file_tools
import json_tools
ElGamal = "./ElGamal "
s_ = " "


def update_ElGamalPubKeysJSON():
    pubkeyStoreJSONPath = "ElGamalPubKeys.json"
    keyIndex = 0
    if os.path.isfile(pubkeyStoreJSONPath) == False:
        file_tools.clean_file_open(pubkeyStoreJSONPath, "w", "{}")
    while True:
        path = "Key" + str(keyIndex) + ".ElGamalKey"
        if os.path.isfile(path):
            pubkey = json_tools.ojf(path)["Public Key"]
            updatelist = [{keyIndex:pubkey}]
            json_tools.keyVal_list_update(updatelist, pubkeyStoreJSONPath)
            keyIndex = keyIndex + 1
        else:
            break


def generateNewElGamalPubKey(q=None, g=None):
    command = ""
    if q == None or g == None:
        command = "./ElGamal genPubKey"
    else:
        command = "./ElGamal genPubKey_specific_q_g " + q + " " + g
    os.popen(command).read()
    update_ElGamalPubKeysJSON()




def ElGamal_Encrypt(receiverPubKey, userKeyFileName, subject, filePath):
    command = \
            "subject=" + "\'" + subject + "\' " + " && " + \
            ElGamal + "encryptToPubKey " + \
            receiverPubKey + s_ + \
            userKeyFileName + s_ + \
            " $subject " + s_ + \
            filePath
#    print(command)
    return os.popen(command).read()

def ElGamal_Decrypt(subjectFilePath, senderPubKey, userKeyFileName):
    command = \
            ElGamal + "decryptFromPubKey " +\
            subjectFilePath + s_ + \
            senderPubKey + s_ + \
            userKeyFileName 
    decryption = os.popen(command).read()
    return decryption

            

