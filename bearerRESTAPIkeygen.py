import secrets
import string
import file_tools
import json_tools
import os
import json

def generate_bearer_RESTAPI_key(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def add_RESTAPI_key_to_private_accepted_keys_JSON(key):
    accepted_keys_filepath = "accepted_private_api_keys.json"
    return json_tools.createOrUpdateIndexedJSONPath(accepted_keys_filepath, key)

def starterAPIKeys(APIkey):

    starterAPIKeysPath = "starterAPIKeys.json"
    return json_tools.createOrUpdateIndexedJSONPath(starterAPIKeysPath, APIkey)


