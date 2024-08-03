import json
import logging
import os
from dotenv import load_dotenv
load_dotenv()
from dotenv import dotenv_values
import sys 
import file_tools
from passwordFileEncryption import get_val_from_envdata_key, decrypt_file_return_contents
if bool(os.getenv('localErgpy')) == True:
    sys.path.insert(0, '../ergpy/ergpy') #prefer local version
from ergpy import appkit, helper_functions

def connect(password=""):
    '''
    log = f"Current Working Directory: {os.getcwd()}\n"
    log += f"Script Directory: {os.path.dirname(os.path.realpath(__file__))}\n"

    # Resolve absolute path for .env file
    script_dir = os.path.dirname(os.path.realpath(__file__))
#    contractdir = os.path.join(script_dir, "Ergo/SigmaParticle/")
    script_dir = script_dir[script_dir.find("Ergo"):]
    env_path = os.path.join(script_dir.replace("py", ""), '.env')
 #   log += f"Target Directory: {contractdir}\n"
    log += f".env Path: {env_path}\n"

    # Load environment variables
    if os.path.isfile(env_path):
        loadedenv = dotenv_values(env_path)
        os.environ.update(loadedenv)
        log += "Environment variables loaded."
    else:
        log += f".env file not found at: {env_path}"

    file_tools.clean_file_open("testpyo3envs", "w", log)
    '''
    if password == "":
        load_dotenv()
        node_url = os.getenv('testnetNode') # MainNet or TestNet
        api_url = os.getenv('apiURL')
        ergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
        wallet_mnemonic = os.getenv('mnemonic')
        mnemonic_password = os.getenv('mnemonicPass')
        senderEIP3Secret = os.getenv('senderEIP3Secret')
        if mnemonic_password != "":
            usingMnemonicPass = True
        else:
            usingMnemonicPass = False

        if usingMnemonicPass == True:
            #WITH MNEMONIC PASSWORD
            senderAddress = helper_functions.get_wallet_address(ergo=ergo, amount=1, wallet_mnemonic=wallet_mnemonic, mnemonic_password=mnemonic_password)
        else:
            #WITHOUT MNEMONIC PASSWORD
            senderAddress = helper_functions.get_wallet_address(ergo=ergo, amount=1, wallet_mnemonic=wallet_mnemonic)
        return ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret
    else:
        envdata = decrypt_file_return_contents(".env.encrypted", password)
        node_url = get_val_from_envdata_key('testnetNode', envdata).strip('\"')
        api_url = get_val_from_envdata_key("apiURL", envdata).strip('\"')
        wallet_mnemonic = get_val_from_envdata_key('mnemonic', envdata).strip('\"')
        mnemonic_password = get_val_from_envdata_key('mnemonicPass', envdata).strip('\"')
        senderEIP3Secret = get_val_from_envdata_key('senderEIP3Secret', envdata).strip('\"')
        ergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
        if mnemonic_password != "":
            usingMnemonicPass = True
        else:
            usingMnemonicPass = False

        if usingMnemonicPass == True:
            #WITH MNEMONIC PASSWORD
            senderAddress = helper_functions.get_wallet_address(ergo=ergo, amount=1, wallet_mnemonic=wallet_mnemonic, mnemonic_password=mnemonic_password)
        else:
            senderAddress = helper_functions.get_wallet_address(ergo=ergo, amount=1, wallet_mnemonic=wallet_mnemonic)

        return ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret
