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
    
    def getPubkey(index):
        sys.stdout.write(senderAddress[index])

    if len(args) > 1:
        if args[1] == "getPubkey":
            if len(args) > 2:
               getPubkey(int(args[2]))
            else:
                print("enter pubkey index as argument [0 - 9 for now]")
        else:
            print(args[1])
            print("unknown arg")
    else:
        print("enter arguments:\n \
                1)  getPubkey [index]")
                
    
