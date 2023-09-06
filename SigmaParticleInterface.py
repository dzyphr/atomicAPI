import json, ast, os, time
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

def responderClaimAtomicSchnorr(swapName, DEC_finalizationPATH, responderMasterJSONPATH):
    if os.path.isfile(DEC_finalizationPATH) == False:
        print("finalization path is not a file! check filepath")
    else:
        claimContractGeneration = "cd SigmaParticle && ./new_frame " + swapName
        gen = os.popen(claimContractGeneration).read()
        importBoilerplate = "cp " + SigmaParticlePath + "/AtomicMultiSig/py/main.py " + SigmaParticlePath + swapName + "/py/main.py"
        imp = os.popen(importBoilerplate).read()
        sr = json.loads(clean_file_open(DEC_finalizationPATH, "r"))["sr"]

        




def deployErgoContract(swapName):
    command = "cd " + SigmaParticlePath + swapName + " && ./deploy.sh deposit"
    os.popen(command).read()

def getBoxID(swapName):
    return clean_file_open(SigmaParticlePath + swapName + "/boxId", "r")

def checkBoxValue(boxID, boxValPATH):
    while True:
        cmd = "cd " + SigmaParticlePath + "/boxValue/ && ./deploy.sh " + boxID + " " + "../../../" + boxValPATH
        os.popen(cmd).read()
        response = clean_file_open(boxValPATH, "r")
        print("response:", response)
        if "error" in str(response) or type(response) == type(None):
            time.sleep(5)
            continue
        else:
            return response #returns box value in nano Ergs (nΣ)
            break
