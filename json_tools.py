import os, json
from file_tools import *
def keyVal_list_update(keyValList, jsonPath):
#    if type(keyValList) is not type(list):
#        print("type(keyValList) is not type(list)")
#        return False
    try:
        j = json.loads(str(clean_file_open(jsonPath, "r")))
        for keyVal in keyValList:
            j.update(keyVal)
    except ValueError as e:
        print("Invalid Json")
       
def json_to_keyValList(jsonPath):
    keyValList = []
    try: 
        j = json.loads(clean_file_open(jsonPath, "r"))
        for key in j:
            keyValList.append({key:j[key]})
        return keyValList
    except ValueError as e:
        print("Invalid Json")

