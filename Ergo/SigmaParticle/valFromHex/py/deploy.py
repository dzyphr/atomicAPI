import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

password = ""
if len(args) >= 2:
    if len(args) >= 3:
        if len(args) == 4:
            password = args[3]


# Create connection to the blockchain #exported to connect.py
from connect import *
ergo, wallet_mnemonic, mnemonic_password, senderAddress= connect(password=password) #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress, args)

from cleanup import *
cleanup()


