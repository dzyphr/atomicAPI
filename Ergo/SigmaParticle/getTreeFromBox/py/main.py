import sys
import file_tools
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
import requests, json

def treeFromBox(nodeurl, boxId, filepath=None):
    def REST_getbox(nodeurl, boxId):
        url = nodeurl + "utxo/byId/"
        headers = {\
            "accept": 'application/json',\
            "Content-type": 'application/json'
        }
        data = str(boxId)
        try:
            response = requests.get(url + boxId).text
            return response
        except Exception as err:
            print("error getting box by Id: ", boxId, "\nerror: ", err)


    if filepath == None:
        inputbox = REST_getbox(nodeurl, boxId)
        if "ergoTree" in json.loads(inputbox):
#            sys.stdout.write(json.loads(inputbox)["ergoTree"])
            return json.loads(inputbox)["ergoTree"]
        else:
            return "404"
#            sys.stdout.write("404")
    else:
        inputbox = REST_getbox(nodeurl, boxId)
        if "ergoTree" in json.loads(inputbox):
            tree =  json.loads(inputbox)["ergoTree"]
            file_tools.clean_file_open(filepath, "w", tree)
#            sys.stdout.write(tree)
            return tree
        else:
            return "404"
#            sys.stdout.write("NotFound")

def main(contractName, nodeurl, args):
    def treeFromBox(boxId, filepath=None):
        def REST_getbox(nodeurl, boxId):
            url = nodeurl + "utxo/byId/"
            headers = {\
                "accept": 'application/json',\
                "Content-type": 'application/json'
            }
            data = str(boxId)
            try:
                response = requests.get(url + boxId).text
                return response
            except Exception as err:
                print("error getting box by Id: ", boxId, "\nerror: ", err)


        if filepath == None:
            inputbox = REST_getbox(nodeurl, boxId)
            if "ergoTree" in json.loads(inputbox):
                sys.stdout.write(json.loads(inputbox)["ergoTree"])
            else:
                sys.stdout.write("404")
        else:
            inputbox = REST_getbox(nodeurl, boxId)
            if "ergoTree" in json.loads(inputbox):
                tree =  json.loads(inputbox)["ergoTree"]
                file_tools.clean_file_open(filepath, "w", tree)
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

