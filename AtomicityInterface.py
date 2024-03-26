import time, os, ast, json, json_tools, subprocess
import file_tools
Atomicity = "EVM/Atomicity/"


def Atomicity_CheckContractFunds(swapName, j_response, password=""):
    chain = j_response["responderLocalChain"]
    contractAddr = j_response["responderContractAddr"]
    swapName = "Swap_" + swapName.replace("-", "")
    if chain == "Sepolia":
        script = "cd " + Atomicity  + "/" + swapName + \
                    " && python3 -u py/deploy.py getBalance " + \
                    contractAddr + " " + password
        value = os.popen(script).read()
        file_tools.clean_file_open("checkcontractfundsdebug", "w", script)
        return value

def Atomicity_SendFunds(addr, amount_wei, swapName, gas=None, gasMod=None, password=""):
    swapName = "Swap_" + swapName.replace("-", "")
    cmd = "cd " + Atomicity + \
            swapName + " && ./deploy.sh sendAmount " + \
            str(amount_wei) + " " + addr + " " + password
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

def Atomicity_Refund(swapName, role, gas=None, gasMod=None, password=""):
    formattedSwapName = "Swap_" + swapName.replace("-", "")
    if role == "responder":
        if gas == None or gasMod == None:
            addr = json_tools.ojf(swapName + "/response_path.json")["responderContractAddr"]
            refundCMD = \
                    "cd " + Atomicity + formattedSwapName + " && ./deploy.sh refund " + addr + " " + password
            return os.popen(refundCMD).read()
        else:
            addr = json_tools.ojf(swapName + "/response_path.json")["responderContractAddr"]
            refundCMD = \
                    "cd " + Atomicity + formattedSwapName + " && ./deploy.sh refund " +\
                    addr + " " + str(gas) + " " + str(gasMod) + " " + password
            print(refundCMD)
            return os.popen(refundCMD).read()
        


def Atomicity_RemainingLockTimeAtomicMultisig_v_002(j_response, swapName, password=""):
    resp_j = j_response
    responderChain = resp_j["responderLocalChain"]
    if responderChain == "Sepolia":
        addr = resp_j["responderContractAddr"]
        file_tools.clean_file_open("addrtest", "w", addr)
        cmd = \
                "cd " + Atomicity + "Swap_" + swapName.replace("-", "") + " && ./deploy.sh lockTime " + \
                addr + " ../../../" + swapName + "/remainingLockTime " + password
        os.popen(cmd.replace("\n", "")).read()
        if file_tools.wait_for_file(swapName + "/remainingLockTime"):
            remainingLockTime = file_tools.clean_file_open(swapName + "/remainingLockTime", "r")
            while remainingLockTime == '':
                os.popen(cmd).read()
                remainingLockTime = file_tools.clean_file_open(swapName + "/remainingLockTime", "r")
                time.sleep(5) 
            return int(remainingLockTime)
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
    file_tools.wait_for_file(Atomicity + swapName + "/contracts/" + swapName + ".sol")
    os.remove(Atomicity + swapName + "/contracts/" + swapName + ".sol")
    contract_copy = \
            "cd " + Atomicity + swapName + "/contracts " + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/AtomicMultiSigSecp256k1.sol " + swapName + ".sol" + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/ReentrancyGuard.sol . " + \
            "&& cp ../../AtomicMultiSigSecp256k1/contracts/EllipticCurve.sol . "
    cpy = os.popen(contract_copy).read()
    rename = str(file_tools.clean_file_open(Atomicity + swapName + "/contracts/" + swapName + ".sol", "r"))
    file_tools.clean_file_open(Atomicity + swapName + "/contracts/" + swapName + ".sol", "w", rename.replace('AtomicMultiSigSecp256k1', swapName))
    specifyChain = os.popen("echo 'CurrentChain=\"" + chain  + "\"' >> " + Atomicity + \
          swapName + "/.env").read()

def Atomicity_deployEVMContract(swapName, customGas=None, customGasMod=None, password=""):
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
       response = os.popen("cd " + Atomicity + swapName + "/ && python3 py/deploy.py " + password).read()
       if response.startswith("0x"):
           return response
       else:
           return "fail"
    elif custom == True:
       response = \
               os.popen(\
               "cd " +  Atomicity + swapName + \
               "/ && python3 py/deploy.py deployCustomGas " + \
               str(gas) + " " + str(gasMod)).read() + " " + password
       if str(response).startswith("0x"):
           return response
       else:
           return "fail"

def Atomicity_compareScalarContractCoords(swapName, contractAddr, expectedX, expectedY, password=""):
    swapName = "Swap_" + swapName.replace("-", "")
    x = os.popen("cd " + Atomicity + swapName + " && python3 -u py/deploy.py getXCoord " + contractAddr + " " + password).read()
    y = os.popen("cd " + Atomicity + swapName + " && python3 -u py/deploy.py getYCoord " + contractAddr + " " + password).read()
    print("onchain:(", x, " ,", y, ")  offchain:(", expectedX, " ,", expectedY, ")")
    if int(x) == int(expectedX) and int(y) == int(expectedY):
        return True
    else:
        return False

def Atomicity_claimScalarContract(initiatorMasterJSONPath, swapName, gas=None, gasMod=None, password=""):
    swapName = "Swap_" + swapName.replace("-", "")
    j_master = json.loads(file_tools.clean_file_open(initiatorMasterJSONPath, "r"))
    x = j_master["x"]
    contractAddr = j_master["responderContractAddr"]
    if gas == None or type(gas) != int:
        gas = 8000000
    if gasMod == None or type(gasMod) != int:
        gasMod = 1
    claimScript = \
            "cd " + Atomicity + swapName + " && ./deploy.sh claim " + contractAddr + " " + str(x) + \
            " " + str(gas) + " " + str(gasMod) + " " + password
    return os.popen(claimScript).read()


def Atomicity_updateKeyEnv(swapName, targetKeyEnvDirName): #TODO check for .env.encrypted?
    swapName = "Swap_" + swapName.replace("-", "")
    update = file_tools.clean_file_open(Atomicity + targetKeyEnvDirName + "/.env", "r")
    update.replace("[default]", "")
    cmd = \
        "echo \"" + update + "\"" + " >> " + Atomicity + swapName + "/.env"
    os.popen(cmd).read()

