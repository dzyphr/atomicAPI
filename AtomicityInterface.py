import os, ast
from file_tools import *
Atomicity = "EVM/Atomicity/"

def Atomicity_CheckContractFunds(j_response):
    chain = j_response["chain"]
    contractAddr = j_response["contractAddr"]
    if chain == "Sepolia":
        value = os.popen("cd Atomicity/Sepolia && python3 -u py/deploy.py getBalance " + contractAddr).read()
        return value

def buildScalarContract(chain, counterpartyChainPub, xG, locktimeDuration, swapName):
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
