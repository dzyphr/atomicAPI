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
    def getConstantAt(boxId, index, filepath=None):
        if filepath == None: 
            sys.stdout.write(str(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().constants().array()[int(index)].value()))
        else:
            f = open(filepath, "w")
            f.write(str(java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().constants().array()[int(index)].value()))
            f.close()
    if len(args) == 2:
        boxId = args[1]
        array = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getErgoTree().constants().array()[0]
        sys.stdout.write(str(array))
    if len(args) == 3:
        boxId = args[1]
        index = args[2]
        getConstantAt(boxId, index)
    if len(args) >= 4:
        boxId = args[1]
        index = args[2]
        filepath = args[3]
        getConstantAt(boxId, index, filepath)
    


