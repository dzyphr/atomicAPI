import os

py = "python3 -u "
AtomicSwapECCPath = "Ergo/SigmaParticle/AtomicMultiSigECC/py/deploy.py " #TODO Ergo Specific
s_ = " "

def initiation(crossChainPubKey, initiatorChain): #returns an initiation JSON object #TODO link between selected chain and atomic ECC
    return os.popen(py + AtomicSwapECCPath + "p1Initiate " + crossChainPubKey + s_ + initiatorChain).read()

