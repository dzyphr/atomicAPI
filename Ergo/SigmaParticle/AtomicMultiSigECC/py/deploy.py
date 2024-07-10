import sys, os, signal

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
from connect import *
#ergo, wallet_mnemonic, mnemonic_password, senderAddress= connect() #dotenv loaded here dont call env vars before
connect()
from main import *
#main(os.getenv('ContractName'), ergo, wallet_mnemonic, mnemonic_password, senderAddress, args)


def sigHandle(sig, frame):
    os._exit(0)
    
signal.signal(signal.SIGTERM, sigHandle)
signal.signal(signal.SIGINT, sigHandle)

try:
    main(args)
except(BrokenPipeError, IOError):
#    print ('BrokenPipeError caught', file = sys.stderr)
    pass



from cleanup import *
cleanup()


