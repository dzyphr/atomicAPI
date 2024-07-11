import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
#print("args:", args)
#print(len(args))
password = ""
if len(args) >= 3:
    if len(args) >= 4:
        if len(args) == 5:
            password = args[4]
    else:
        txBoxFilter(args[1], args[2])
        exit()


from connect import *
ergo = connect(password=password) #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), ergo, args)

from cleanup import *
cleanup()


