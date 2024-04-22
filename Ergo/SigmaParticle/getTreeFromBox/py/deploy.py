import sys

args = sys.argv

# Logging utility #exported to loggingFmt.py
from loggingFmt import *
loggingFmt()

# Create connection to the blockchain #exported to connect.py
password = ""
if len(args) == 4:
    password = args[3]

from connect import *
node_url, nodeAPIKey = connect(password=password) #dotenv loaded here dont call env vars before

from main import *
main(os.getenv('ContractName'), node_url, nodeAPIKey,  args)

from cleanup import *
cleanup()


