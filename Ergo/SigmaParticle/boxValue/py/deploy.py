import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()


password = ""
if len(args) == 4:
    password = args[3]

# Create connection to the blockchain #exported to connect.py
from connect import *
ergo  = connect(password=password) #dotenv loaded here dont call env vars befor

from main import *
main(os.getenv('ContractName'), ergo, args)

from cleanup import *
cleanup()


