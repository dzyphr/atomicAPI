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
def height(ergo):
    height = str(ergo._ctx.getHeight())
    sys.stdout.write(str(height))
    return height

def height_filepath(ergo, filepath):
    height = str(ergo._ctx.getHeight())
    f = open(filepath, "w")
    f.write(height)
    f.close()
    print(height)
    return height

def main(contractName, ergo, args):
    
    def height():
        sys.stdout.write(str(ergo._ctx.getHeight()))

    def height_filepath(filepath):
        height = str(ergo._ctx.getHeight())
        f = open(filepath, "w")
        f.write(height)
        f.close()
        print(height)



    if len(args) > 1:
        height_filepath(args[1])
    else:
        height()
