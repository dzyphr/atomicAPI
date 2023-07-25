import os

ElGamal = "./ElGamal "
s_ = " "

def ElGamal_Encrypt(receiverPubKey, userKeyFileName, subject, filePath):
    command = \
            ElGamal + "encryptToPubKey " + \
            receiverPubKey + s_ + \
            userKeyFileName + s_ + \
            "\'" + subject + "\'" + s_ + \
            filePath
    return os.popen(command).read()

def ElGamal_Decrypt(subjectFilePath, senderPubKey, userKeyFileName):
    command = \
            ElGamal + "decryptFromPubKey " +\
            subjectFilePath + s_ + \
            senderPubKey + s_ + \
            userKeyFileName 
    decryption = os.popen(command).read()
    return decryption

            

