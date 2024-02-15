import os
import file_tools
import json_tools
ElGamal = "./ElGamal "
s_ = " "



def update_ElGamalPubKeysJSON():
    #q:pubkey list for clients to coordinate from available options
    pubkeyStoreJSONPath = "ElGamalPubKeys.json"
    QChannelStoreJSONPath = "ElGamalQChannels.json"
    QPubkeyArrayStoreJSONPath = "QPubkeyArray.json"
    keyIndex = 0
    if os.path.isfile(pubkeyStoreJSONPath) == False:
        file_tools.clean_file_open(pubkeyStoreJSONPath, "w", "{}")
    if os.path.isfile(QChannelStoreJSONPath) == False:
        file_tools.clean_file_open(QChannelStoreJSONPath, "w", "{}")
    if os.path.isfile(QPubkeyArrayStoreJSONPath) == False:
        file_tools.clean_file_open(QPubkeyArrayStoreJSONPath, "w", "{}")
    while True:
        path = "Key" + str(keyIndex) + ".ElGamalKey"
        if os.path.isfile(path):
            Q = json_tools.ojf(path)["q"]
            pubkey = json_tools.ojf(path)["Public Key"]
            updatelist = [{keyIndex:pubkey}]
            json_tools.keyVal_list_update(updatelist, pubkeyStoreJSONPath)
            keyIndex = keyIndex + 1
            QList = json_tools.ojf(QChannelStoreJSONPath)
            QPubkeyArray = json_tools.ojf(QPubkeyArrayStoreJSONPath)
            if Q not in QList.values():
                #not in list, add it
                QIndex = len(QList) + 1
                QupdateList = [{QIndex:Q}]
                json_tools.keyVal_list_update(QupdateList, QChannelStoreJSONPath)
            elif Q not in QPubkeyArray.keys():
                QPubkeyArrayUpdateList = [{Q:pubkey}]
                json_tools.keyVal_list_update(QPubkeyArrayUpdateList, QPubkeyArrayStoreJSONPath)
            elif pubkey not in QPubkeyArray.values():
                if type(QPubkeyArray[Q]) != list:
                    newlist = [QPubkeyArray[Q], pubkey]
                    QPubkeyArrayUpdateList = [{Q:newlist}]
                    json_tools.keyVal_list_update(QPubkeyArrayUpdateList, QPubkeyArrayStoreJSONPath)
                    #make it a list
                else:
                    publist = QPubkeyArray[Q]
                    publist.append(pubkey)
                    QPubkeyArrayUpdateList = [{Q:list(set(publist))}]
                    json_tools.keyVal_list_update(QPubkeyArrayUpdateList, QPubkeyArrayStoreJSONPath)
                    #add to the list
        else:
            break


def generateNewElGamalPubKey(q=None, g=None):
    command = ""
    if q is None and g is None:
        command = "./ElGamal genPubKey"
        print("none")
    elif q is not None and g is not None:
        command = "./ElGamal genPubKey_specific_q_g " + q + " " + g
        print("qg")
    elif q is not None and g is None:
        command = "./ElGamal genPubKey_specific_q " + q
        print("q")
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

            

