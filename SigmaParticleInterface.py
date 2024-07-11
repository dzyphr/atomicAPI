import json, ast, os, time, subprocess, json_tools, file_tools, config_tools, AtomicityInterface, hashlib
import importlib.util
from LOG import LOG
py = "python3 -u "
SigmaParticlePath = "Ergo/SigmaParticle/"
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
AtomicSwapPath = "Ergo/SigmaParticle/AtomicMultiSig/"


#def SigmaParticle_addNodeEndpoint(nodeurl, accountName):
#    nodesmax = 64 #arbitrary limit
#    filepath = SigmaParticlePath + accountName + "/.env"
#    apiURL_label = "apiURL"
#    index = 0
#    while index < nodesmax
#        if os.path.isfile(filepath):
#            if config_tools.valFromConf(filepath, apiURL_label) == None:
#                cmd  = \
#                        "echo " + "\'\""
#        else:

def SigmaParticle_newFrame(swapName):
    LOG('SigmaParticle_newFrame')
    cmd = "cd " + str(SigmaParticlePath)  + " && ./new_frame " + str(swapName)
#    file_tools.clean_file_open("newframesigmaparticlescriptdebug", "w" , cmd)
    output = os.popen(cmd).read()
    LOG(f'SigmaParticle new_frame output:{output}')

def is_json(j): #TODO use the one from json_tools
    try:
        json.loads(j)
    except (ValueError , TypeError) as e:
        return False
    return True

def SigmaParticle_treeToAddr(tree, swapName, filename, password=""):
    scriptPath = f'{SigmaParticlePath}treeToAddr/py/connect.py'
    spec = importlib.util.spec_from_file_location("connect", scriptPath)
    connect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connect)
    node_url = connect.connect(password=password) #dotenv loaded here dont call env vars before

    scriptPath = f'{SigmaParticlePath}treeToAddr/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    res = main.treeToAddr(node_url, tree, filepath=f'{swapName}/{filename}', password=password)
    return res

def SigmaParticle_box_to_addr(boxId, swapName, password=""):
    LOG('SigmaParticle_box_to_addr')
    tries = 20
    file_tools.clean_mkdir(SigmaParticlePath + swapName) #this might need to be created here sooner
    while tries > 0:
        try:
            tree = SigmaParticle_getTreeFromBox(boxId, swapName, password=password).replace("\n", "")
            if tree != None and tree != "":
                hashedtree = str(hashlib.sha256(tree.encode()).hexdigest())#for deterministic proper size filename
                '''
                scriptPath = f'{SigmaParticlePath}treeToAddr/py/connect.py'
                spec = importlib.util.spec_from_file_location("connect", scriptPath)
                connect = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(connect)
                node_url = connect.connect(password=password) #dotenv loaded here dont call env vars before

                scriptPath = f'{SigmaParticlePath}treeToAddr/py/main.py'
                spec = importlib.util.spec_from_file_location("main", scriptPath)
                main = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main)
                res = main.treeToAddr(node_url, tree, filepath=f'{swapName}/boxAddr', password=password)
                '''
                res = SigmaParticle_treeToAddr(tree, swapName, 'boxAddr', password=password)
                '''
                treeToAddrCmd = \
                            "cd " + SigmaParticlePath + "treeToAddr && ./deploy.sh " + \
                            tree + " " + \
                            "../../../" + swapName + "/boxAddr" 
                
#                file_tools.clean_file_open("treeToAddrScriptTestDebug", "w", treeToAddrCmd)
                res = os.popen(treeToAddrCmd).read()
                '''
                LOG(f'SigmaParticle treeToAddr output: {res}')
                if is_json(res) == True:
                    addr = json.loads(res)["address"]
                    return addr
                else:
                    waittime = 15
                    LOG(f'response not json, retrying in {waittime}')
                    tries = tries - 1
                    time.sleep(waittime)
                    continue
        except ValueError as e:
            print(e)
            waittime = 15
            LOG(f'response not json, retrying in {waittime}')
            time.sleep(waittime)
            tries = tries - 1
            continue
    LOG(f'attempts exhausted looking for this box: {boxId}')
    return "attempts exhausted looking for this box: " + boxId

def is_file_contents_int(file_path):
    try:
        with open(file_path, 'r') as file:
            contents = file.read().strip()
        
        if not contents: #checks for empty file
            return False
        # Split contents into individual elements assuming they are space-separated
        elements = contents.split()
        
        # Check if all elements are integers
        for element in elements:
            if not element.isdigit() and not (element.startswith('-') and element[1:].isdigit()):
                return False
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False




def SigmaParticle_CheckLockTimeAtomicSchnorr(swapName, boxId, password=""):
    LOG('SigmaParticle_CheckLockTimeAtomicSchnorr')
    #TODO remove password, public call
    lockHeightPath = SigmaParticlePath + swapName + "/lockHeight"
    if os.path.isfile(lockHeightPath) == False:
        while is_file_contents_int(lockHeightPath) == False:
            scriptPath = f'{SigmaParticlePath}boxConstantByIndex/py/connect.py'
            spec = importlib.util.spec_from_file_location("connect", scriptPath)
            connect = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(connect)
            ergo = connect.connect(password=password) 
            #dotenv loaded here dont call env vars before

            scriptPath = f'{SigmaParticlePath}boxConstantByIndex/py/main.py'
            spec = importlib.util.spec_from_file_location("main", scriptPath)
            main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main)
            output = main.getConstantAt(ergo, boxId, 8, filepath=f'{SigmaParticlePath}{swapName}/lockHeight')
            '''
            lockHeightCMD = \
                            "cd " + SigmaParticlePath + "boxConstantByIndex && ./deploy.sh " + boxId + \
                            " 8 ../" + swapName + "/lockHeight"
#            file_tools.clean_file_open("lockHeightScriptDebug", "w" , lockHeightCMD)
            output = os.popen(lockHeightCMD).read()
            '''
            LOG(f'SigmaParticle boxConstantByIndex output: {output}')
            time.sleep(5)
    '''
    currentHeightCMD = \
                    "cd " + SigmaParticlePath + "currentHeight && ./deploy.sh ../../../" + \
                    swapName + "/localChain_currentHeight " 
    file_tools.clean_file_open("currentHeightCMDDeubug", "w", currentHeightCMD)
    output = os.popen(currentHeightCMD).read()
    '''
    scriptPath = f'{SigmaParticlePath}currentHeight/py/connect.py'
    spec = importlib.util.spec_from_file_location("connect", scriptPath)
    connect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connect)
    ergo = connect.connect(password=password)
    #dotenv loaded here dont call env vars before

    scriptPath = f'{SigmaParticlePath}currentHeight/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    output = main.height_filepath(ergo, f'{swapName}/localChain_currentHeight')

    LOG(f'SigmaParticle currentHeight output: {output}')

    if \
    os.path.isfile(SigmaParticlePath + swapName + "/lockHeight") == True and \
    os.path.isfile(swapName + "/localChain_currentHeight") == True:
        lockHeight = file_tools.clean_file_open(SigmaParticlePath + swapName + "/lockHeight", "r")
        currentHeight = file_tools.clean_file_open(swapName + "/localChain_currentHeight", "r")
        if currentHeight.isnumeric() == True and lockHeight.isnumeric() == True:
            if int(currentHeight) <= int(lockHeight):
                lockTime = int(lockHeight) - int(currentHeight) + 1#plus 1 because currently contract checks for GREATER THAN lock height
                                                                #TODO: verify this
                LOG(f'SigmaParticle_CheckLockTimeAtomicSchnorr output: {lockTime}')
                return lockTime #plus 1 because currently contract checks for GREATER THAN lock height
                                                                #TODO: verify this

            else:
                LOG('SigmaParticle_CheckLockTimeAtomicSchnorr output: {0}')
                return 0
        else:
            LOG(f'error: currentHeight or lockHeight is not numeric.\n currentHeight: {currentHeight} lockHeight: {lockHeight}')
            print("error: currentHeight or lockHeight is not numeric.\n currentHeight:", currentHeight, "lockHeight:", lockHeight)
            return "error: currentHeight or lockHeight is not numeric.\n currentHeight:" +  currentHeight +  "lockHeight:" +  lockHeight
    else:
        LOG('/localChain_lockHeight or /localChain_currentHeight files not found')
        print("/localChain_lockHeight or /localChain_currentHeight files not found")
        return "/localChain_lockHeight or /localChain_currentHeight files not found"



#This function should be used for building an INITIATOR's atomic schnorr contract.
def BuildAtomicSchnorrContract(initiatorMasterJSONPath, refundDuration_BLOCKS, swapName, valueERGO):
    LOG('BuildAtomicSchnorrContract')
    j = json.loads(file_tools.clean_file_open(initiatorMasterJSONPath, "r"))
    krG = ast.literal_eval(j["krG"])
    srG = ast.literal_eval(j["srG"])
    ssG = ast.literal_eval(j["ssG"])
    ksG = ast.literal_eval(j["ksG"])
    responderChainPubKey = j["ResponderErgoAddr"]
    initiatorEIP3Secret = j["InitiatorEIP3Secret"]
    cmd = "cd " + str(SigmaParticlePath)  + " && ./new_frame " + str(swapName) + \
        " && cd " + str(swapName) + " && echo " + \
        "'" + \
        "senderEIP3Secret=" + str(initiatorEIP3Secret)  + "\n" + \
        "receiverAddr=\"" + str(responderChainPubKey) + "\"\n" + \
        "ergoAmount=" + str(valueERGO) + "\n" +\
        "refundDuration=" + str(refundDuration_BLOCKS) + "\n" + \
        "krGX=" + str(krG[0]) + "\n" +\
        "krGY=" + str(krG[1]) + "\n" +\
        "ksGX=" + str(ksG[0]) + "\n" +\
        "ksGY=" + str(ksG[1]) + "\n" +\
        "srGX=" + str(srG[0]) + "\n" +\
        "srGY=" + str(srG[1]) + "\n" +\
        "ssGX=" + str(ssG[0]) + "\n" +\
        "ssGY=" + str(ssG[1]) + "\n" +\
        "'" + \
        " >> .env"
    createContract = os.popen(cmd).read()
    LOG(f'createContract output: {createContract}')
    employScriptsCMD = "cp " + AtomicSwapPath + "py/main.py " + SigmaParticlePath + swapName + "/py/main.py"
    employ = os.popen(employScriptsCMD).read()
    LOG(f'employScripts output: {employ}')

#This function should be used for RE-CONSTRUCTING the ErgoTree Address by the RESPONDER ONLY.
def responderGenerateAtomicSchnorr(swapName, DEC_finalizationPATH, responderMasterJSONPATH, boxValue):
    LOG('responderGenerateAtomicSchnorr')
    if os.path.isfile(DEC_finalizationPATH) == False:
        print("finalization path is not a file! check filepath")
    else:
        claimContractGeneration = "cd " + SigmaParticlePath + " && ./new_frame " + swapName
        gen = os.popen(claimContractGeneration).read()
        LOG(f'SigmaParticle new_frame output: {gen}')
        importBoilerplate = "cp " + SigmaParticlePath + "/AtomicMultiSig/py/main.py " + SigmaParticlePath + swapName + "/py/main.py"
        imp = os.popen(importBoilerplate).read()
        (f'importBoilerPlate output: {imp}')
        finalization = json.loads(file_tools.clean_file_open(DEC_finalizationPATH, "r"))
        master = json.loads(file_tools.clean_file_open(responderMasterJSONPATH, "r"))
        responderChainPubKey = master["ResponderErgoAddr"]
        initiatorChainPubKey = master["InitiatorErgoAddr"]
        lockHeight = master["InitiatorAtomicSchnorrLockHeight"]
        ss = finalization["ss"]
        sr = master["sr"]
        srG = ast.literal_eval(master["srG"])
        ssG = ast.literal_eval(master["ssG"])
        krG = master["krG"]
        ksG = master["ksG"]
        boxID = finalization["boxId"]
        nanoErgs = boxValue
        echoVariablesCMD = \
            "echo \"" + \
            "sr=" + sr + "\n" + \
            "ss=" + ss + "\n" + \
            "srGX=" + str(srG[0]) + "\n" +\
            "srGY=" + str(srG[1]) + "\n" +\
            "ssGX=" + str(ssG[0]) + "\n" +\
            "ssGY=" + str(ssG[1]) + "\n" +\
            "receiverAddr=\"" + str(responderChainPubKey) + "\"\n" + \
            "senderAddr=\"" + str(initiatorChainPubKey) + "\"\n" + \
            "ksGX=" + str(ast.literal_eval(ksG)[0]) + "\n" + \
            "ksGY=" + str(ast.literal_eval(ksG)[1]) + "\n" + \
            "krGX=" + str(ast.literal_eval(krG)[0]) + "\n" + \
            "krGY=" + str(ast.literal_eval(krG)[1]) + "\n" + \
            "atomicBox=" + "\"" + boxID + "\"\n" + \
            "ergoAmount=" + str(nanoErgs) + "\n" + \
            "staticLockHeight=" + str(lockHeight) + "\n" + \
            "\" >> " + SigmaParticlePath + swapName + "/.env"
        out = os.popen(echoVariablesCMD).read()
        LOG(f'echoVariables output: {out}')



def responderVerifyErgoScript(swapName, expectedErgoTree, password=""):
    LOG('responderVerifyErgoScript')

    scriptPath = f'{SigmaParticlePath}{swapName}/py/connect.py'
    spec = importlib.util.spec_from_file_location("connect", scriptPath)
    connect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connect)
    ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret = connect.connect(password=password)
    #dotenv loaded here dont call env vars before

    scriptPath = f'{SigmaParticlePath}{swapName}/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    verify = main.atomicDeposit(ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret, verifyTreeOnly=True, password=password)
    '''
    verifyCMD = \
        "cd " + SigmaParticlePath + swapName + " && ./deploy.sh deposit verifyTreeOnly " + password
#    file_tools.clean_file_open("responderVerifyErgoScriptdebug", "w", verifyCMD)
    verify = os.popen(verifyCMD).read() 
    '''
    LOG('SigmaParticle verifyTreeOnly output: {verify}')
    ergoTreePath = SigmaParticlePath + swapName + "/ergoTree"
    ergoTree = file_tools.clean_file_open(ergoTreePath, "r")
    fmt = "onchain:", expectedErgoTree, "offchain:", ergoTree
    print(fmt)
    LOG(f'onchain: {expectedErgoTree} offchain: {ergoTree}')
#    file_tools.clean_file_open(swapName + "/ergoTreeCompareTest", "w", fmt)
    if expectedErgoTree.strip() == ergoTree.strip():
        LOG('SigmaParticle Verification True')
        return True
    else:
        LOG('SigmaParticle Verification False')
        SigmaParticle_CheckLockTimeAtomicSchnorr(swapName, json_tools.ojf(swapName + "/responder.json")["boxId"], password=password)
        return False
       

def responderClaimAtomicSchnorr(swapName, tries=None, password=""):
    LOG('responderClaimAtomicSchnorr')
    rounds = 0
    if tries == None:
        rounds = 60
    elif type(tries) != int:
        print("tries must be int! defaulting to 60 tries")
        rounds = 60
    else:
        rounds = tries

    scriptPath = f'{SigmaParticlePath}{swapName}/py/connect.py'
    spec = importlib.util.spec_from_file_location("connect", scriptPath)
    connect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connect)
    ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret = connect.connect(password=password)
    #dotenv loaded here dont call env vars before

    scriptPath = f'{SigmaParticlePath}{swapName}/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    '''
    claimCMD = \
            "cd " + SigmaParticlePath + swapName + " && ./deploy.sh claim " + password
#    file_tools.clean_file_open("sigmaresponderclaimscriptdebug", "w", claimCMD)
    '''
    while rounds > 0:
        claim = main.atomicReceiverClaim( \
                ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret,  password=password \
        )
        LOG(f'SigmaParticle claim response: {claim}')
        if claim == None:
            waittime = 5
            LOG(f'response was None, retrying in {waittime}')
            rounds = rounds - 1
            time.sleep(waittime)
            continue
        else:
            return claim
        break


def SigmaParticle_updateKeyEnv(swapName, targetKeyEnvDirName):
    LOG('SigmaParticle_updateKeyEnv')
    if os.path.isfile(SigmaParticlePath + targetKeyEnvDirName + "/.env"):
        update = file_tools.clean_file_open(SigmaParticlePath + targetKeyEnvDirName + "/.env", "r")
        update.replace("[default]", "")
        cmd = \
                "echo \"" + update + "\"" + " >> " + SigmaParticlePath + swapName + "/.env"
        echo = os.popen(cmd).read()
        LOG(f'updateKeyEnv output: {echo}')
    else:
        encpath = SigmaParticlePath + targetKeyEnvDirName + "/.env.encrypted"
        if os.path.isfile(encpath):
            newpath = SigmaParticlePath + swapName + "/.env.encrypted"
            cpcmd = "cp " + encpath + " " + newpath
            cp = os.popen(cpcmd).read()
            LOG(f'updateKeyEnv output: {cp}')

    

def SigmaParticle_getTreeFromBox(boxID, swapName, password=""):
    LOG('SigmaParticle_getTreeFromBox')
    #TODO REMOVE password var, its a public call
    tries = 60
    while tries > 0:
        boxID = boxID.replace("\n", "")
        '''
        cmd = \
                "cd " + SigmaParticlePath + "getTreeFromBox && ./deploy.sh " + boxID + \
                " ../" + swapName + "/expectedErgoTree" + " "
#        file_tools.clean_file_open("getTreeFromBoxScriptDebug", "w", cmd)
        result = os.popen(cmd).read()
        '''
        scriptPath = f'{SigmaParticlePath}getTreeFromBox/py/connect.py'
        spec = importlib.util.spec_from_file_location("connect", scriptPath)
        connect = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(connect)
        nodeurl = connect.connect(password=password)
        #dotenv loaded here dont call env vars before

        scriptPath = f'{SigmaParticlePath}getTreeFromBox/py/main.py'
        spec = importlib.util.spec_from_file_location("main", scriptPath)
        main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main)
        result = main.treeFromBox(nodeurl, boxID, filepath=f'{SigmaParticlePath}{swapName}/expectedErgoTree')
        LOG(f'SigmaParticle getTreeFromBox output: {result}')
        if "notfound" in result.lower():
            waittime = 5
            LOG(f'box not found retrying in {waittime}\ntries left: {tries}')
            tries = tries - 1
            time.sleep(waittime)
            continue
        else:
            return result

def deployErgoContract(swapName, password=""):
    LOG('deployErgoContract')
    '''
    command = "cd " + SigmaParticlePath + swapName + " && ./deploy.sh deposit " + password
 #   file_tools.clean_file_open("initiatorDeployErgoContractDebug", "w", command)
    deploy = os.popen(command).read()
    '''
    scriptPath = f'{SigmaParticlePath}{swapName}/py/connect.py'
    spec = importlib.util.spec_from_file_location("connect", scriptPath)
    connect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connect)
    ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret = connect.connect(password=password)
    #dotenv loaded here dont call env vars before

    scriptPath = f'{SigmaParticlePath}{swapName}/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
#this will depend on the contract function names so needs modularization w new routines
    main.atomicDeposit(ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret, password=password)
    LOG(f'SigmaParticle deploy output: {deploy}')

def getBoxID(swapName):
    LOG('getBoxID')
    path = SigmaParticlePath + swapName + "/boxId"
    if os.path.isfile(path):
        boxID = file_tools.clean_file_open(path, "r")
        LOG(f'boxID: {boxID}')
        return boxID
    else:
        LOG(f'Path: {path} not found!')
        print("Path:", path, "not found!")
        return False

def is_numeric_string(value):
    return isinstance(value, str) and value.isdigit()

def checkBoxValue(boxID, boxValPATH, swapName, role=None, ergopassword="", otherchainpassword=""):
    LOG('checkBoxValue')
    tries = 200
    while tries > 0:
        '''
        cmd = \
                "cd " + SigmaParticlePath + \
                "/boxValue/ && ./deploy.sh " + \
                boxID + " " + "../../../" + boxValPATH + \
                " " #DONT USE ERGO PASSWORD ITS NOT NEEDED FOR PUBLIC API STUFF #TODO Remove ergopassword
#        file_tools.clean_file_open("checkBoxValueScriptDebug", "w", cmd)
        devnull = open(os.devnull, 'wb')
        '''
        scriptPath = f'{SigmaParticlePath}boxValue/py/connect.py'
        spec = importlib.util.spec_from_file_location("connect", scriptPath)
        connect = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(connect)
        ergo = connect.connect(password=ergopassword)
        #dotenv loaded here dont call env vars before

        scriptPath = f'{SigmaParticlePath}boxValue/py/main.py'
        spec = importlib.util.spec_from_file_location("main", scriptPath)
        main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main)
    #this will depend on the contract function names so needs modularization w new routines
        while is_numeric_string(file_tools.clean_file_open(boxValPATH, "r")) == False:
            response = main.boxVal(ergo, boxID, filepath=f'{boxValPATH}')
            '''
            pipe = subprocess.Popen(cmd, shell=True, stdout=devnull, stderr=devnull, close_fds=True)
            pipe.wait()
            '''
            time.sleep(5)
#        response = file_tools.clean_file_open(boxValPATH, "r")
        LOG(f'SigmaParticle boxValue output: {response}')
        tries = tries - 1
        if str(response) in ["error"] or type(response) == type(None): #TODO needs logical cleanup
            if role == "responder":
                masterjsonpath = swapName + "/responder.json"
                responderChain = json_tools.ojf(masterjsonpath)["ResponderChain"]
                if responderChain == "Sepolia":
                    responsepath = swapName + "/response_path.json"
                    j_response = json_tools.ojf(responsepath)
                    if AtomicityInterface.Atomicity_RemainingLockTimeAtomicMultisig_v_002( \
                        j_response, swapName, password=otherchainpassword \
                    ) == 0:
                        AtomicityInterface.Atomicity_Refund(swapName, "responder",  gas=7000000, gasMod=3, password=otherchainpassword)
                        return 0
                        break
            time.sleep(5)
            continue
        else:
            return response #returns box value in nano Ergs (nΣ)
            break

def key_path_exists(data, key_path):
    """
    Check if a nested key path exists in a dictionary or list.

    Args:
        data (dict or list): The data structure to check.
        key_path (list): The list of keys and/or indices representing the path.

    Returns:
        bool: True if the path exists, False otherwise.
    """
    try:
        for key in key_path:
            if isinstance(data, list) and isinstance(key, int):
                data = data[key]
            elif isinstance(data, dict):
                data = data[key]
            else:
                return False
        return True
    except (KeyError, IndexError, TypeError):
        return False

def SigmaParticle_boxFilter(address, boxID, swapName, filename, password=""):
    scriptPath = f'{SigmaParticlePath}boxFilter/py/connect.py'
    spec = importlib.util.spec_from_file_location("connect", scriptPath)
    connect = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(connect)
    ergo = connect.connect(password=password) #dotenv loaded here dont call env vars before

    scriptPath = f'{SigmaParticlePath}boxFilter/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    res = main.txBoxFilter(ergo, address, boxID, filepath=f'{swapName}/{filename}')
    return res


def checkSchnorrTreeForClaim(boxID, swapName, initiatorMasterJSONPath, password=""):
    LOG('checkSchnorrTreeForClaim')
    tree = None
    addr = None 
    while True:
#        if os.path.isfile(SigmaParticlePath + swapName + "/ergoTree") == True:
#            tree = file_tools.clean_file_open(SigmaParticlePath + swapName + "/ergoTree", "r").replace("\n", "")
#        else:
        while tree == None:
            tree = SigmaParticle_getTreeFromBox(boxID, swapName, password=password)
        res = SigmaParticle_treeToAddr(tree, swapName, 'scriptAddr', password=password)        
        '''
        treeToAddrCmd = \
                f'cd   {SigmaParticlePath}treeToAddr && ./deploy.sh  {tree}  ../../../{swapName}/scriptAddr'
 #       file_tools.clean_file_open("treeToAddrScriptTestDebug", "w", treeToAddrCmd)
        '''
#        while addr == None:
        addr = json.loads(res)["address"]
        LOG(f'SigmaParticle treeToAddr output: {addr}')
        '''
        boxFilterCmd = \
                "cd " + SigmaParticlePath + "boxFilter && " + \
                "./deploy.sh " + addr + " " + boxID + " ../../../" + swapName + "/atomicClaim "
        file_tools.clean_file_open("boxFilterCmdDebug", "w", boxFilterCmd)
        boxFilter = os.popen(boxFilterCmd).read()
        '''
        SigmaParticle_boxFilter(addr, boxID, swapName, 'atomicClaim', password=password)
        LOG(f'SigmaParticle boxFilter output: {boxFilter}')
        if os.path.isfile(swapName + "/atomicClaim_tx1") == True:
            j = json.loads(file_tools.clean_file_open(swapName + "/atomicClaim_tx1", "r"))
            keypath = ["outputs", 0, "additionalRegisters", "R4"]
            if key_path_exists(j, keypath):
                R4 = j["outputs"][0]["additionalRegisters"]["R4"]
                sr_list = [{"sr":R4}]
                json_tools.keyVal_list_update(sr_list, initiatorMasterJSONPath)
    #            print("atomic swap was claimed by responder!")
                LOG("Atomic swap was claimed by responder!")
                return True
        else:
            LOG("no atomic swap claim found...")
            #check contract lock time here for refund
            remainingLocalLockTime = SigmaParticle_CheckLockTimeAtomicSchnorr(swapName, boxID, password=password)
            if type(remainingLocalLockTime) == int:
                if remainingLocalLockTime <= 0:
                    LOG('No claim found and locktime 0, refunding.')
                    #claim refund here
                    echoBoxIdCMD = \
                            "echo '\natomicBox=" + boxID + "' >> " + SigmaParticlePath + swapName + "/.env"
                    echo = os.popen(echoBoxIdCMD).read()
                    LOG(f'echo boxID output: {echo}')
                    '''
                    cmd =  "cd " + SigmaParticlePath + swapName  + " && ./deploy.sh refund " + password
                    refund = os.popen(cmd).read() #TODO check for success
                    '''
                    scriptPath = f'{SigmaParticlePath}{swapName}/py/connect.py'
                    spec = importlib.util.spec_from_file_location("connect", scriptPath)
                    connect = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(connect)
                    ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret = \
                            connect.connect(password=password)
                    #dotenv loaded here dont call env vars before

                    scriptPath = f'{SigmaParticlePath}{swapName}/py/main.py'
                    spec = importlib.util.spec_from_file_location("main", scriptPath)
                    main = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(main)
                    refund = main.atomicSenderRefund( \
                            ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret, password=password \
                    )
                    LOG(f'SigmaParticle refund output: {refund}')
                    return False
                time.sleep(5)
                continue
            

def SigmaParticle_valFromHex(hexval, swapName, filename):
    scriptPath = f'{SigmaParticlePath}valFromHex/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    val = main.intVal(hexval, filepath=f'{swapName}/{filename}')
    return val


def SigmaParticle_ECC_p1Deduce(sr_, sr):
    scriptPath = f'{SigmaParticlePath}AtomicMultiSigECC/py/main.py'
    spec = importlib.util.spec_from_file_location("main", scriptPath)
    main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main)
    x = main.p1Deduce(sr_, sr)
    return x


#This function takes a Register from the Responder's claim transaction from the Atomic Schnorr contract.
#It applies a subtraction against a previously known partial equation
#which allows Initiator to learn x (responders ephemoral secret).
def deduceX_fromAtomicSchnorrClaim(initiatorMasterJSONPath, swapName):
    masterJSON = json.loads(file_tools.clean_file_open(initiatorMasterJSONPath, "r"))
    sr_ = masterJSON["sr_"]
    responderContractAddr = masterJSON["responderContractAddr"] 
    responderLocalChain = masterJSON["responderLocalChain"]
    enc_sr = masterJSON["sr"]
    '''
    decode_sr_cmd = \
            "cd " + SigmaParticlePath + "valFromHex && ./deploy.sh " + enc_sr + " ../../../" + swapName + "/decoded_sr.bin " 
    decode = os.popen(decode_sr_cmd).read()
    '''
    decode = SigmaParticle_valFromHex(enc_sr, swapName, 'decoded_sr.bin')
    LOG(f'SigmaParticle valFromHex output: {decode}')
    sr = file_tools.clean_file_open(swapName + "/decoded_sr.bin", "r")
    '''
    deduction_cmd = \
            "cd " + SigmaParticlePath + "AtomicMultiSigECC && python3 -u py/deploy.py p1Deduce " + sr_ + " " + sr
    deduction_response = os.popen(deduction_cmd).read()
    '''
    deduction_response = SigmaParticle_ECC_p1Deduce(sr_, sr)
    LOG(f'SigmaParticle deduction command output: {deduction_response}')
    deduction_j = json.loads(deduction_response)
    x = deduction_j["x"]
    deduction_list = [{"x":x}]
    json_tools.keyVal_list_update(deduction_list, initiatorMasterJSONPath)
    return x



    
