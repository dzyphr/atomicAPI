import sys
import os
import json
import shutil
import configparser
import json_tools
import time
import uuid
import file_tools
import passwordFileEncryption
from passwordFileEncryption import encrypt_file
from bearerRESTAPIkeygen import generate_bearer_RESTAPI_key, add_RESTAPI_key_to_private_accepted_keys_JSON
from dotenv import dotenv_values, set_key
args = sys.argv

def updateMainEnv(Key, Val):
    return set_key('.env', Key, Val, quote_mode='never')

def valFromConf(confPath, val):
    confParser = configparser.ConfigParser()
    confParser.read(confPath)
    return confParser['default'][val]

def compareListsFindOutliers(actual, expected):
    actualSet = set(actual)
    expectedSet = set(expected)
    actualOutliers = actualSet - expectedSet
    expectedOutliers = expectedSet - actualSet
    return list(actualOutliers), list(expectedOutliers)

def is_uuid(string):
    try:
        uuid_obj = uuid.UUID(string, version=4)
        return str(uuid_obj) == string
    except ValueError:
        return False

def remove_uuids_from_list(string_list):
    return [string for string in string_list if not is_uuid(string)]

def is_EVM_swap_dir(dirname):
    if dirname.startswith('Swap_'):
        return True
    else:
        return False

def remove_EVM_swap_dirs_from_list(string_list):
    return [string for string in string_list if not is_EVM_swap_dir(string)]


def firstRunCheck():
    userjsonpath = "user.json"
    add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if os.path.isfile(userjsonpath) == False:
        userjson = \
        {
            "Chains": {
                "TestnetErgo": "True",
                "Sepolia": "True"
            }
        }
        file_tools.clean_file_open(userjsonpath, "w", json.dumps(userjson, indent=4))
    ChainsList = json.loads(file_tools.clean_file_open(userjsonpath, "r"))["Chains"]
    for chain in ChainsList:
        if ChainsList[chain] == "True":
            initializeAccount("basic_framework", chain)
            #look for other accounts
            #if none prompt for first account name
            #initialize that account
            #in initializeAccount() ensure basic_framework accounts don't require private variables like seed phrase
            chain_framework_path = ""
            if chain == "TestnetErgo":
                chain_framework_path = "Ergo/SigmaParticle/"
                ExpectedDirs = [
                    "AtomicMultiSig", "AtomicMultiSigECC", "basic_framework", "boxFilter", "boxValue",
                    "cpp", "getTreeFromBox", "treeToAddr", "boxConstantByIndex",
                    "boxToContract", "currentHeight", "currentHeight", "valFromHex", "testaccountname", "SwapKeyManager"
                ]
                #NOTE testaccountname and other expected folders that aren't always gonna be there should work being added to this check
                #even if they aren't there majority of time in instance they are they wont cause false positive as real account
                #TODO chain specific helper projects should likely be deleted and not used
            if chain == "Sepolia":
                chain_framework_path = "EVM/Atomicity/"
                ExpectedDirs = [
                    "AtomicMultiSigSecp256k1", "AtomicMultiSigSecp256k1_0.0.1", "basic_framework",
                    "cpp", "Goerli", "Sepolia", "solidity-flattener", "testaccountname"
                ]

                #NOTE w current logic this lsit must be updated anytime a helper project dir is added
                #TODO maybe just a system to tag helper files vs real accounts would make it faster and easier
            foundDirs = []
            for dirs in os.listdir(chain_framework_path):
                if os.path.isdir(chain_framework_path + dirs):
                    if os.path.isfile(chain_framework_path + "basic_framework/.env"):
                        if ".env" not in os.listdir(chain_framework_path + dirs):
                            cmd = "cp " + chain_framework_path + "basic_framework/.env " + \
                                    chain_framework_path + dirs + "/.env"
                            os.popen(cmd).read()
                    elif os.path.isfile(chain_framework_path + "basic_framework/.env.encrypted"):
                        if ".env.encrypted" not in os.listdir(chain_framework_path + dirs):
                            cmd = "cp " + chain_framework_path + "basic_framework/.env.encrypted " +\
                                    chain_framework_path + dirs + "/.env.encrypted"
                            os.popen(cmd).read()
                    foundDirs.append(dirs)
            foundDirs =  remove_uuids_from_list(foundDirs)
            #remove any type of UUID file from dirs
            foundDirs = remove_EVM_swap_dirs_from_list(foundDirs)
            #for evm they are formatted as Swap_uuidwithnodashes
            actualOutliers, expectedOutliers = compareListsFindOutliers(foundDirs, ExpectedDirs)
            print("dir outliers(accounts): ", actualOutliers, "expected but not found:", expectedOutliers)
            if len(actualOutliers) == 0: #no accounts created yet so one needs to be created
                while True:
                    print("No", chain, "account created yet. First account name:")
                    accountName = input()
                    print("Name Chosen: ", accountName, ", continue?")
                    yn = input()
                    if yn.upper() == "Y":
                        initializeAccount(accountName, chain)
                        break
                    else:
                        continue



def createNonInteractive(fulldirpath, fullenvpath, envFormat, enc=False, password=""):
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
            if file_tools.clean_mkdir(fulldirpath) == True:
                if os.path.isfile(fullenvpath):
                    print("Unhandled Edge Case: duplicate .env path found,  aborting")
                    return False
                else:
                    file_tools.clean_file_open(fullenvpath, "w", envFormat)
                    encrypt_file(fullenvpath, password, delete=True)
                    return True

def initSepoliaAccountNonInteractive(\
        SepoliaSenderAddr, SepoliaPrivKey, Sepolia, SepoliaID, SepoliaScan, 
        SolidityCompilerVersion, fulldirpath, fullenvpath, enc=False, password=""):
    #TODO get rid of ID scan and compiler version args
    #TODO use hardcoded (fornow) chain frameworkpath instead of fullpaths to build paths on fly w less args
    envFormat = \
        "[default]\n" +\
        "SepoliaSenderAddr=\"" + SepoliaSenderAddr + "\"\n" + \
        "SepoliaPrivKey=\"" + SepoliaPrivKey + "\"\n"  + \
        "Sepolia=\"" + Sepolia + "\"\n" + \
        "SepoliaID=\"" + SepoliaID + "\"\n" + \
        "SepoliaScan=\"" + SepoliaScan + "\"\n" + \
        "SolidityCompilerVersion=\"" + SolidityCompilerVersion + "\"\n"

    createNonInteractive(fulldirpath, fullenvpath, envFormat, enc, password)


def initErgoAccountNonInteractive(testnetNode, mnemonic, mnemonicPass, senderEIP3Secret, senderPubKey, 
        apiURL, fulldirpath, fullenvpath, enc=False, password=""):
    #TODO use hardcoded (fornow) chain frameworkpath instead of fullpaths to build paths on fly w less args
    envFormat = \
        "[default]\n" +\
        "testnetNode=\"" + testnetNode + "\"\n" +\
        "mnemonic=\"" + mnemonic + "\"\n" +\
        "mnemonicPass=\"" + mnemonicPass + "\"\n" +\
        "senderEIP3Secret=" + senderEIP3Secret + "\n" +\
        "senderPubKey=\"" + senderPubKey + "\"\n" +\
        "apiURL=\"" + apiURL + "\"\n"

    createNonInteractive(fulldirpath, fullenvpath, envFormat, enc, password)

def initializeAccount(accountName, chain): #interactive command line function to setup .env files
    implemented_chains = ["TestnetErgo", "Sepolia"]
    chain_framework_path = ""
    #TODO
    #remove sensetive data from basic_framework "accounts"
    #stop treating basic_framework as legit account instead use it as holder for things like rpc urls only
    #ensure an "account" other than basic_framework is created here too
    #can potentially just create the other account first then export the public vars such as rpc url to basic_framework env
    #will improve user accuount log in experience, not forcing users into basic_framework titled account 
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
                                return create(fulldirpath, fullenvpath, envFormat, enc=True, password=password)
                                break
                            if yn == "n":
                                break
                            else:
                                continue
            elif yn == "n":
                return create(fulldirpath, fullenvpath, envFormat)
                break
            else:
                continue

    if chain in implemented_chains:
        if chain == "TestnetErgo":
            chain_framework_path = "Ergo/SigmaParticle/"
            fulldirpath = chain_framework_path + accountName
            fullenvpath = fulldirpath + "/.env"
            fullencenvpath = fulldirpath + "/.env.encrypted"
            if os.path.isfile(fullenvpath) or os.path.isfile(fullencenvpath):
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
            if accountName != "basic_framework":
                print("Chain:", chain, "\nAccount Name chosen:", accountName)
                print("Setting up .env file which will include typing in private data, \n" +
                        "You may disconnect internet while doing this if concerned about any connected applications.")
                print("Enter the URL address of the ", chain, " node you want to connect to.:")
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
                print("Enter your explorer api URL (default: https://testnet.ergoplatform.com/)")
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
            else:
                print("Chain :", chain)
                print("Setting up basic_framework .env file, should only include public data")
                print("Enter the URL address of the ", chain, " node you want to connect to. (May be testnet or mainnet):")
                testnetNode = input()
                print("Enter your explorer api URL (default: https://testnet.ergoplatform.com/)")
                apiURL = input()
                envFormat = \
                    "[default]\n" +\
                    "testnetNode=\"" + testnetNode + "\"\n" +\
                    "apiURL=\"" + apiURL + "\"\n"
                create(fulldirpath, fullenvpath, envFormat)



        elif chain == "Sepolia":
            chain_framework_path = "EVM/Atomicity/"
            fulldirpath = chain_framework_path + accountName
            fullenvpath = fulldirpath + "/.env"
            fullencenvpath = fulldirpath + "/.env.encrypted"
            if os.path.isfile(fullenvpath) or os.path.isfile(fullencenvpath):
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
            if accountName != "basic_framework":
                print("Chain:", chain, "\nAccount Name chosen:", accountName)
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
                print("Chain:", chain)
                print("Setting up basic_framework .env file, should only include public data")
                print("Enter the RPC URL address you wish to submit calls to:")
                Sepolia = input()
                SepoliaID = "11155111" #chain id
                SepoliaScan = "https://api-sepolia.etherscan.io/api" #block explorer
                envFormat = \
                    "[default]\n" +\
                    "Sepolia=\"" + Sepolia + "\"\n" + \
                    "SepoliaID=\"" + SepoliaID + "\"\n" + \
                    "SepoliaScan=\"" + SepoliaScan + "\"\n"  
                create(fulldirpath, fullenvpath, envFormat)

    else:
        print(chain, " is not currently implemented into this framework")

