import os
import file_tools
import json_tools
ElGamal = "./ElGamal "
s_ = " "



def update_ElGamalPubKeysJSON(index):
    pubkeyStoreJSONPath = "ElGamalPubKeys.json"
    QGChannelStoreJSONPath = "ElGamalQGChannels.json"
    QGPubkeyArrayStoreJSONPath = "QGPubkeyArray.json"
    keyIndex = 0
    if os.path.isfile(pubkeyStoreJSONPath) == False:
        file_tools.clean_file_open(pubkeyStoreJSONPath, "w", "{}")
    if os.path.isfile(QGChannelStoreJSONPath) == False:
        file_tools.clean_file_open(QGChannelStoreJSONPath, "w", "{}")
    if os.path.isfile(QGPubkeyArrayStoreJSONPath) == False:
        file_tools.clean_file_open(QGPubkeyArrayStoreJSONPath, "w", "{}")
    while True:
        path = "Key" + str(keyIndex) + ".ElGamalKey"
        if os.path.isfile(path):
            pubkey = json_tools.ojf(path)["Public Key"]
            Q = json_tools.ojf(path)["q"]
            G = json_tools.ojf(path)["g"]
            QG = f"{Q},{G}"
            if keyIndex == index:
                print(pubkey, index)
            updatelist = [{keyIndex:pubkey}]
            json_tools.keyVal_list_update(updatelist, pubkeyStoreJSONPath)
            keyIndex = keyIndex + 1
            QGList = json_tools.ojf(QGChannelStoreJSONPath)
            QGPubkeyArray = json_tools.ojf(QGPubkeyArrayStoreJSONPath)
            if QG not in QGList.values():
                #not in list, add it
                QGIndex = len(QGList) + 1
                QGupdateList = [{QGIndex:QG}]
                json_tools.keyVal_list_update(QGupdateList, QGChannelStoreJSONPath)
            if QG not in QGPubkeyArray.keys():
                QGPubkeyArrayUpdateList = [{QG:pubkey}]
                json_tools.keyVal_list_update(QGPubkeyArrayUpdateList, QGPubkeyArrayStoreJSONPath)
            elif pubkey not in QGPubkeyArray.values():
                if type(QGPubkeyArray[QG]) != list:
                    newlist = [QGPubkeyArray[QG], pubkey]
                    QGPubkeyArrayUpdateList = [{QG:newlist}]
                    json_tools.keyVal_list_update(QGPubkeyArrayUpdateList, QGPubkeyArrayStoreJSONPath)
                    #make it a list
                else:
                    publist = QGPubkeyArray[QG]
                    publist.append(pubkey)
                    QGPubkeyArrayUpdateList = [{QG:list(set(publist))}]
                    json_tools.keyVal_list_update(QGPubkeyArrayUpdateList, QGPubkeyArrayStoreJSONPath)
                    #add to the list
        else:
            break

def currentKeysStateCheck():
    keyIndex = 0
    while True:
        path = "Key" + str(keyIndex) + ".ElGamalKey"
        if os.path.isfile(path) == False:
            return keyIndex 
        else:
            keyIndex = keyIndex + 1
            continue

def generateNewElGamalPubKey(q=None, g=None):
    command = ""
    index = currentKeysStateCheck()
    if q is None and g is None:
        command = "./ElGamal genPubKey"
    elif q is not None and g is not None:
        command = "./ElGamal genPubKey_specific_q_g " + q + " " + g
    elif q is not None and g is None:
        command = "./ElGamal genPubKey_specific_q " + q
    os.popen(command).read()
    update_ElGamalPubKeysJSON(index)




def ElGamal_Encrypt(receiverPubKey, userKeyFileName, subject, filePath):
    command = \
            "subject=" + "\'" + subject + "\' " + " && " + \
            ElGamal + "encryptToPubKey " + \
            receiverPubKey + s_ + \
            userKeyFileName + s_ + \
            " $subject " + s_ + \
            filePath
#    file_tools.clean_file_open("ElGEncTest", "w" , command)
    return os.popen(command).read()

def ElGamal_Decrypt(subjectFilePath, senderPubKey, userKeyFileName):
    command = \
            ElGamal + "decryptFromPubKey " +\
            subjectFilePath + s_ + \
            senderPubKey + s_ + \
            userKeyFileName 
    decryption = os.popen(command).read()
    return decryption

            

