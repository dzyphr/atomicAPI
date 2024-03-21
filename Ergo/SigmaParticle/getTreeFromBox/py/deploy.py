import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
password = ""
if len(args) > 1:
        if len(args) > 3:
            password = args[3]

from connect import *
ergo, wallet_mnemonic, mnemonic_password, senderAddress= connect(password=password) #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress, args)

from cleanup import *
cleanup()


