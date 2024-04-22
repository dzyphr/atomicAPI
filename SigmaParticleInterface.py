import json, ast, os, time, subprocess, json_tools
import file_tools
import config_tools
import AtomicityInterface
import hashlib
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
    cmd = "cd " + str(SigmaParticlePath)  + " && ./new_frame " + str(swapName)
    file_tools.clean_file_open("newframesigmaparticlescriptdebug", "w" , cmd)
    os.popen(cmd).read()

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True



def SigmaParticle_box_to_addr(boxId, swapName, password=""):
    tries = 20
    file_tools.clean_mkdir(SigmaParticlePath + swapName) #this might need to be created here sooner
    while tries > 0:
        try:
            tree = SigmaParticle_getTreeFromBox(boxId, swapName, password=password).replace("\n", "")
            if tree != None and tree != "":
                hashedtree = str(hashlib.sha256(tree.encode()).hexdigest())#for deterministic proper size filename
                treeToAddrCmd = \
                            "cd " + SigmaParticlePath + "treeToAddr && ./deploy.sh " + \
                            tree + " " + \
                            "../treeAddrs/" + hashedtree + " " + \
                            password
                file_tools.clean_file_open("treeToAddrScriptTestDebug", "w", treeToAddrCmd)
                res = os.popen(treeToAddrCmd).read()
                if is_json(res) == True:
                    addr = json.loads(res)["address"]
                    return addr
                else:
                    tries = tries - 1
                    time.sleep(15)
                    continue
        except ValueError as e:
            print(e)
            time.sleep(15)
            tries = tries - 1
            continue
    return "attempts exhausted looking for this box: " + boxId

def SigmaParticle_CheckLockTimeAtomicSchnorr(swapName, boxId, password=""):
    lockHeightCMD = \
                            "cd " + SigmaParticlePath + "boxConstantByIndex && ./deploy.sh " + boxId + \
                            " 8 ../../../" + swapName + "/localChain_lockHeight " + password
    file_tools.clean_file_open("lockHeightScriptDebug", "w" , lockHeightCMD)
    print(os.popen(lockHeightCMD).read())
    currentHeightCMD = \
                    "cd " + SigmaParticlePath + "currentHeight && ./deploy.sh ../../../" + \
                    swapName + "/localChain_currentHeight " + password
    file_tools.clean_file_open("currentHeightCMDDeubug", "w", currentHeightCMD)
    print(os.popen(currentHeightCMD).read())
    if os.path.isfile(swapName + "/localChain_lockHeight") == True and os.path.isfile(swapName + "/localChain_currentHeight") == True:
        lockHeight = file_tools.clean_file_open(swapName + "/localChain_lockHeight", "r")
        currentHeight = file_tools.clean_file_open(swapName + "/localChain_currentHeight", "r")
        if currentHeight.isnumeric() == True and lockHeight.isnumeric() == True:
            if int(currentHeight) <= int(lockHeight):
                return int(lockHeight) - int(currentHeight) + 1 #plus 1 because currently contract checks for GREATER THAN lock height
                                                                #TODO: verify this
            else:
                return 0
        else:
            print("error: currentHeight or lockHeight is not numeric.\n currentHeight:", currentHeight, "lockHeight:", lockHeight)
            return "error: currentHeight or lockHeight is not numeric.\n currentHeight:" +  currentHeight +  "lockHeight:" +  lockHeight
    else:
        print("/localChain_lockHeight or /localChain_currentHeight files not found")
        return "/localChain_lockHeight or /localChain_currentHeight files not found"



#This function should be used for building an INITIATOR's atomic schnorr contract.
def BuildAtomicSchnorrContract(initiatorMasterJSONPath, refundDuration_BLOCKS, swapName, valueERGO):
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
    employScriptsCMD = "cp " + AtomicSwapPath + "py/main.py " + SigmaParticlePath + swapName + "/py/main.py"
    os.popen(employScriptsCMD).read()

#This function should be used for RE-CONSTRUCTING the ErgoTree Address by the RESPONDER ONLY.
def responderGenerateAtomicSchnorr(swapName, DEC_finalizationPATH, responderMasterJSONPATH, boxValue):
    if os.path.isfile(DEC_finalizationPATH) == False:
        print("finalization path is not a file! check filepath")
    else:
        claimContractGeneration = "cd " + SigmaParticlePath + " && ./new_frame " + swapName
        gen = os.popen(claimContractGeneration).read()
        importBoilerplate = "cp " + SigmaParticlePath + "/AtomicMultiSig/py/main.py " + SigmaParticlePath + swapName + "/py/main.py"
        imp = os.popen(importBoilerplate).read()
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
        os.popen(echoVariablesCMD).read()



def responderVerifyErgoScript(swapName, expectedErgoTree, password=""):
    verifyCMD = \
        "cd " + SigmaParticlePath + swapName + " && ./deploy.sh deposit verifyTreeOnly " + password
    file_tools.clean_file_open("responderVerifyErgoScriptdebug", "w", verifyCMD)
    os.popen(verifyCMD).read() 
    ergoTreePath = SigmaParticlePath + swapName + "/ergoTree"
    ergoTree = file_tools.clean_file_open(ergoTreePath, "r")
    fmt = "onchain:", expectedErgoTree, "offchain:", ergoTree
    print(fmt)
    file_tools.clean_file_open(swapName + "/ergoTreeCompareTest", "w", fmt)
    if expectedErgoTree.strip() == ergoTree.strip():
        return True
    else:
        SigmaParticle_CheckLockTimeAtomicSchnorr(swapName, json_tools.ojf(swapName + "/responder.json")["boxId"], password=password)
        return False
       

def responderClaimAtomicSchnorr(swapName, tries=None, password=""):
    rounds = 0
    if tries == None:
        rounds = 60
    elif type(tries) != int:
        print("tries must be int! defaulting to 60 tries")
        rounds = 60
    else:
        rounds = tries
    claimCMD = \
            "cd " + SigmaParticlePath + swapName + " && ./deploy.sh claim " + password
    file_tools.clean_file_open("sigmaresponderclaimscriptdebug", "w", claimCMD)
    while rounds > 0:
        response = os.popen(claimCMD).read()
        if response == None:
            rounds = rounds - 1
            time.sleep(5)
            continue
        else:
            return response
        break


def SigmaParticle_updateKeyEnv(swapName, targetKeyEnvDirName):
    if os.path.isfile(SigmaParticlePath + targetKeyEnvDirName + "/.env"):
        update = file_tools.clean_file_open(SigmaParticlePath + targetKeyEnvDirName + "/.env", "r")
        update.replace("[default]", "")
        cmd = \
                "echo \"" + update + "\"" + " >> " + SigmaParticlePath + swapName + "/.env"
        os.popen(cmd).read()
    else:
        encpath = SigmaParticlePath + targetKeyEnvDirName + "/.env.encrypted"
        if os.path.isfile(encpath):
            newpath = SigmaParticlePath + swapName + "/.env.encrypted"
            cpcmd = "cp " + encpath + " " + newpath
            os.popen(cpcmd).read()
    

def SigmaParticle_getTreeFromBox(boxID, swapName, password=""):
    tries = 60
    while tries > 0:
        boxID = boxID.replace("\n", "")
        cmd = \
                "cd " + SigmaParticlePath + "getTreeFromBox && ./deploy.sh " + boxID + \
                " ../" + swapName + "/expectedErgoTree" + " " + password
        file_tools.clean_file_open("getTreeFromBoxScriptDebug", "w", cmd)
        result = os.popen(cmd).read()
        if "notfound" in result.lower():
            tries = tries - 1
            time.sleep(5)
            continue
        else:
            return result

def deployErgoContract(swapName, password=""):
    command = "cd " + SigmaParticlePath + swapName + " && ./deploy.sh deposit " + password
    os.popen(command).read()

def getBoxID(swapName):
    path = SigmaParticlePath + swapName + "/boxId"
    if os.path.isfile(path):
        return file_tools.clean_file_open(path, "r")
    else:
        print("Path:", path, "not found!")
        return False

def checkBoxValue(boxID, boxValPATH, swapName, role=None, ergopassword="", otherchainpassword=""):
    while True:
        cmd = \
                "cd " + SigmaParticlePath + \
                "/boxValue/ && ./deploy.sh " + \
                boxID + " " + "../../../" + boxValPATH + \
                " " + ergopassword
        file_tools.clean_file_open("checkBoxValueScriptDebug", "w", cmd)
        devnull = open(os.devnull, 'wb')
        pipe = subprocess.Popen(cmd, shell=True, stdout=devnull, stderr=devnull, close_fds=True)
        pipe.wait()
        response = file_tools.clean_file_open(boxValPATH, "r")
        if "error" in str(response) or type(response) == type(None): 
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

def checkSchnorrTreeForClaim(boxID, swapName, initiatorMasterJSONPath, password=""):
    while True:
        tree = file_tools.clean_file_open(SigmaParticlePath + swapName + "/ergoTree", "r").replace("\n", "")
        treeToAddrCmd = \
                "cd " + SigmaParticlePath + "treeToAddr && ./deploy.sh " + tree + " ../" + \
                swapName + "/scriptAddr " + password
        file_tools.clean_file_open("treeToAddrScriptTestDebug", "w", treeToAddrCmd)
        addr = json.loads(os.popen(treeToAddrCmd).read())["address"]
        boxFilterCmd = \
                "cd " + SigmaParticlePath + "boxFilter && " + \
                "./deploy.sh " + addr + " " + boxID + " ../../../" + swapName + "/atomicClaim"
        os.popen(boxFilterCmd).read()
        if os.path.isfile(swapName + "/atomicClaim_tx1") == True:
            j = json.loads(file_tools.clean_file_open(swapName + "/atomicClaim_tx1", "r"))
            R4 = j["outputs"][0]["additionalRegisters"]["R4"]
            sr_list = [{"sr":R4}]
            json_tools.keyVal_list_update(sr_list, initiatorMasterJSONPath)
#            print("atomic swap was claimed by responder!")
            return True
        else:
#            print("no atomic swap claim found...")
            #check contract lock time here for refund
            remainingLocalLockTime = SigmaParticle_CheckLockTimeAtomicSchnorr(swapName, boxID, password=password)
            if type(remainingLocalLockTime) == int:
                if remainingLocalLockTime <= 0:
                    #claim refund here
                    echoBoxIdCMD = \
                            "echo '\natomicBox=" + boxID + "' >> " + SigmaParticlePath + swapName + "/.env"
                    os.popen(echoBoxIdCMD).read()

                    cmd =  "cd " + SigmaParticlePath + swapName  + " && ./deploy.sh refund"
                    print(os.popen(cmd).read()) #TODO check for success
                    return False
                time.sleep(5)
                continue
            

#This function takes a Register from the Responder's claim transaction from the Atomic Schnorr contract.
#It applies a subtraction against a previously known partial equation
#which allows Initiator to learn x (responders ephemoral secret).
def deduceX_fromAtomicSchnorrClaim(initiatorMasterJSONPath, swapName):
    masterJSON = json.loads(file_tools.clean_file_open(initiatorMasterJSONPath, "r"))
    sr_ = masterJSON["sr_"]
    responderContractAddr = masterJSON["responderContractAddr"] 
    responderLocalChain = masterJSON["responderLocalChain"]
    enc_sr = masterJSON["sr"]
    decode_sr_cmd = \
            "cd " + SigmaParticlePath + "valFromHex && ./deploy.sh " + enc_sr + " ../../../" + swapName + "/decoded_sr.bin"
    decode = os.popen(decode_sr_cmd).read()
    sr = file_tools.clean_file_open(swapName + "/decoded_sr.bin", "r")
    deduction_cmd = \
            "cd " + SigmaParticlePath + "AtomicMultiSigECC && python3 -u py/deploy.py p1Deduce " + sr_ + " " + sr
    deduction_response = os.popen(deduction_cmd).read()
    deduction_j = json.loads(deduction_response)
    x = deduction_j["x"]
    deduction_list = [{"x":x}]
    json_tools.keyVal_list_update(deduction_list, initiatorMasterJSONPath)
    return x



    
