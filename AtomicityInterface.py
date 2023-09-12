import os, ast, json, json_tools
from file_tools import *
Atomicity = "EVM/Atomicity/"

def Atomicity_CheckContractFunds(j_response):
    chain = j_response["responderLocalChain"]
    contractAddr = j_response["responderContractAddr"]
    if chain == "Sepolia":
        value = os.popen("cd " + Atomicity + "Sepolia && python3 -u py/deploy.py getBalance " + contractAddr).read()
        return value

def Atomicity_buildScalarContract(chain, counterpartyChainPub, xG, locktimeDuration, swapName):
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
    x = os.popen("cd " + Atomicity + swapname + " && python3 -u py/deploy.py getXCoord").read()
    y = os.popen("cd " + Atomicity + swapname + " && python3 -u py/deploy.py getYCoord").read()
    if x != expectedX or y != expectedY:
        return False
    else:
        return True

def Atomicity_claimScalarContract(initiatorMasterJSONPath, gas=None, gasMod=None):
    j_master = json.loads(clean_file_open(initiatorMasterJSONPath, "r"))
    chain = j_master["responderLocalChain"]
    x = j_master["x"]
    contractAddr = j_master["responderContractAddr"]
    if gas == None or type(gas) != int:
        gas = 8000000
    if gasMod == None or type(gasMod) != int:
        gasMod = 1
    claimScript = \
            "cd " + Atomicity + chain + " && ./deploy.sh claim " + contractAddr + " " + str(x) + " " + str(gas) + " " + str(gasMod)
    return os.popen(claimScript).read()


def Atomicity_updateKeyEnv(swapName, targetKeyEnvDirName):
    update = clean_file_open(Atomicity + targetKeyEnvDirName + "/.env", "r")
    update.replace("[default]", "")
    cmd = \
    "echo \"" + update + "\"" + " >> " + Atomicity + swapName + "/.env"
    os.popen(cmd).read()

