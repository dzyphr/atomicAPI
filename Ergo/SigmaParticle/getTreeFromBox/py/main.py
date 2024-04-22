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
import requests, json
def main(contractName, nodeurl, nodeAPIKey, args):
#    org.slf4j.impl.StaticLoggerBinder 
    def treeFromBox(boxId, filepath=None):
        def REST_getbox(nodeurl, nodeAPIKey, boxId):
            url = nodeurl + "utxo/byId/"
#            print(url + boxId)
            headers = {\
                "accept": 'application/json',\
                "Content-type": 'application/json',\
                "api_key": nodeAPIKey
            }
            data = str(boxId)
            try:
#                response = requests.post(url, headers=headers, data=data).text
                response = requests.get(url + boxId).text
                return response
            except Exception as err:
                print("error getting box by Id: ", boxId, "\nerror: ", err)


        if filepath == None:
#            inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId)) 
            inputbox = REST_getbox(nodeurl, nodeAPIKey, boxId)
            if "ergoTree" in json.loads(inputbox):
                sys.stdout.write(json.loads(inputbox)["ergoTree"])
            else:
                sys.stdout.write("404")
#           sys.stdout.write(str(inputBox[0].getErgoTree().bytesHex()))
#            print(dir(inputBox[0].getErgoTree().bytesHex()))
        else:
#            inputBox = java.util.Arrays.asList(ergo._ctx.getBoxesById(boxId))
#            tree = inputBox[0].getErgoTree().bytesHex()
            inputbox = REST_getbox(nodeurl, nodeAPIKey, boxId)
            if "ergoTree" in json.loads(inputbox):
#                print(inputbox)
                tree =  json.loads(inputbox)["ergoTree"]
    #            print(tree)
                f = open(filepath, "w")
                f.write(str(tree))
                f.close()
    #            sys.stdout.write(str(inputBox[0].getErgoTree().bytesHex()))
                sys.stdout.write(tree)
            else:
                sys.stdout.write("NotFound")

    if len(args) > 1:
        if len(args) > 2:
            treeFromBox(args[1], args[2])
            exit()
        treeFromBox(args[1])
        exit()

    else:
        print("enter boxId as argument")

