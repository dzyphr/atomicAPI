import pathlib
from pathlib import Path
import requests
import os
import time
from dotenv import load_dotenv
from dotenv import dotenv_values
load_dotenv()
from web3 import Web3
from solcx import compile_standard, install_solc, compile_files
import json
import sys
from passwordFileEncryption import get_val_from_envdata_key, decrypt_file_return_contents
import signal

contractdir = str(os.path.dirname(os.path.realpath(__file__)))
contractdir = contractdir.replace("py", "") #full path!!! from /home
contractdir = contractdir[contractdir.find("EVM"):]
targetdir = f'{contractdir}'
#print(targetdir)
loadedenv = dotenv_values(targetdir + '.env')
os.environ.update(loadedenv)

Atomicity = "EVM/Atomicity/"


solcV = os.getenv('SolidityCompilerVersion') #solidity compiler version
contractName = os.getenv('ContractName') #this variable is set when creating a new_frame
if contractName == None:
    contractName = "NOCONTRACTNAMECHOSEN" #for testing purposes to get rid of debug warning



#targetdir = f'{Atomicity}{contractName}/'
xsol = ".sol"
xjson = ".json"
xtxt = ".txt"
xabi = "-abi"
xcomp = "-comp"
xbyte = "-bytecode"
contractDir = "/contracts/"
contractFile = contractName + xsol
constructorArgs = bool(os.getenv('ConstructorArgs'))
gasMod = 1
chain = os.getenv('CurrentChain') #set the current chain in .env
from decimal import Decimal

if bool(os.getenv('VerifyBlockExplorer')) == True:
    verifyBlockExplorer = True
else:
    verifyBlockExplorer = False


def senderReclaim(addr, gas=None, gasMod=None, password=""):
    if gas == None:
        gas = 10000000
    if gasMod == None:
        gasMod = 2
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    f = open(f"{targetdir}../AtomicMultisig_ABI_0.0.2.json")
    abi = f.read()
    f.close()
    contract = rpc.eth.contract(address=addr, abi=abi)
    tx = contract.functions.senderReclaim().buildTransaction(
        {
            'chainId': chain_id,
            'from': senderAddr,
#            'gasPrice':int(Decimal( rpc.eth.gas_price) * Decimal(gasMod)),
            "maxFeePerGas": rpc.eth.getBlock("pending").baseFeePerGas \
                    + rpc.toWei('.2', 'gwei') + rpc.toWei(str(gasMod), 'gwei'),
            "maxPriorityFeePerGas": rpc.toWei(str(gasMod), 'gwei'),
            'gas': int(gas),
            'nonce': rpc.eth.get_transaction_count(senderAddr)
        }
    )
    signed_tx = rpc.eth.account.sign_transaction(tx, private_key=senderPrivKey)
    send_tx = rpc.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = rpc.eth.wait_for_transaction_receipt(send_tx)
    print(tx_receipt)

def claim(addr, x, gas=None, gasMod=None, password=""):
    if gas == None:
        gas = 8000000
    if gasMod == None:
        gasMod = 1
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password=password)
    f = open(f"{targetdir}../AtomicMultisig_ABI_0.0.2.json")
    abi = f.read()
    f.close()
    contract = rpc.eth.contract(address=addr, abi=abi)
    gasPrice = int(Decimal(rpc.eth.gas_price) * Decimal(gasMod))
    nonce = rpc.eth.get_transaction_count(senderAddr)
    def gettx(nonce):
        tx = contract.functions.receiverWithdraw(int(x)).buildTransaction({
            'chainId': chain_id,
            'from': senderAddr,
#            'gasPrice': gasPrice,
            "maxFeePerGas": rpc.eth.getBlock("pending").baseFeePerGas \
                    + rpc.toWei('.2', 'gwei') + rpc.toWei(str(gasMod), 'gwei'),
            "maxPriorityFeePerGas": rpc.toWei(str(gasMod), 'gwei'),
            'gas': int(gas),
            'nonce': rpc.eth.get_transaction_count(senderAddr)
        })
        newgas = rpc.eth.estimate_gas(tx)
        tx.update({"gas": newgas})
        return tx
    signedTx = rpc.eth.account.sign_transaction(gettx(nonce), senderPrivKey)
    while True:
        try:
            tx_hash = rpc.eth.send_raw_transaction(signedTx.rawTransaction)
            break
        except ValueError as e:
            serr = str(e)
            if "replacement transaction underpriced" in serr or 'nonce too low' in serr:
                nonce += 1
                tx = gettx(nonce)
                signedTx = rpc.eth.account.sign_transaction(tx, private_key=senderPrivKey)
    tx_receipt = rpc.eth.wait_for_transaction_receipt(tx_hash)
    print(tx_receipt)

def checkRemainingLockTime(addr, filepath=None, password=""):
    lockheight = checkLockHeight(addr, password=password)
    currentheight = getHeight(password=password)
    if lockheight >= currentheight:
        if filepath != None:
            f = open(filepath, "w")
            f.write(str(int(lockheight) - int(currentheight)))
            f.close()
        #sys.stdout.write(str(int(lockheight) - int(currentheight)))
        return int(lockheight) - int(currentheight)
    else:
        if filepath != None:
            f = open(filepath, "w")
            f.write("0")
            f.close()
        #sys.stdout.write("0")
        return 0

def getHeight(password=""):
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    return int(rpc.eth.get_block_number())

def checkLockHeight(addr, password=""):
    f = open(f"{targetdir}../AtomicMultisig_ABI_0.0.2.json")
    abi = f.read()
    f.close()
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    contract = rpc.eth.contract(address=addr, abi=abi)
    return int(contract.functions.lockHeight().call())

def checkCoords(addr, password=""):  #TODO: check curve constants against expected as well as receiver pubkey against specified pubkey
    f = open(f"{targetdir}../AtomicMultisig_ABI_0.0.2.json")
    abi = f.read()
    f.close()
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    contract = rpc.eth.contract(address=addr, abi=abi)
    x = contract.functions.gxX().call()
    y = contract.functions.gxY().call()
    onCurve = contract.functions.onCurve(x, y).call()
    assert(onCurve == True)
    if onCurve == True:
        sys.stdout.write( "(" + str(contract.functions.gxX().call()) + ", " +  str(contract.functions.gxY().call()) + ")" )
    else:
        sys.stdout.write("Coordinates are not on the curve! Do not fulfil the swap!")
        #technically this should be checked in the contract's constructor given we are using the same contract coordinated by the
        #contract abi hash, however ultimately its good practice for the counterparty to check curve validity

def getXCoord(addr, password=""):
    f = open(f"{targetdir}../AtomicMultisig_ABI_0.0.2.json")
    abi = f.read()
    f.close()
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    contract = rpc.eth.contract(address=addr, abi=abi)
#    sys.stdout.write(str(contract.functions.gxX().call()))
    return contract.functions.gxX().call()

def getYCoord(addr, password=""):
    f = open(f"{targetdir}../AtomicMultisig_ABI_0.0.2.json")
    abi = f.read()
    f.close()
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    contract = rpc.eth.contract(address=addr, abi=abi)
#   sys.stdout.write(str(contract.functions.gxY().call()))
    return contract.functions.gxY().call()


def getAccount(password=""):
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    sys.stdout.write(senderAddr)


def getBalance(address, password=""):
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    balance = str(rpc.eth.get_balance(address))
#   sys.stdout.write(balance)
    return balance

def sendAmount(amount, receiver, password="", gas=None, gasMod=None):
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password)
    nonce = rpc.eth.get_transaction_count(senderAddr)
    gasprice = rpc.eth.gas_price * gasMod
    startgas = 70000
    to = receiver
    value = int(amount)
    data = ''
    nonce = rpc.eth.get_transaction_count(senderAddr)
    if gas == None:
        gas = 7000000
    if gasMod == None:
        gasMod = 1
    def gettx(nonce):
        txdata  = {
            'to': receiver.strip(),
            'from': senderAddr,
            'value': int(amount),
#            'gasPrice': int(Decimal( rpc.eth.gas_price) * Decimal(gasMod)),
            'gas': gas,
            "maxFeePerGas": rpc.eth.getBlock("pending").baseFeePerGas \
                + rpc.toWei('.2', 'gwei') + rpc.toWei(str(gasMod), 'gwei'),
            "maxPriorityFeePerGas": rpc.toWei(str(gasMod), 'gwei'),
            'nonce': nonce,
            "chainId": chain_id
        }
        newgas = rpc.eth.estimate_gas(txdata)
        txdata.update({"gas": newgas})
        return txdata
    signedTx = rpc.eth.account.sign_transaction(gettx(nonce), senderPrivKey)
    while True:
        try:
            tx_hash = rpc.eth.send_raw_transaction(signedTx.rawTransaction)
            return tx_hash
            break
        except ValueError as e:
            serr = str(e)
            print(serr)
            if "replacement transaction underpriced" in serr or 'nonce too low' in serr:
                nonce += 1
                tx = gettx(nonce)
                signedTx = rpc.eth.account.sign_transaction(tx, private_key=senderPrivKey)

        time.sleep(1)
#    return rpc.eth.send_raw_transaction(signedTx.rawTransaction)

def pickChain(password=""):
    #PICK THE CHAIN HERE #fills all chain specific args with env variables
    #TODO idea: use this to remove chain logic flow from beggining of all other functions???
    targetdir = f'{Atomicity}{contractName}/' #migration away from sub python child processes
    if chain == "Goerli":
        if password == "":
            loadedenv = dotenv_values(targetdir + '.env')
            os.environ.update(loadedenv)
            rpc = Web3(Web3.HTTPProvider(os.getenv('Goerli')))
            chain_id = int(os.getenv('GoerliID')) #use int so it doesnt interpret env variable as string values
            senderAddr = os.getenv('GoerliSenderAddr')
            senderPrivKey = os.getenv('GoerliPrivKey')
            url = os.getenv('GoerliScan')
            return rpc, chain_id, senderAddr, senderPrivKey, url
        else:
            envdata = decrypt_file_return_contents(f'{targetdir}.env.encrypted', password)
            rpc = Web3(Web3.HTTPProvider(get_val_from_envdata_key('Goerli', envdata).strip('"\"')))
            chain_id = int(get_val_from_envdata_key('GoerliID', envdata).strip('"\"')) #use int so it doesnt interpret env variable as string values
            senderAddr = get_val_from_envdata_key('GoerliSenderAddr', envdata).strip('"\"')
            senderPrivKey = get_val_from_envdata_key('GoerliPrivKey', envdata).strip('"\"')
            url = get_val_from_envdata_key('GoerliScan', envdata).strip('"\"')
            return rpc, chain_id, senderAddr, senderPrivKey, url
    elif chain == "Sepolia":
        if password == "":
            envpath = f'{targetdir}.env'
            loadedenv = dotenv_values(envpath)
            os.environ.update(loadedenv)
            rpc = Web3(Web3.HTTPProvider(os.getenv('Sepolia')))
            chain_id = int(os.getenv('SepoliaID'))
            senderAddr = os.getenv('SepoliaSenderAddr')
            senderPrivKey = os.getenv('SepoliaPrivKey')
            url = os.getenv('SepoliaScan')
            return rpc, chain_id, senderAddr, senderPrivKey, url
        else:
            envdata = decrypt_file_return_contents(f'{targetdir}.env.encrypted', password)
#            envdata = decrypt_file_return_contents(".env.encrypted", password)
            rpc = Web3(Web3.HTTPProvider(get_val_from_envdata_key('Sepolia', envdata).strip('"\"')))
            chain_id = int(get_val_from_envdata_key('SepoliaID', envdata).strip('"\"'))
            senderAddr = get_val_from_envdata_key('SepoliaSenderAddr', envdata).strip('"\"')
            senderPrivKey = get_val_from_envdata_key('SepoliaPrivKey', envdata).strip('"\"')
            url = get_val_from_envdata_key('SepoliaScan', envdata).strip('"\"')
            return rpc, chain_id, senderAddr, senderPrivKey, url


def getContract():
    with open(targetdir + contractDir + contractFile, "r") as file:
        contract = file.read()

def checkMultiFile():
    if os.getenv('MultiFile') == "True": #flatten based on multifile arg
    #changes the flattener config based on current contract expects flattener in base directory / prev directory / `../solidity-flattener`
        change_conf = "echo \'{\"inputFilePath\": \"" + "../" + \
                    contractName  + "/contracts/" + \
                    contractName  + ".sol\",\"outputDir\": \"../" + \
                    contractName  + "/contracts/\"}\' > " + targetdir + "../solidity-flattener/config.json"
        c = os.popen(change_conf).read()
    #    print(c)
        flatOutput = os.popen("cd " + targetdir  + "../solidity-flattener/ && npm start").read()
    #    print(flatOutput)
        if "Success!" in flatOutput:
    #        print("flattened contract!")
            f = open(targetdir + "contracts/" + contractName + "_flat.sol", "r")
            flat = f.read()
            f.close()
            return flat
        else:
    #        print("failed to flatten multi-file contract, verification wont succeed automatically!")
            if verifyBlockExplorer == True:
                exit(1)

def compileContract():
    install_solc(solcV)
    #NOTE: Theoretically we can just default to compile_files later right now its convinient to use working impls
    if os.getenv('MultiFile') == "False":
        compilation = compile_standard(
        {
            "language": "Solidity",
            "sources": {contractFile: {"content": contract}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                    }
                }
            },
        },
            solc_version=solcV,
        )
        return compilation
    else:
        contractsList = os.listdir(f'{targetdir}contracts')
        i = 0
        absPaths = []
        remapDict = {}
        for contract in contractsList:
            absPaths.append(f"./{targetdir}contracts/" + contract)
            remapDict[contract] = f"./{targetdir}contracts/" + contract
        compilation = compile_files(
            absPaths,
            import_remappings=remapDict,
            solc_version=solcV,
        )
        return compilation


                            #set whether to verify on block explorer
def exportBytecode(compilation):                            #turn off when using ganache or anything else without one
    #NOTE: Theoretically we can just default to compile_files later right now its convinient to use working impls
    if os.getenv('MultiFile') == "False":
        #write contract compilation to json file
        #with open(contractName + xcomp + xjson, "w") as file:
        #    json.dump(compilation, file) #this tends to produce relatively large ~1mb files which are not used so we will keep this optional
        #get contract bytecode
        bytecode = compilation["contracts"][contractFile][contractName]["evm"]["bytecode"]["object"]
        #write bytecode to txt file
        with open(contractName + xbyte + xtxt, "w") as file:
            file.write(bytecode)
        #get abi
        abi = compilation["contracts"][contractFile][contractName]["abi"]
        #write abi to file
        with open(contractName + xabi + xjson, "w") as file:
            json.dump(abi, file)
        return abi, bytecode
    else:
        #write contract compilation to json file
        #with open(contractName + xcomp + xjson, "w") as file:
        #    json.dump(compilation, file) ##this tends to produce relatively large ~1mb files which are not used so we will keep this optional
        #get contract bytecode
#        with open("comptest", "w") as file:
#            file.write(str(compilation))
        bytecode = compilation["./" + targetdir[:-1] + contractDir + contractName + xsol + ":" + contractName]['bin']
        #write bytecode to txt file
        with open(targetdir + contractName + xbyte + xtxt, "w") as file:
            file.write(bytecode)
        #get abi
        abi = compilation["./" + targetdir[:-1] + contractDir + contractName + xsol + ":" + contractName]['abi']
        #write abi to file
        with open(targetdir + contractName + xabi + xjson, "w") as file:
            json.dump(abi, file)
        return abi, bytecode


def uploadContract(senderAddr, senderPrivKey, rpc, abi, bytecode, chain_id, gas=None, gasModExtra=None):
    InitContract = rpc.eth.contract(abi=abi, bytecode=bytecode)
    #print("current gas price :", rpc.eth.gas_price );
    '''
    def getNonce(senderAddr):
        nonce = rpc.eth.getTransactionCount(senderAddr)
        pending = rpc.eth.get_block('pending').transactions
        while True:
            # Filter pending transactions by sender address and fetch nonces
            for tx in pending:
                tx_info = rpc.eth.get_transaction(tx)
                if tx_info['from'].lower() == senderAddr.lower():
                    print("match found")
                    nonce += 1
            return nonce
    nonce = getNonce(senderAddr)
    '''
    nonce = rpc.eth.getTransactionCount(senderAddr)
    if gas == None:
        gas = 8000000
    if gasModExtra == None:
        gasModExtra = 1
    def gettx(nonce):
        if constructorArgs == True:
            basefee = rpc.eth.getBlock("pending").baseFeePerGas
            tx = InitContract.constructor(*constructorParamVals).buildTransaction( #if we have constructor parameters we unwrap the array of their arguments into the constructor()
                {
                    "chainId": chain_id, 
                    "from": senderAddr, 
                    "nonce": nonce, 
                    "gas": int(gas),
                    "maxFeePerGas": (rpc.eth.getBlock("pending").baseFeePerGas \
                            + rpc.toWei('.2', 'gwei') + rpc.toWei(str(gasModExtra), 'gwei')),
                    "maxPriorityFeePerGas": rpc.toWei(str(gasModExtra), 'gwei')
                }
            )
        else:
            tx = InitContract.constructor().buildTransaction( 
                {
                    "chainId": chain_id,
                    "from": senderAddr,
                    "nonce": nonce,
                    "gas": int(gas),
                    "maxFeePerGas": (rpc.eth.getBlock("pending").baseFeePerGas \
                            + rpc.toWei('.2', 'gwei') + rpc.toWei(str(gasModExtra), 'gwei')),
                    "maxPriorityFeePerGas": rpc.toWei(str(gasModExtra), 'gwei')
                }
            )
        return tx
    tx = gettx(nonce)
    newgas = rpc.eth.estimate_gas(tx)
    tx.update({"gas": newgas})
    signedTx = rpc.eth.account.sign_transaction(tx, private_key=senderPrivKey)
    while True:
        try:
            tx_hash = rpc.eth.send_raw_transaction(signedTx.rawTransaction)
            break
        except ValueError as e:
            serr = str(e)
            if "replacement transaction underpriced" in serr or 'nonce too low' in serr:
                nonce += 1
                tx = gettx(nonce)
                signedTx = rpc.eth.account.sign_transaction(tx, private_key=senderPrivKey)

        time.sleep(1)
    tx_receipt = rpc.eth.wait_for_transaction_receipt(tx_hash, timeout=1000)
    #print(contractName, "Deployed!\n")
    print(tx_receipt.contractAddress)
    uploadedContract = rpc.eth.contract(address=tx_receipt.contractAddress, abi=abi)
    f = open(targetdir +  contractName + "-addr", "w")
    f.write(tx_receipt.contractAddress) 
    f.close()
    return tx_receipt.contractAddress

def getSOLCVersion():
    APIsolcV = "v0.8.18-nightly.2023.1.25+commit.fd9ac9ab" #latest nightly as default
    match solcV: #match solidity compiler version to API accepted verification version name
        case '0.6.0':
            APIsolcV = 'v0.6.0+commit.26b70077'
        case '0.6.12':
            APIsolcV = 'v0.6.12+commit.27d51765'
        case '0.7.5':
            APIsolcV = 'v0.7.5+commit.eb77ed08'
        case '0.7.6':
            APIsolcV = 'v0.7.6+commit.7338295f'
        case '0.8.0':                           #gets confusing at 8.0 need to make sure we arent skipping a generation
            APIsolcV = 'v0.8.0+commit.c7dfd78e'
        case '0.8.1':
            APIsolcV = 'v0.8.1+commit.df193b15'
        case '0.8.17':
            APIsolcV = 'v0.8.17+commit.8df45f5f'
    return APIsolcV

def verify(flat, contractAddr, APIsolcV, url, fresh):
    #verifying the code on a block explorer
    if verifyBlockExplorer == True: #https://docs.etherscan.io/tutorials/verifying-contracts-programmatically
        if fresh == True:
            time.sleep(60)#giv:ve the explorer some time to register the transaction
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if constructorArgs == False:
            if os.getenv('MultiFile') == "True":
                contract = flat
            content = {
                    'apikey': os.getenv('EtherscanAPIKey'),
                    'module': 'contract',
                    'action': 'verifysourcecode',
                    'sourceCode': contract, #if failing make sure to flatten the contract https://github.com/BlockCatIO/solidity-flattener
                    'contractaddress': contractAddr,
                    'codeformat': 'solidity-single-file',
                    'contractname': contractName,
                    'compilerversion': APIsolcV,
                    'optimizationUsed': 0, #0 or 1
                    'runs': 200,
                    'evmversion': '',
                    'licenseType': 5 #GPL 3
            }
        else:
            cmd = "node js/abiEnc.js " + contractName + " " + str(len(constructorParamVals)) #we will call the abiEnc.js program followed by contractname and constructor args
                                                                                            #to get the abi encoded constructor arguments
            for val in constructorParamVals:
                #loop through param val types if array convert it to pipe-able array
                if type(val) == list:
                    strlist = "\"["
                    for i in range(len(val)):
                        if i < len(val)-1:
                            strlist = strlist + "\\\"" + val[i] + "\\\","
                        else:
                            strlist = strlist + "\\\"" + val[i] + "\\\""
                    strlist = strlist + "]\""
                    val = strlist
                cmd = cmd + " " + str(val)
            encoding = os.popen(cmd).read()

            if os.getenv('MultiFile') == "True":
                contract = flat
    #        print(encoding.replace(" ", "").replace("\n", "")) if auto-verify fails you can print the encoding and manually verify
            content = {
                    'apikey': os.getenv('EtherscanAPIKey'),
                    'module': 'contract',
                    'action': 'verifysourcecode',
                    'sourceCode': contract, #if failing make sure to flatten the contract https://github.com/BlockCatIO/solidity-flattener
                    'contractaddress': contractAddr,
                    'codeformat': 'solidity-single-file',
                    'contractname': contractName,
                    'compilerversion': APIsolcV,
                    'optimizationUsed': 0, #0 or 1
                    'runs': 200,            #must spell Arguments wrong (Arguements) to actually pass lol...
                    'constructorArguements': encoding.replace(" ", "").replace("\n", ""), #popen leaves empty space remove w replace()
                    'evmversion': '',
                    'licenseType': 5 #GPL 3
            }
        response = requests.post(url, headers=headers, data=content).content #not sure how to properly check for response working though

        if fresh == False:
            print(response.decode("utf-8"))
        j = json.loads(response.decode("utf-8"))
        guid = j["result"]
        return guid

def checkVerifStatus(guid,  url, fresh):
    data = {
            'apikey': os.getenv('EtherscanAPIKey'),
            'guid': guid,
            'module': "contract",
            'action': "checkverifystatus"
    }
    response = requests.get(url, data=data).content
    if fresh == False:
        print(response.decode("utf-8"))
        #TODO:automate check for failure case save reason to file

def grabExistingContractAddr():
    if os.path.isfile(contractName + "-addr"):
        f = open(contractName + "-addr", "r")
        addr = f.read()
        f.close()
        return addr
    else:
        print("contract addr not found (not deployed yet?)")
        exit()

def deploy(gas="", gasMod="", password=""):
    rpc, chain_id, senderAddr, senderPrivKey, url = pickChain(password=password)
    getContract()
    flat = checkMultiFile()
    compilation = compileContract()
    abi, bytecode = exportBytecode(compilation)
    contractAddr = uploadContract(senderAddr, senderPrivKey, rpc, abi, bytecode, chain_id, gas=gas, gasModExtra=gasMod)
    APISolcV = getSOLCVersion()
    return contractAddr

#print(sys.argv)
#print(len(sys.argv))
args_n = len(sys.argv)
if args_n > 1:
    if sys.argv[1] == "getAccount":
        if args_n == 2:
            getAccount()
            exit()
        elif args_n == 3:
            getAccount(password=sys.argv[2])
            exit()
    elif sys.argv[1] == "sendAmount":
        if args_n == 4:
            sendAmount(sys.argv[2], sys.argv[3])
            exit()
        elif args_n == 5:
            sendAmount(sys.argv[2], sys.argv[3], password=sys.argv[4])
            exit()
        else:
            print("enter amount(in wei), receiver evm pubkey as followup arguments to sendAmount")
            exit()
    elif sys.argv[1] == "getBalance":
        if args_n == 3:
            getBalance(sys.argv[2])
            exit()
        if args_n == 4:
            getBalance(sys.argv[2], password=sys.argv[3])
            exit()
        else:
            print("enter address to get balance from as followup argument")
            exit()
    elif sys.argv[1] == "checkCoords":
        if args_n > 2:
            checkCoords(sys.argv[2])
            exit()
        elif args_n > 3:
            checkCoords(sys.argv[2], password=sys.argv[3])
            exit()
        else:
            print("enter the address to check as followup argument")
            exit()
    elif sys.argv[1] == "getXCoord":
        if args_n == 3:
            getXCoord(sys.argv[2])
            exit()
        if args_n == 4:
            getXCoord(sys.argv[2], password=sys.argv[3])
            exit()
        else:
            print("enter the address to check as followup argument")
            exit()
    elif sys.argv[1] == "getYCoord":
        if args_n == 3:
            getYCoord(sys.argv[2])
            exit()
        if args_n == 4:
            getYCoord(sys.argv[2], password=sys.argv[3])
            exit()
        else:
            print("enter the address to check as followup argument")
            exit()
    elif sys.argv[1] == "claim":
        if args_n == 4 :
            claim(sys.argv[2], sys.argv[3])
            exit()
        if args_n == 5:
            claim(sys.argv[2], sys.argv[3], password=sys.argv[5])
            exit()
        if args_n == 6:
            claim(sys.argv[2], sys.argv[3], gas=sys.argv[4], gasMod=sys.argv[5])
            exit()
        if args_n == 7:
            claim(sys.argv[2], sys.argv[3], gas=sys.argv[4], gasMod=sys.argv[5], password=sys.argv[6])
            exit()
        else :
            print("enter the address, x, optional: gas and gasMod as followup arguments")
            exit()
    elif sys.argv[1] == "refund":
        if args_n == 3 :
            senderReclaim(sys.argv[2])
            exit()
        if args_n == 4 :
            senderReclaim(sys.argv[2], password=sys.argv[3])
            exit()
        if args_n == 5  : 
            senderReclaim(sys.argv[2], gas=sys.argv[3], gasMod=sys.argv[4])
            exit()
        if args_n == 6  :
            senderReclaim(sys.argv[2], gas=sys.argv[3], gasMod=sys.argv[4], password=sys.argv[5])
            exit()
        else:
            print("enter the address, optional: gas and gasMod as followup arguments")
            exit()
    elif sys.argv[1] == "lockTime":
        if args_n == 3:
            checkRemainingLockTime(sys.argv[2])
            exit()
        if args_n == 4:
            checkRemainingLockTime(sys.argv[2], sys.argv[3])
            exit()
        if args_n == 5:
            checkRemainingLockTime(sys.argv[2], sys.argv[3], password=sys.argv[4])
        #if args_n == 5: then env is encrypted and use this arg implicitly as password
        else:
            print("enter address, optional: filepath as follup arguments")
    elif sys.argv[1] == "verify":
        #TODO update w password usage in pickchain
        time.sleep(30)
        rpc, chain_id, senderAddr, senderPrivKey, url = pickChain()
        flat = checkMultiFile()
        contractAddr = grabExistingContractAddr()
        APISolcV = getSOLCVersion()
        guid = verify(flat, contractAddr, APISolcV, url, False)
        time.sleep(30)
        checkVerifStatus(guid,  url, False)
        exit()
    elif sys.argv[1] == "deployCustomGas":
        if args_n == 4:
            gas = sys.argv[2]
            gasMod = sys.argv[3]
            deploy(gas=gas, gasMod=gasMod)
            exit()
        if args_n == 5:
            gas = sys.argv[2]
            gasModExtra = sys.argv[3]
            password = sys.argv[4]
            deploy(gas=gas, gasMod=gasMod, password=password)
