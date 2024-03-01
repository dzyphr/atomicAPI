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
    if os.path.isfile(accepted_keys_filepath) == True:
        contents = file_tools.clean_file_open(accepted_keys_filepath, "r")
        obj = json.loads(contents)
        index = len(obj)
        updatelist = [{index:key}]
        json_tools.keyVal_list_update(updatelist, accepted_keys_filepath)
    else:
        file_tools.clean_file_open(accepted_keys_filepath, "w", "{}")
        updatelist = [{0:key}]
        json_tools.keyVal_list_update(updatelist, accepted_keys_filepath)


