import sys
sys.path.append('Ergo/SigmaParticle/treeToAddr/py/')
import json
import requests
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
import coinSelection
import scalaPipe
from passwordFileEncryption import get_val_from_envdata_key, decrypt_file_return_contents

def treeToAddr(node_url, tree, filepath=None, password=""):
    '''
    node = ""
    if password == "":
        node = os.getenv('testnetNode')          
    else:
        envdata = decrypt_file_return_contents(".env.encrypted", password)
        node = get_val_from_envdata_key('testnetNode', envdata).strip('\"')
    '''
    url = node_url  + "utils/ergoTreeToAddress"
    headers = {\
        "accept": 'application/json',\
        "Content-type": 'application/json'
#        "api_key": testnetAPIKey
    }
    if tree.startswith("\"") == False:
        tree = "\"" + tree
    if tree.endswith("\"") == False:
        tree = tree + "\""
    data = str(tree)
    try:
        response = requests.post(url, headers=headers, data=data).text
        if filepath != None:
            f = open(filepath, "w")
            addr = json.loads(response)["address"]
            f.write(addr)
            f.close()
#            print(response)
            return response
        else:
            print(response)
            return response
    except Exception as err:
        #print("error getting address for: ", tree, "\nerror: ", err)
        pass

def main(contractName, node_url, args):
    
    def treeToAddr(tree, filepath=None, password=""):
        '''
        node = ""
        if password == "":
            node = os.getenv('testnetNode')          
        else:
            envdata = decrypt_file_return_contents(".env.encrypted", password)
            node = get_val_from_envdata_key('testnetNode', envdata).strip('\"')
        '''
        url = node_url  + "utils/ergoTreeToAddress"
        headers = {\
            "accept": 'application/json',\
            "Content-type": 'application/json'
#            "api_key": testnetAPIKey
        }
        if tree.startswith("\"") == False:
            tree = "\"" + tree
        if tree.endswith("\"") == False:
            tree = tree + "\""
        data = str(tree)
        try:
            response = requests.post(url, headers=headers, data=data).text
            if filepath != None:
                f = open(filepath, "w")
                addr = json.loads(response)["address"]
                f.write(addr)
                f.close()
                print(response)
            else:
                print(response)
        except Exception as err:
            print("error getting address for: ", tree, "\nerror: ", err)


    if len(args) == 2:
        treeToAddr(args[1])
        exit()
    if len(args) == 3:
        treeToAddr(args[1], filepath=args[2])
        exit()
    if len(args) == 4:
        treeToAddr(args[1], filepath=args[2], password=args[3])
        exit()
    else:
        print("enter tree [optional: filepath] as argument")
