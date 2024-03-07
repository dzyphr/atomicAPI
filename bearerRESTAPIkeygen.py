import secrets
import string
import file_tools
import json_tools
import os
import json

def generate_bearer_RESTAPI_key(length=64): #length is modular higher is more secure against brute force
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def add_RESTAPI_key_to_private_accepted_keys_JSON(key):#PRIVATE accepted key list
    accepted_keys_filepath = "accepted_private_api_keys.json"
    return json_tools.createOrUpdateIndexedJSONPath(accepted_keys_filepath, key)

def add_RESTAPI_key_to_public_accepted_keys_JSON(key):#PUBLIC accepted key list
    accepted_keys_filepath = "accepted_public_api_keys.json"
    return json_tools.createOrUpdateIndexedJSONPath(accepted_keys_filepath, key)


def starterAPIKeys(APIkey):#might be defunct in future releases
    starterAPIKeysPath = "starterAPIKeys.json" #list used to simplify key setup for public networked REST API calls
    return json_tools.createOrUpdateIndexedJSONPath(starterAPIKeysPath, APIkey)


