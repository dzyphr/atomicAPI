import sys
import os
import time
import random
import jpype
from jpype import *
import java.lang
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
from ergpy import helper_functions, appkit
import waits
import coinSelection
import scalaPipe
def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress, args):
#    org.slf4j.impl.StaticLoggerBinder 
    def treeFromBox(boxId, filepath=None):
        if filepath == None:
            inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId)) 
            sys.stdout.write(str(inputBox[0].getErgoTree().bytesHex()))
#            print(dir(inputBox[0].getErgoTree().bytesHex()))
        else:
            tree = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().bytesHex()
            print(tree)
            f = open(filepath, "w")
            f.write(str(tree))
            f.close()
            sys.stdout.write(str(inputBox[0].getErgoTree().bytesHex()))

    if len(args) > 1:
        if len(args) > 2:
            treeFromBox(args[1], args[2])
            exit()
        treeFromBox(args[1])
        exit()

    else:
        print("enter boxId as argument")

