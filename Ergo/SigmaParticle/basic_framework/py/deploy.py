import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
password = ""
if len(args) > 1: #collect a potential password from args
    if args[1] == "deposit":
        if len(args) > 2:
            if args[2] == "verifyTreeOnly":
                if len(args) > 3:
                    password = args[3]
            else:
                password = args[2]
    elif args[1] == "claim":
        if len(args) > 2:
            password = args[2]
    elif args[1] == "refund":
        if len(args) > 2:
            password = args[2]

from connect import *
ergo, wallet_mnemonic, mnemonic_password, senderAddress= connect(password=password) #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress, args)

from cleanup import *
cleanup()


