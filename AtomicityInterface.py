import time, os, ast, json, json_tools, subprocess, file_tools
import importlib.util
from LOG import LOG
Atomicity = "EVM/Atomicity/"
HARDCODEDSOLCV = "0.8.0"

def Atomicity_CheckContractFunds(swapName, j_response, password=""):
    LOG('Atomicity_CheckContractFunds')
    chain = j_response["responderLocalChain"]
    contractAddr = j_response["responderContractAddr"]
    swapName = "Swap_" + swapName.replace("-", "")
    if chain == "Sepolia":
        scriptPath = f'{Atomicity}{swapName}/py/deploy.py'
        spec = importlib.util.spec_from_file_location("deploy", scriptPath)
        deploy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy)
        balance = deploy.getBalance(contractAddr)
        LOG(f'Atomicity getBalance script output: {balance}')
        return balance

def Atomicity_SendFunds(addr, amount_wei, swapName, gas=None, gasMod=None, password=""):
    LOG('Atomicity_SendFunds')
    swapName = "Swap_" + swapName.replace("-", "")
    scriptPath = f'{Atomicity}{swapName}/py/deploy.py'
    spec = importlib.util.spec_from_file_location("deploy", scriptPath)
    deploy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(deploy)
    output = deploy.sendAmount(amount_wei, addr, password=password, gas=gas, gasMod=gasMod)
    return output

def Atomicity_newFrame(swapName, chain, multiFile=None, constructorArgs=None):
    LOG('Atomicity_newFrame')
    swapName = "Swap_" + swapName.replace("-", "")
    cmd = ""
    if multiFile == None and constructorArgs == None:
        cmd = "cd " + Atomicity + "&& ./new_frame " + swapName  
    specChain = "echo 'CurrentChain=\"" + chain  + "\"' >> " + Atomicity + \
          swapName + "/.env" 
    output = os.popen(cmd).read()
    LOG(f'Atomicity new_frame script output: {output}')
    output2 = os.popen(specChain).read()
    LOG(f'echo script output: {output2}')

def Atomicity_Refund(swapName, role, gas=None, gasMod=None, password=""):
    LOG('Atomicity_Refund')
    formattedSwapName = "Swap_" + swapName.replace("-", "")
    EVMSwapName = "Swap_" + swapName.replace("-", "")
    if role == "responder":
        addr = json_tools.ojf(swapName + "/response_path.json")["responderContractAddr"]
        scriptPath = f'{Atomicity}{EVMSwapName}/py/deploy.py'
        spec = importlib.util.spec_from_file_location("deploy", scriptPath)
        deploy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy)
        output = deploy.senderReclaim(addr, gas=gas, gasMod=gasMod, password=password)
        LOG(f'Atomicity refund output: {output}')
        return output
        


def Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName, password=""):
    LOG('Atomicity_RemainingLockTimeAtomicMultisig_v_002')
    resp_j = j_response
    responderChain = resp_j["responderLocalChain"]
    EVMSwapName = "Swap_" + swapName.replace("-", "")
    if responderChain == "Sepolia":
        addr = resp_j["responderContractAddr"]
        scriptPath = f'{Atomicity}{EVMSwapName}/py/deploy.py'
        spec = importlib.util.spec_from_file_location("deploy", scriptPath)
        deploy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy)
        lockTimeoutput = deploy.checkRemainingLockTime(addr, filepath=f'{swapName}/remainingLockTime', password=password)
        LOG(f'Atomicity lockTime output: {lockTimeoutput}')
        if file_tools.wait_for_file(swapName + "/remainingLockTime"):
            remainingLockTime = file_tools.clean_file_open(swapName + "/remainingLockTime", "r")
            while remainingLockTime == '':
               # os.popen(cmd).read()
                deploy.checkRemainingLockTime(addr, filepath=f'{swapName}/remainingLockTime', password=password)
                remainingLockTime = file_tools.clean_file_open(swapName + "/remainingLockTime", "r")
                time.sleep(5) 
            LOG(f'Atomicity remainingLockTime: {remainingLockTime}')
            return int(remainingLockTime)
        else:
            LOG(f'Atomicity_RemainingLockTimeAtomicMultisig_v_002 Error:\nfailed to create or find remainingLockTime file')
            print("failed to create or find remainingLockTime file")
    else:
        LOG(f'Atomicity_RemainingLockTimeAtomicMultisig_v_002 Error:\nchain un-handled:" {responderChain}')
        print("chain un-handled:", responderChain)

def Atomicity_buildScalarContract(chain, counterpartyChainPub, xG, locktimeDuration, swapName):
    LOG('Atomicity_buildScalarContract')
    swapName = "Swap_" + swapName.replace("-", "")
    cmd = "cd " + Atomicity + "&& ./new_frame " + swapName + \
            " -M -CA 4 " + "\\\"" + counterpartyChainPub + "\\\" " + \
            str(ast.literal_eval(xG)[0]) + " " + str(ast.literal_eval(xG)[1]) + " " + str(locktimeDuration)
    new_frame = os.popen(cmd).read()
    LOG(f'Atomicity new_frame output: {new_frame}')
    file_tools.wait_for_file(Atomicity + swapName + "/contracts/" + swapName + ".sol")
    os.remove(Atomicity + swapName + "/contracts/" + swapName + ".sol")
    contract_copy = \
            "cd " + Atomicity + swapName + "/contracts " + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/AtomicMultiSigSecp256k1.sol " + swapName + ".sol" + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/ReentrancyGuard.sol . " + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/EllipticCurve.sol . "
    cpy = os.popen(contract_copy).read()
    LOG(f'cp output: {cpy}')
    rename = str(file_tools.clean_file_open(Atomicity + swapName + "/contracts/" + swapName + ".sol", "r"))
    file_tools.clean_file_open(Atomicity + swapName + "/contracts/" + swapName + ".sol", "w", rename.replace('AtomicMultiSigSecp256k1', swapName))
    specifyChain = os.popen("echo 'CurrentChain=\"" + chain  + "\"' >> " + Atomicity + \
          swapName + "/.env").read()
    LOG(f'echo CurrentChain output: {specifyChain}')
    specifySolcV = os.popen("echo 'SolidityCompilerVersion=\"" + HARDCODEDSOLCV  + "\"' >> " + Atomicity + \
          swapName + "/.env").read()
    LOG(f'echo SolidityCompilerVersion output: {specifySolcV}')

def Atomicity_deployEVMContract(swapName, customGas=None, customGasMod=None, password=""):
    LOG('Atomicity_deployEVMContract')
    #TODO:
    #There are many different potential errors that many occur when deploying a contract
    #so far we only follow the happy path so we should catch any errors we can expect
    #in order to give good UX feedback in the unfortunate case that there is an error
    #errors related to gas usage for example are expected in EVM
    custom = False
    swapName = "Swap_" + swapName.replace("-", "")
    gas = "9000000"
    if customGas != None:
        if type(customGas) != int:
            print("customGas must be int")
        else:
            gas = customGas
            custom = True
    gasMod = 1
    if customGasMod != None:
        if type(customGasMod) != int:
            print("gasMod must be int")
        else:
            gasMod = customGasMod
            custom = True
    if custom == False:
        scriptPath = f'{Atomicity}{swapName}/py/deploy.py'
        spec = importlib.util.spec_from_file_location("deploy", scriptPath)
        deploy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy)
        addr = deploy.deploy(password=password)
    elif custom == True:
        scriptPath = f'{Atomicity}{swapName}/py/deploy.py'
        spec = importlib.util.spec_from_file_location("deploy", scriptPath)
        deploy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy)
        addr = deploy.deploy(gas=customGas, gasMod=customGasMod, password=password)
    if addr.startswith("0x"):
        return addr
    else:
        return "fail"

def Atomicity_compareScalarContractCoords(swapName, contractAddr, expectedX, expectedY, password=""):
    LOG('Atomicity_compareScalarContractCoords')
    swapName = "Swap_" + swapName.replace("-", "")
    scriptPath = f'{Atomicity}{swapName}/py/deploy.py'
    spec = importlib.util.spec_from_file_location("deploy", scriptPath)
    deploy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(deploy)
    x = deploy.getXCoord(contractAddr)
    y = deploy.getYCoord(contractAddr)
    print("onchain:(", x, " ,", y, ")  offchain:(", expectedX, " ,", expectedY, ")")
    LOG(f'onchain:({x},{y}) offchain:({expectedX}, {expectedY})')
    if int(x) == int(expectedX) and int(y) == int(expectedY):
        LOG(f'Contract Coordinates Comparison Result: True')
        return True
    else:
        LOG(f'Contract Coordinates Comparison Result: False')
        return False

def Atomicity_claimScalarContract(initiatorMasterJSONPath, swapName, gas=None, gasMod=None, password=""):
    LOG('Atomicity_claimScalarContract')
    swapName = "Swap_" + swapName.replace("-", "")
    j_master = json.loads(file_tools.clean_file_open(initiatorMasterJSONPath, "r"))
    x = j_master["x"]
    contractAddr = j_master["responderContractAddr"]
    if gas == None or type(gas) != int:
        gas = 8000000
    if gasMod == None or type(gasMod) != int:
        gasMod = 1
    scriptPath = f'{Atomicity}{swapName}/py/deploy.py'
    spec = importlib.util.spec_from_file_location("deploy", scriptPath)
    deploy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(deploy)
    output = deploy.claim(contractAddr, x, gas=gas, gasMod=gasMod, password=password)
    LOG(f'Atomicity Scalar Contract Claim Output: {output}')
    return output

def Atomicity_updateKeyEnv(swapName, targetKeyEnvDirName): 
    LOG('Atomicity_updateKeyEnv')
    swapName = "Swap_" + swapName.replace("-", "")
    if os.path.isfile(Atomicity + targetKeyEnvDirName + "/.env") == True:
        update = file_tools.clean_file_open(Atomicity + targetKeyEnvDirName + "/.env", "r")
        update = update.replace("[default]", "")
        cmd = \
            "echo \"" + update + "\"" + " >> " + Atomicity + swapName + "/.env"
        response = os.popen(cmd).read()
    elif os.path.isfile(Atomicity + targetKeyEnvDirName + "/.env.encrypted") == True:
        origin = Atomicity + targetKeyEnvDirName + "/.env.encrypted"
        dest = Atomicity + swapName + "/.env.encrypted"
        cmd = "cp " + origin + " " + dest
        response = os.popen(cmd).read()
    LOG(f'Atomicity_updateKeyEnv output: {response}')

