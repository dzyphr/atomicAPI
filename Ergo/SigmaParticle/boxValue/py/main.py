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
#import waits
#import coinSelection
#import scalaPipe
def boxVal(ergo, boxId, filepath=None):
    if filepath == None:
        inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))
#       sys.stdout.write(str(inputBox[0].getValue()))
#        sys.stdout.write(str(inputBox[0].getValue()))
        return inputBox[0].getValue()
    else:
        value = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getValue()
#        sys.stdout.write(str(value))
        f = open(filepath, "w")
        f.write(str(value))
        f.close()
        return value

def main(contractName, ergo,  args):
#    org.slf4j.impl.StaticLoggerBinder 
    def boxVal(boxId, filepath=None):
        if filepath == None:
            inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId)) 
    #       sys.stdout.write(str(inputBox[0].getValue()))
            sys.stdout.write(str(inputBox[0].getValue()))
        else:
            value = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))[0].getValue()
            sys.stdout.write(str(value))
            f = open(filepath, "w")
            f.write(str(value))
            f.close()

    if len(args) == 2:
        boxVal(args[1])
        exit()
    elif len(args) >= 3:
        boxVal(args[1], filepath=args[2])
        exit()
    else:
        print("enter boxId , filepath (optional), password (optional) as argument")

