import json, ast, os, time, subprocess, json_tools
from file_tools import *
py = "python3 -u "
SigmaParticlePath = "Ergo/SigmaParticle/"
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
AtomicSwapPath = "Ergo/SigmaParticle/AtomicMultiSig/"

def SigmaParticle_newFrame(swapName):
    cmd = "cd " + str(SigmaParticlePath)  + " && ./new_frame " + str(swapName)
    os.popen(cmd).read()

def BuildAtomicSchnorrContract(initiatorMasterJSONPath, refundDuration_BLOCKS, swapName, valueERGO):
    j = json.loads(clean_file_open(initiatorMasterJSONPath, "r"))
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


def responderGenerateAtomicSchnorr(swapName, DEC_finalizationPATH, responderMasterJSONPATH, boxValue):
    if os.path.isfile(DEC_finalizationPATH) == False:
        print("finalization path is not a file! check filepath")
    else:
        claimContractGeneration = "cd " + SigmaParticlePath + " && ./new_frame " + swapName
        gen = os.popen(claimContractGeneration).read()
        importBoilerplate = "cp " + SigmaParticlePath + "/AtomicMultiSig/py/main.py " + SigmaParticlePath + swapName + "/py/main.py"
        imp = os.popen(importBoilerplate).read()
        finalization = json.loads(clean_file_open(DEC_finalizationPATH, "r"))
        master = json.loads(clean_file_open(responderMasterJSONPATH, "r"))
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



def responderVerifyErgoScript(swapName, expectedErgoTree):
    verifyCMD = \
        "cd " + SigmaParticlePath + swapName + " && ./deploy.sh deposit verifyTreeOnly"
    os.popen(verifyCMD).read() 
    ergoTreePath = SigmaParticlePath + swapName + "/ergoTree"
    ergoTree = clean_file_open(ergoTreePath, "r")
    fmt = "onchain:", expectedErgoTree, "offchain:", ergoTree
    print(fmt)
    clean_file_open(swapName + "/ergoTreeCompareTest", "w", fmt)
    if expectedErgoTree.strip() == ergoTree.strip():
        return True
    else:
        return False
       

def responderClaimAtomicSchnorr(swapName, tries=None):
    rounds = 0
    if tries == None:
        rounds = 60
    elif type(tries) != int:
        print("tries must be int! defaulting to 60 tries")
        rounds = 60
    else:
        rounds = tries
    claimCMD = \
            "cd " + SigmaParticlePath + swapName + " && ./deploy.sh claim"
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
    update = clean_file_open(SigmaParticlePath + targetKeyEnvDirName + "/.env", "r")
    update.replace("[default]", "")
    cmd = \
            "echo \"" + update + "\"" + " >> " + SigmaParticlePath + swapName + "/.env"
    os.popen(cmd).read()
    

def SigmaParticle_getTreeFromBox(boxID):
    cmd = \
            "cd " + SigmaParticlePath + "getTreeFromBox && ./deploy.sh " + boxID
    return os.popen(cmd).read()

def deployErgoContract(swapName):
    command = "cd " + SigmaParticlePath + swapName + " && ./deploy.sh deposit"
    os.popen(command).read()

def getBoxID(swapName):
    return clean_file_open(SigmaParticlePath + swapName + "/boxId", "r")

def checkBoxValue(boxID, boxValPATH):
    while True:
        cmd = "cd " + SigmaParticlePath + "/boxValue/ && ./deploy.sh " + boxID + " " + "../../../" + boxValPATH
        devnull = open(os.devnull, 'wb')
        pipe = subprocess.Popen(cmd, shell=True, stdout=devnull, stderr=devnull, close_fds=True)
        response = clean_file_open(boxValPATH, "r")
        if "error" in str(response) or type(response) == type(None):
            time.sleep(5)
            continue
        else:
            return response #returns box value in nano Ergs (nΣ)
            break

def checkSchnorrTreeForClaim(boxID, swapName, initiatorMasterJSONPath):
    while True:
        tree = clean_file_open(SigmaParticlePath + swapName + "/ergoTree", "r")
        treeToAddrCmd = \
                "cd " + SigmaParticlePath + "treeToAddr && ./deploy.sh " + tree
        addr = json.loads(os.popen(treeToAddrCmd).read())["address"]
        boxFilterCmd = \
                "cd " + SigmaParticlePath + "boxFilter && " + \
                "./deploy.sh " + addr + " " + boxID + " ../../../" + swapName + "/atomicClaim"
        os.popen(boxFilterCmd).read()
        if os.path.isfile(swapName + "/atomicClaim_tx1") == True:
            j = json.loads(clean_file_open(swapName + "/atomicClaim_tx1", "r"))
            R4 = j["outputs"][0]["additionalRegisters"]["R4"]
            sr_list = [{"sr":R4}]
            json_tools.keyVal_list_update(sr_list, initiatorMasterJSONPath)
#            print("atomic swap was claimed by responder!")
            return True
        else:
#            print("no atomic swap claim found...")
            time.sleep(5)
            continue
            
def deduceX_fromAtomicSchnorrClaim(initiatorMasterJSONPath, swapName):
    masterJSON = json.loads(clean_file_open(initiatorMasterJSONPath, "r"))
    sr_ = masterJSON["sr_"]
    responderContractAddr = masterJSON["responderContractAddr"] 
    responderLocalChain = masterJSON["responderLocalChain"]
    enc_sr = masterJSON["sr"]
    decode_sr_cmd = \
            "cd " + SigmaParticlePath + "valFromHex && ./deploy.sh " + enc_sr + " ../../../" + swapName + "/decoded_sr.bin"
    decode = os.popen(decode_sr_cmd).read()
    sr = clean_file_open(swapName + "/decoded_sr.bin", "r")
    deduction_cmd = \
            "cd " + SigmaParticlePath + "AtomicMultiSigECC && python3 -u py/deploy.py p1Deduce " + sr_ + " " + sr
    deduction_response = os.popen(deduction_cmd).read()
    deduction_j = json.loads(deduction_response)
    x = deduction_j["x"]
    deduction_list = [{"x":x}]
    json_tools.keyVal_list_update(deduction_list, initiatorMasterJSONPath)
    return x



    
