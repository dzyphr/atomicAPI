import sys
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
#import coinSelection
#import scalaPipe
import file_tools

def txBoxFilter(ergo, address, boxId, filepath=None):
    node = ergo._node_url
    url = node  + "blockchain/transaction/byAddress"
    params = {\
            "limit": 5,\
            "offset": 0\
    }
    headers = {\
        "accept": 'application/json',\
        "Content-type": 'application/json',\
    }
    data = str(address)
    response = requests.post(url, params=params, headers=headers, data=data).text
    j = json.loads(response)
    newBoxes = []
    newTxs = []
    for tx in j["items"]:
        if tx["outputs"][0]["boxId"] != boxId:
            newBoxes.append(tx["outputs"][0]["boxId"])
            newTxs.append(tx)
    ext = "_tx"
    i = 1
    for tx in newTxs:
        if filepath == None:
            print(json.dumps(tx, indent=2))
            return json.dumps(tx, indent=2)
        else:
            #f = open(filepath + ext + str(i), "w")
            #f.write(str(json.dumps(tx, indent=2)))
            #f.close()
            file_tools.clean_file_open(filepath + ext + str(i), "w", str(json.dumps(tx, indent=2)))
            return json.dumps(tx, indent=2) #TODO this could find more but for now just one for claim txs does the job
#            i = i + 1
    #        print(json.dumps(tx, indent=2))

def main(contractName, ergo, args):
    def txBoxFilter(address, boxId, filepath=None):
        node = ergo._node_url  
        url = node  + "blockchain/transaction/byAddress"
        params = {\
                "limit": 5,\
                "offset": 0\
        }
        headers = {\
            "accept": 'application/json',\
            "Content-type": 'application/json',\
        }
        data = str(address)
        response = requests.post(url, params=params, headers=headers, data=data).text
        j = json.loads(response)
        newBoxes = []
        newTxs = []
        for tx in j["items"]:
            if tx["outputs"][0]["boxId"] != boxId:
                newBoxes.append(tx["outputs"][0]["boxId"])
                newTxs.append(tx)
        ext = "_tx"
        i = 1
        for tx in newTxs:
            if filepath == None:
                print(json.dumps(tx, indent=2))
            else:
                #f = open(filepath + ext + str(i), "w")
                #f.write(str(json.dumps(tx, indent=2)))
                #f.close()
                file_tools.clean_file_open(filepath + ext + str(i), "w", str(json.dumps(tx, indent=2)))
                i = i + 1
        #        print(json.dumps(tx, indent=2)) 

    if len(args) >= 3:
        if len(args) >= 4:
            txBoxFilter(args[1], args[2], filepath=args[3])
            exit()
        txBoxFilter(args[1], args[2])
        exit()
    else:
        print("enter address, boxId, [optional: filepath] as argument")
