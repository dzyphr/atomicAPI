import json, ast, os, time, subprocess
from file_tools import *
py = "python3 -u "
SigmaParticlePath = "Ergo/SigmaParticle/"
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
AtomicSwapPath = "Ergo/SigmaParticle/AtomicMultiSig/"

def BuildAtomicSchnorrContract(initiatorMasterJSONPath, refundDuration_BLOCKS, swapName, valueERGO):
    j = json.loads(clean_file_open(initiatorMasterJSONPath, "r"))
    krG = ast.literal_eval(j["krG"])
    srG = ast.literal_eval(j["srG"])
    ssG = ast.literal_eval(j["ssG"])
    ksG = ast.literal_eval(j["ksG"])
    responderChainPubKey = j["responderErgoChainPubKey"]
    initiatorEIP3Secret = j["initiatorEIP3Secret"]
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

def responderClaimAtomicSchnorr(swapName, DEC_finalizationPATH, responderMasterJSONPATH, boxValue, tries=None):
    if os.path.isfile(DEC_finalizationPATH) == False:
        print("finalization path is not a file! check filepath")
    else:
        rounds = 0
        if tries == None:
            rounds = 60
        elif type(tries) != int:
            print("tries must be int! defaulting to 60 tries")
            rounds = 60
        else:
            rounds = tries
        claimContractGeneration = "cd " + SigmaParticlePath + " && ./new_frame " + swapName
        gen = os.popen(claimContractGeneration).read()
        importBoilerplate = "cp " + SigmaParticlePath + "/AtomicMultiSig/py/main.py " + SigmaParticlePath + swapName + "/py/main.py"
        imp = os.popen(importBoilerplate).read()
        finalization = json.loads(clean_file_open(DEC_finalizationPATH, "r"))
        master = json.loads(clean_file_open(responderMasterJSONPATH, "r"))
        ss = finalization["ss"]
        sr = master["sr"]
        krG = master["krG"]
        ksG = master["ksG"]
        boxID = finalization["boxId"]
        nanoErgs = boxValue
        echoVariablesCMD = \
            "echo \"" + \
            "sr=" + sr + "\n" + \
            "ss=" + ss + "\n" + \
            "ksGX=" + str(ast.literal_eval(ksG)[0]) + "\n" + \
            "ksGY=" + str(ast.literal_eval(ksG)[1]) + "\n" + \
            "krGX=" + str(ast.literal_eval(krG)[0]) + "\n" + \
            "krGY=" + str(ast.literal_eval(krG)[1]) + "\n" + \
            "atomicBox=" + "\"" + boxID + "\"\n" + \
            "ergoAmount=" + str(nanoErgs) + "\n" + \
            "\" >> " + SigmaParticlePath + swapName + "/.env"
        os.popen(echoVariablesCMD).read()
        claimCMD = \
                "cd " + SigmaParticlePath + swapName + " && ./deploy.sh claim"
        while rounds > 0:
            response = os.popen(claimCMD).read()
            print("response:\n", response)
            if response == None:
                rounds = rounds - 1
                time.sleep(5)
                continue
            else:
                return response

def updateKeyEnv(swapName, targetKeyEnvDirName):
    update = clean_file_open(SigmaParticlePath + targetKeyEnvDirName + "/.env", "r")
    update.replace("[default]", "")
    cmd = \
            "echo \"" + update + "\"" + " >> " + SigmaParticlePath + swapName + "/.env"
    os.popen(cmd).read()
    

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
#        os.popen(cmd).read()
        response = clean_file_open(boxValPATH, "r")
        print("response:", response)
        if "error" in str(response) or type(response) == type(None):
            time.sleep(5)
            continue
        else:
            return response #returns box value in nano Ergs (nΣ)
            break
