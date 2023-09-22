import os
import sys
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
#    if len(args) > 1:
#        boxId = args[1]
#       print("Running", contractName)
#       print(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().constants())
#        array = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().constants().array()[0]
       # for item in array:
        #    print(item.value())
#        print(dir(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().constants().toIndexedSeq()))


    def getContract(boxId, filepath=None):
        if filepath == None: 
#            sys.stdout.write(str(dir(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0])))
            print(str(dir(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree())))
            print(str(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree()))
        else:
            exit()
#            f = open(filepath, "w")
#            f.write(str(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().constants().array()[int(index)].value()))
#            f.close()

    if len(args) == 2:
        boxId = args[1]
        getContract(boxId)
    if len(args) == 3:
        boxId = args[1]
        filepath = args[2]
        getContract(boxId, filepath)
    


