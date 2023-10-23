import sys
import json
import shutil
import configparser
from initiatorInterface import *
from responderInterface import *
from ElGamalInterface import *
from AtomicityInterface import *
from SigmaParticleInterface import *
from functional_tests import *
import json_tools
import time
import file_tools
args = sys.argv

def firstRunCheck():
    userjsonpath = "user.json"
    if os.path.isfile(userjsonpath) == False:
        userjson = \
        {
            "Chains": {
                "Ergo": "True",
                "Sepolia": "True"
            }
        }
        clean_file_open(userjsonpath, "w", json.dumps(userjson, indent=4))
    ChainsList = json.loads(clean_file_open(userjsonpath, "r"))["Chains"]
    for chain in ChainsList:
        if ChainsList[chain] == "True":
            initializeAccount("basic_framework", chain)
            chain_framework_path = ""
            if chain == "Ergo":
                chain_framework_path = "Ergo/SigmaParticle/"
            if chain == "Sepolia":
                chain_framework_path = "EVM/Atomicity/"
            for dirs in os.listdir(chain_framework_path):
                if os.path.isdir(chain_framework_path + dirs):
                    if ".env" not in os.listdir(chain_framework_path + dirs):
                        cmd = "cp " + chain_framework_path + "basic_framework/.env " + chain_framework_path + dirs + "/.env"
                        os.popen(cmd).read()


def initializeAccount(accountName, chain): #interactive command line function to setup .env files
    implemented_chains = ["Ergo", "Sepolia"]
    chain_framework_path = ""
    def create(fulldirpath, fullenvpath, envFormat):
        if file_tools.clean_mkdir(fulldirpath) == False:
            if os.path.isfile(fullenvpath):
                while True:
                    print("A(n)", chain, "Account named ", accountName, "was already found, overwrite?") #we added an upfront check for this, should we double check?
                    yn = input()
                    if yn == "y":
                        clean_file_open(fullenvpath, "w", envFormat)
                        print("Account: ", accountName, " created!")
                        return False
                    if yn == "n": #add a rename option here to make this ux more useful
                        print("aborting")
                        return False
                    else:
                        print("unknown: ", yn)
                        continue
            else:
                clean_file_open(fullenvpath, "w", envFormat)
                print(chain, "Account: ", accountName, " created!")
                return True

        else:
            clean_file_open(fullenvpath, "w", envFormat)
            print(chain, "Account: ", accountName, " created!")
            return True

    if chain in implemented_chains:
        if chain == "Ergo":
            chain_framework_path = "Ergo/SigmaParticle/"
            fulldirpath = chain_framework_path + accountName
            fullenvpath = fulldirpath + "/.env"
            if os.path.isfile(fullenvpath):
                while True:
                    print("A(n)", chain, "Account named ", accountName, "was already found, overwrite?") #we added an upfront check for this, should we double check?
                    yn = input()
                    if yn == "n":
                        return False
                    if yn == "y":
                        break
                    else:
                        print("unknown response: ", yn)
                        continue
            print("Chain chosen:", chain, "\nAccount Name chosen:", accountName)
            print("Setting up .env file which will include typing in private data, \n" +
                    "You may disconnect internet while doing this if concerned about any connected applications.")
            print("Enter the URL address of the ", chain, " node you want to connect to. (May be testnet or mainnet):")
            testnetNode = input()
            print("(REMINDER: You may disconnect internet while doing this if concerned about any connected applications.)", \
                    "\nEnter your Ergo private mnemonic seed words:")
            mnemonic = input()
            print("Enter your Ergo mnemonic password:")
            mnemonicPass = input()
            print("Enter your EIP3 Secret:")
            senderEIP3Secret = input()
            print("Enter your Ergo PubKey:")
            senderPubKey = input()
            print("Enter your explorer api URL (default: https://tn-ergo-explorer.anetabtc.io/)")
            apiURL = input()

            envFormat = \
                "[default]\n" +\
                "testnetNode=\"" + testnetNode + "\"\n" +\
                "mnemonic=\"" + mnemonic + "\"\n" +\
                "mnemonicPass=\"" + mnemonicPass + "\"\n" +\
                "senderEIP3Secret=" + senderEIP3Secret + "\n" +\
                "senderPubKey=\"" + senderPubKey + "\"\n" +\
                "apiURL=\"" + apiURL + "\"\n"

            create(fulldirpath, fullenvpath, envFormat)


        elif chain == "Sepolia":
            chain_framework_path = "EVM/Atomicity/"
            fulldirpath = chain_framework_path + accountName
            fullenvpath = fulldirpath + "/.env"
            if os.path.isfile(fullenvpath):
                while True:
                    print("A(n)", chain, "Account named ", accountName, "was already found, overwrite?") #we added an upfront check for this, should we double check?
                    yn = input()
                    if yn == "n":
                        return False
                    if yn == "y":
                        break
                    else:
                        print("unknown response: ", yn)
                        continue
            print("Chain chosen:", chain, "\nAccount Name chosen:", accountName)
            print("Setting up .env file which will include typing in private data, \n" +
                    "You may disconnect internet while doing this if concerned about any connected applications.")
            print("Enter the Public " + chain +" Address that you wish to add:")
            SepoliaSenderAddr = input()
            print("(REMINDER: You may disconnect internet while doing this if concerned about any connected applications.)")
            print("Enter the Private Key of this address:")
            SepoliaPrivKey = input()
            print("Enter the RPC URL address you wish to submit your transactions to:")
            Sepolia = input()
            SepoliaID = "11155111" #chain id
            SepoliaScan = "https://api-sepolia.etherscan.io/api" #block explorer
            SolidityCompilerVersion = "0.8.0" #solidity version
            #EtherscanAPIKey = input() #contract verification stuff goes here if we need it

            envFormat = \
                "[default]\n" +\
                "SepoliaSenderAddr=\"" + SepoliaSenderAddr + "\"\n" + \
                "SepoliaPrivKey=\"" + SepoliaPrivKey + "\"\n"  + \
                "Sepolia=\"" + Sepolia + "\"\n" + \
                "SepoliaID=\"" + SepoliaID + "\"\n" + \
                "SepoliaScan=\"" + SepoliaScan + "\"\n" + \
                "SolidityCompilerVersion=\"" + SolidityCompilerVersion + "\"\n"

            create(fulldirpath, fullenvpath, envFormat)


    else:
        print(chain, " is not currently implemented into this framework")

