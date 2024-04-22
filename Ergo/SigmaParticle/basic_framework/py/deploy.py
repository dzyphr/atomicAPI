import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
password = ""
print(len(args))
print(args)
if len(args) == 4:
    password = args[3]
if len(args) == 3:
    password = args[2]

from connect import *
ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret = connect(password=password) #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret, args)

from cleanup import *
cleanup()


