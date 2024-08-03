import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
password = ""
print(len(args))
print(args)

if args[1] == "deposit":
    if len(args) >= 3:
        if args[2] == "verifyTreeOnly":
            if len(args) == 4:
                password = args[3]
        else:
            if len(args) == 3:
                password = args[2]
elif args[1] == "claim":
    if len(args) == 3:
        password = args[2]
elif args[1] == "refund":
    if len(args) == 3:
        password = args[2]



from connect import *
ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret = connect(password=password) #dotenv loaded here dont call env vars before

try:
    getattr(__import__("main"), "main")\
            (os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret, args)
except(BrokenPipeError, IOError):
#    print ('BrokenPipeError caught', file = sys.stderr)
    pass

from cleanup import *
cleanup()


