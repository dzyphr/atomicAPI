import sys
import json
import shutil
import configparser
from initiatorInterface import *
from responderInterface import *
from ElGamalInterface import *
from AtomicityInterface import * 
from SigmaParticleInterface import *
from functional_tests import *
import json_tools
import time
args = sys.argv


def test():
    FT_ErgoToSepolia()

if len(args) >= 1:
    if args[1] == "test":
        test()
