import sys
import os
import json
import shutil
import configparser
import json_tools
import time
import file_tools
from bearerRESTAPIkeygen import generate_bearer_RESTAPI_key, add_RESTAPI_key_to_private_accepted_keys_JSON
from dotenv import dotenv_values, set_key
args = sys.argv

def updateMainEnv(Key, Val):
#    env_content = dotenv_values('.env')
    return set_key('.env', Key, Val, quote_mode='never')

def valFromConf(confPath, val):
    confParser = configparser.ConfigParser()
    confParser.read(confPath)
    return confParser['default'][val]


def firstRunCheck():
    userjsonpath = "user.json"
    add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if os.path.isfile(userjsonpath) == False:
        userjson = \
        {
            "Chains": {
                "Ergo": "True",
                "Sepolia": "True"
            }
        }
        file_tools.clean_file_open(userjsonpath, "w", json.dumps(userjson, indent=4))
    ChainsList = json.loads(file_tools.clean_file_open(userjsonpath, "r"))["Chains"]
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



def initSepoliaAccountNonInteractive(\
        SepoliaSenderAddr, SepoliaPrivKey, Sepolia, SepoliaID, SepoliaScan, 
        SolidityCompilerVersion, fulldirpath, fullenvpath, enc=False, password=""):
    envFormat = \
        "[default]\n" +\
        "SepoliaSenderAddr=\"" + SepoliaSenderAddr + "\"\n" + \
        "SepoliaPrivKey=\"" + SepoliaPrivKey + "\"\n"  + \
        "Sepolia=\"" + Sepolia + "\"\n" + \
        "SepoliaID=\"" + SepoliaID + "\"\n" + \
        "SepoliaScan=\"" + SepoliaScan + "\"\n" + \
        "SolidityCompilerVersion=\"" + SolidityCompilerVersion + "\"\n"

    def create(fulldirpath, fullenvpath, envFormat):
        if enc == False:
            if file_tools.clean_mkdir(fulldirpath) == True:
                if os.path.isfile(fullenvpath):
                    print("Unhandled Edge Case: duplicate .env path found,  aborting")
                    return False
                else:
                    file_tools.clean_file_open(fullenvpath, "w", envFormat)
                    return True
        else:
            if password == "":
                print("PROVIDE PASSWORD WHEN ENCRYPTING ENV FILE")
                return False
            else:
                file_tools.clean_file_open(fullenvpath, "w", envFormat)
                encrypt_file(fullenvpath, password, delete=True)
                return True


    create(fulldirpath, fullenvpath, envFormat)


def initErgoAccountNonInteractive(testnetNode, mnemonic, mnemonicPass, senderEIP3Secret, senderPubKey, 
        apiURL, fulldirpath, fullenvpath, enc=False, password=""):
    envFormat = \
                "[default]\n" +\
                "testnetNode=\"" + testnetNode + "\"\n" +\
                "mnemonic=\"" + mnemonic + "\"\n" +\
                "mnemonicPass=\"" + mnemonicPass + "\"\n" +\
                "senderEIP3Secret=" + senderEIP3Secret + "\n" +\
                "senderPubKey=\"" + senderPubKey + "\"\n" +\
                "apiURL=\"" + apiURL + "\"\n"

    def create(fulldirpath, fullenvpath, envFormat):
        if file_tools.clean_mkdir(fulldirpath) == True:
            if os.path.isfile(fullenvpath):
                print("Unhandled Edge Case: duplicate .env path found,  aborting")
                return False
            else:
                file_tools.clean_file_open(fullenvpath, "w", envFormat)
                return True
        else:
            if password == "":
                print("PROVIDE PASSWORD WHEN ENCRYPTING ENV FILE")
                return False
            else:
                file_tools.clean_file_open(fullenvpath, "w", envFormat)
                encrypt_file(fullenvpath, password, delete=True)
                return True

    create(fulldirpath, fullenvpath, envFormat)

def initializeAccount(accountName, chain): #interactive command line function to setup .env files
    implemented_chains = ["Ergo", "Sepolia"]
    chain_framework_path = ""
    def create(fulldirpath, fullenvpath, envFormat, enc=False, password=""):
        if file_tools.clean_mkdir(fulldirpath) == False:
            if os.path.isfile(fullenvpath):
                while True:
                    print("A(n)", chain, "Account named ", accountName, "was already found, overwrite?") #we added an upfront check for this, should we double check?
                    yn = input()
                    if yn == "y":
                        if enc == False:
                            file_tools.clean_file_open(fullenvpath, "w", envFormat)
                            print("Account: ", accountName, " created!")
                            return True
                        else:
                            if password == "":
                                print("PROVIDE PASSWORD WHEN ENCRYPTING ENV FILE")
                            else:
                                file_tools.clean_file_open(fullenvpath, "w", envFormat)
                                encrypt_file(fullenvpath, password, delete=True)
                                print(chain, "Account: ", accountName, " created!")
                                return True
                    if yn == "n": #add a rename option here to make this ux more useful
                        print("aborting")
                        return False
                    else:
                        print("unknown: ", yn)
                        continue
            else:
                if enc == False:
                    file_tools.clean_file_open(fullenvpath, "w", envFormat)
                    print(chain, "Account: ", accountName, " created!")
                    return True
                else:
                    if password == "":
                        print("PROVIDE PASSWORD WHEN ENCRYPTING ENV FILE")
                    else:
                        file_tools.clean_file_open(fullenvpath, "w", envFormat)
                        encrypt_file(fullenvpath, password, delete=True)
                        print(chain, "Account: ", accountName, " created!")
                        return True

        else:
            if enc == False:
                file_tools.clean_file_open(fullenvpath, "w", envFormat)
                print(chain, "Account: ", accountName, " created!")
                return True
            else:
                if password == "":
                    print("PROVIDE PASSWORD WHEN ENCRYPTING ENV FILE")
                else:
                    file_tools.clean_file_open(fullenvpath, "w", envFormat)
                    encrypt_file(fullenvpath, password, delete=True)
                    print(chain, "Account: ", accountName, " created!")
                    return True

    def enc_env_loop(fulldirpath, fullenvpath, envFormat):
        while True:
            print("Password encrypt account file? y or n (experimental)")
            yn = input()
            if yn == "y":
                enc = True
                while True:
                    print("enter password to encrypt file with")
                    password = input()
                    if password == "":
                        print("password cannot be blank")
                        continue
                    else:
                        print("password used: ", password, "\n Ok?")
                        yn = input()
                        while True:
                            if yn == "y":
                                print("\n This WILL NOT be saved anywhere for you.\n" + \
                                    "Make sure you remember or save this password somewhere safe that you can always access.\n" + \
                                    "If you lose access to the password you will need to create another account.\n" + \
                                    "You can ofcourse reupload the same private keys but are solely responsible for\n" + \
                                    "maintaining proper custody of these keys outside of this application.\n" +\
                                    "basically please do not password encrypt keys you havent taken proper custody of")
                                #enc here
                                create(fulldirpath, fullenvpath, envFormat, enc=True, password=password)
                            if yn == "n":
                                break
                            else:
                                continue
            elif yn == "n":
                create(fulldirpath, fullenvpath, envFormat)
            else:
                continue

    if chain in implemented_chains:
        if chain == "Ergo":
            chain_framework_path = "Ergo/SigmaParticle/"
            fulldirpath = chain_framework_path + accountName
            fullenvpath = fulldirpath + "/.env"
            if os.path.isfile(fullenvpath):
                while True:
                    print("A(n)", chain, "Account named ", accountName, "was already found, overwrite?") 
                    #we added an upfront check for this, should we double check?
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

            enc = False
            enc_env_loop(fulldirpath, fullenvpath, envFormat)



        elif chain == "Sepolia":
            chain_framework_path = "EVM/Atomicity/"
            fulldirpath = chain_framework_path + accountName
            fullenvpath = fulldirpath + "/.env"
            if os.path.isfile(fullenvpath):
                while True:
                    print("A(n)", chain, "Account named ", accountName, "was already found, overwrite?") 
                    #we added an upfront check for this, should we double check?
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
            print("Encrypt file? y or n (experimental)")
            yn = input()
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

            enc_env_loop(fulldirpath, fullenvpath, envFormat)
    else:
        print(chain, " is not currently implemented into this framework")

