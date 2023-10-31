import os, ast, json, json_tools, subprocess
from file_tools import *
Atomicity = "EVM/Atomicity/"


def Atomicity_CheckContractFunds(j_response):
    chain = j_response["responderLocalChain"]
    contractAddr = j_response["responderContractAddr"]
    if chain == "Sepolia":
        value = os.popen("cd " + Atomicity  + chain + "  && python3 -u py/deploy.py getBalance " + contractAddr).read()
        return value

def Atomicity_SendFunds(addr, amount_wei, swapName, gas=None, gasMod=None):
    swapName = "Swap_" + swapName.replace("-", "")
    cmd = "cd " + Atomicity + \
            swapName + " && ./deploy.sh sendAmount " + \
            str(amount_wei) + " " + addr
    return os.popen(cmd).read()

def Atomicity_newFrame(swapName, chain, multiFile=None, constructorArgs=None):
    swapName = "Swap_" + swapName.replace("-", "")
    cmd = ""
    if multiFile == None and constructorArgs == None:
        cmd = "cd " + Atomicity + "&& ./new_frame " + swapName  
    specChain = "echo 'CurrentChain=\"" + chain  + "\"' >> " + Atomicity + \
          swapName + "/.env" 

    os.popen(cmd).read()
    os.popen(specChain).read()

def Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName):
    resp_j = j_response
    responderChain = resp_j["responderLocalChain"]
    if responderChain == "Sepolia":
        addr = resp_j["responderContractAddr"]
        cmd = \
                "cd " + Atomicity + "Swap_" + swapName.replace("-", "") + " && ./deploy.sh lockTime " + \
                addr + " ../../../" + swapName + "/remainingLockTime"
        print(os.popen(cmd).read())
#        devnull = open(os.devnull, 'wb')
#        response = subprocess.Popen(cmd, shell=True,
#                        stdout=devnull, stderr=devnull,close_fds=True)
#        print(response)
        if wait_for_file(swapName + "/remainingLockTime"):
            remainingLockTime = clean_file_open(swapName + "/remainingLockTime", "r")
            return remainingLockTime
        else:
            print("failed to create or find remainingLockTime file")
    else:
        print("chain un-handled:", responderChain)


def Atomicity_buildScalarContract(chain, counterpartyChainPub, xG, locktimeDuration, swapName):
    swapName = "Swap_" + swapName.replace("-", "")
    cmd = "cd " + Atomicity + "&& ./new_frame " + swapName + \
            " -M -CA 4 " + "\\\"" + counterpartyChainPub + "\\\" " + \
            str(ast.literal_eval(xG)[0]) + " " + str(ast.literal_eval(xG)[1]) + " " + str(locktimeDuration)
    new_frame = os.popen(cmd).read()
    wait_for_file(Atomicity + swapName + "/contracts/" + swapName + ".sol")
    os.remove(Atomicity + swapName + "/contracts/" + swapName + ".sol")
    contract_copy = \
            "cd " + Atomicity + swapName + "/contracts " + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/AtomicMultiSigSecp256k1.sol " + swapName + ".sol" + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/ReentrancyGuard.sol . " + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/EllipticCurve.sol . "
    cpy = os.popen(contract_copy).read()
    rename = str(clean_file_open(Atomicity + swapName + "/contracts/" + swapName + ".sol", "r"))
    clean_file_open(Atomicity + swapName + "/contracts/" + swapName + ".sol", "w", rename.replace('AtomicMultiSigSecp256k1', swapName))
    specifyChain = os.popen("echo 'CurrentChain=\"" + chain  + "\"' >> " + Atomicity + \
          swapName + "/.env").read()

def Atomicity_deployEVMContract(swapName, customGas=None, customGasMod=None):
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
       response = os.popen("cd " + Atomicity + swapName + "/ && python3 py/deploy.py").read()
       if response.startswith("0x"):
           return response
       else:
           return "fail"
    elif custom == True:
       response = \
               os.popen(\
               "cd " +  Atomicity + swapName + \
               "/ && python3 py/deploy.py deployCustomGas " + \
               str(gas) + " " + str(gasMod)).read()
       if str(response).startswith("0x"):
           return response
       else:
           return "fail"

def Atomicity_compareScalarContractCoords(swapName, contractAddr, expectedX, expectedY):
    swapName = "Swap_" + swapName.replace("-", "")
    x = os.popen("cd " + Atomicity + swapName + " && python3 -u py/deploy.py getXCoord " + contractAddr).read()
    y = os.popen("cd " + Atomicity + swapName + " && python3 -u py/deploy.py getYCoord " + contractAddr).read()
    print("onchain:(", x, " ,", y, ")  offchain:(", expectedX, " ,", expectedY, ")")
    if int(x) == int(expectedX) and int(y) == int(expectedY):
        return True
    else:
        return False

def Atomicity_claimScalarContract(initiatorMasterJSONPath, swapName, gas=None, gasMod=None):
    swapName = "Swap_" + swapName.replace("-", "")
    j_master = json.loads(clean_file_open(initiatorMasterJSONPath, "r"))
    x = j_master["x"]
    contractAddr = j_master["responderContractAddr"]
    if gas == None or type(gas) != int:
        gas = 8000000
    if gasMod == None or type(gasMod) != int:
        gasMod = 1
    claimScript = \
            "cd " + Atomicity + swapName + " && ./deploy.sh claim " + contractAddr + " " + str(x) + " " + str(gas) + " " + str(gasMod)
    return os.popen(claimScript).read()


def Atomicity_updateKeyEnv(swapName, targetKeyEnvDirName):
    swapName = "Swap_" + swapName.replace("-", "")
    update = clean_file_open(Atomicity + targetKeyEnvDirName + "/.env", "r")
    update.replace("[default]", "")
    cmd = \
    "echo \"" + update + "\"" + " >> " + Atomicity + swapName + "/.env"
    os.popen(cmd).read()

