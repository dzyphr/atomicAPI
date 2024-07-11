import json
import logging
import os
from dotenv import load_dotenv
load_dotenv()
import sys 
from passwordFileEncryption import get_val_from_envdata_key, decrypt_file_return_contents
if bool(os.getenv('localErgpy')) == True:
    sys.path.insert(0, '../ergpy/ergpy') #prefer local version
from ergpy import appkit, helper_functions
def connect(password=""):
    if password == "":
        load_dotenv()
        node_url = os.getenv('testnetNode') # MainNet or TestNet
        api_url = os.getenv('apiURL')
        ergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
        wallet_mnemonic = os.getenv('mnemonic')
        mnemonic_password = os.getenv('mnemonicPass')
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
    else:
        envdata = decrypt_file_return_contents(".env.encrypted", password)
        node_url = get_val_from_envdata_key('testnetNode', envdata).strip('\"')
        api_url = get_val_from_envdata_key("apiURL", envdata).strip('\"')
        wallet_mnemonic = get_val_from_envdata_key('mnemonic', envdata).strip('\"')
        mnemonic_password = get_val_from_envdata_key('mnemonicPass', envdata).strip('\"')
        
        ergo = appkit.ErgoAppKit(node_url=node_url, api_url=api_url)
        if mnemonic_password != "":
            usingMnemonicPass = True
        else:
            usingMnemonicPass = False

        if usingMnemonicPass == True:
            #WITH MNEMONIC PASSWORD
            senderAddress = helper_functions.get_wallet_address(ergo=ergo, amount=1, wallet_mnemonic=wallet_mnemonic, mnemonic_password=mnemonic_password)

    return ergo
