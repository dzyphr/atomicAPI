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

            

