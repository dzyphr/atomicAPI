import secrets 
from jpype import *
import numpy as np
import hashlib
import ECC
from ECC import *
import os
import json
import base64
import time
import random
from dotenv import load_dotenv
import org.ergoplatform
import sigmastate
from sigmastate.interpreter.CryptoConstants import * 
from java.math import BigInteger
#from ergo_python_appkit.appkit import *
#from ergpy import helper_functions, appkit
import waits
import coinSelection
import scalaPipe
import sys
import ast
#ERGO ECC ADD point.add(point)
#ERGO ECC MULTIPLY G dlogGroup().generator().multiply(scalar) 
#[IN ERGOSCRIPT(on chain script) MULTIPLY IS Generator.exp(scalar)] because generator is GroupElement

def p1Deduce(sr_, sr):
    p1x = int(sr_) - int(sr)  #p1 discovers x this way
    xObj = {
        "x": str(p1x)
    }
    return json.dumps(xObj, indent=4)


def main(args):
    #Basic Variables
    curve = dlogGroup()
    n =  int(str(curve.order()))
    g = ECC.curve.g
    javaBigIntegerMAX = 57896044618658097711785492504343953926634992332820282019728792003956564819968
#    message = "1000000000" #some public change output #TODO:MAKE THIS MODULAR BEFORE PRODUCTION
    sha256 = hashlib.sha256()


    def p1Initiate(crossChainPubkey, localChain, crossChain):
        if crossChainPubkey == "":
            print("enter chainPubkey as arg")
            exit(1)
        rs = random.randrange(0, n)
        rs = rs % n
def p1Deduce(sr_, sr):
        p1x = int(sr_) - int(sr)  #p1 discovers x this way
        xObj = {
            "x": str(p1x)
        }
        return json.dumps(xObj, indent=4)
        rs = rs % javaBigIntegerMAX
        rsERGO = BigInteger(str(rs))
        ks = random.randrange(0, n)
        ks = ks % n
        ks = ks % javaBigIntegerMAX
        ksERGO = BigInteger(str(ks))
        rsGERGO = dlogGroup().generator().multiply(rsERGO).normalize()
        ksG = scalar_mult(ks, g)
        ksGERGO = dlogGroup().generator().multiply(ksERGO).normalize()
        #return a JSON for easy cross lang/client parsing!
        label_crosschainpub = crossChain + "ChainPubkey"
        p1InitiateOBJECT =  {
            label_crosschainpub : crossChainPubkey,
            "initiatorLocalChain": localChain,
            "rsG": "(" + str(rsGERGO.getXCoord().toBigInteger()) + ", " + str(rsGERGO.getYCoord().toBigInteger()) + ")",
            "ksG": "(" + str(ksGERGO.getXCoord().toBigInteger()) + ", " + str(ksGERGO.getYCoord().toBigInteger()) + ")",
            "ks": ks, #must be stripped by client so it is not shared!
            "rs": rs #!!
        }
        return json.dumps(p1InitiateOBJECT, indent=4)

    def p2Response(ksGERGO, message, srFilePath, xFilePath):
        ksGERGO = ast.literal_eval(ksGERGO)
        ksGERGO_X = ksGERGO[0]
        ksGERGO_Y = ksGERGO[1]        
        ksGERGO = dlogGroup().curve().createPoint(BigInteger(str(ksGERGO_X)), BigInteger(str(ksGERGO_Y)))
        rr = random.randrange(0, n)
        rr = rr % n
        rr = rr % javaBigIntegerMAX
        rrERGO = BigInteger(str(rr))
        kr = random.randrange(0, n)
        kr = kr % n
        kr = kr % javaBigIntegerMAX
        krERGO = BigInteger(str(kr))
        krGERGO = dlogGroup().generator().multiply(krERGO).normalize()
        krG = scalar_mult(kr, g)
        rrG = scalar_mult(rr, g)
        hashContent = message.encode() + str(ksGERGO.add(krGERGO)).encode()
        sha256.update(hashContent)
        e = int(sha256.digest().hex(), 16)
        e = e % n
        e = e % javaBigIntegerMAX
        eERGO = BigInteger(str(int(sha256.digest().hex(), 16)))
        sr = kr + (e * rr)
        def gen_sr(kr, e, rr):
            sr = kr + (e * rr)
            sr = sr % n
            sr = sr % javaBigIntegerMAX
            while sr > javaBigIntegerMAX:
                rr = random.randrange(0, n)
                sr = kr + (e * rr)
                sr = sr % n
                sr = sr % javaBigIntegerMAX
                if sr < javaBigIntegerMAX:
                    return sr
                else: 
                    continue
            return sr 
        sr = gen_sr(kr, e, rr)
        srERGO = BigInteger(str(sr))
        f = open(srFilePath, "w")
        f.write(str(srERGO))
        f.close()
        x = secrets.randbits(256)
        x = x % n
        x = x % javaBigIntegerMAX
        f = open(xFilePath, "w")
        f.write(str(x))
        f.close()
        xERGO = BigInteger(str(x))
        xGERGO = dlogGroup().generator().multiply(xERGO).normalize()
        srGERGO = dlogGroup().generator().multiply(srERGO).normalize()#sr is on ERGO
        srG = scalar_mult(sr, g)
        xG = scalar_mult(x, g)#x is on EVM chain
        sr_ = sr + x
        sr_ = sr_  
        p2RespondOBJECT = {
                "sr_": str(sr_),
                "xG": str(xG),
                "srG": "(" + str(srGERGO.getXCoord().toBigInteger()) + ", " + str(srGERGO.getYCoord().toBigInteger()) + ")",
                "krG": "(" + str(krGERGO.getXCoord().toBigInteger())  + ", " + str(krGERGO.getYCoord().toBigInteger()) + ")",
                "e": str(e) #TODO:figure out if Ergo specific e is necessary above
                #TODO: make chain specific
        }
        return json.dumps(p2RespondOBJECT, indent=4)

    def p1Finalize(sr_, xG, srG,  e, ks, rs):
        sr_ = int(sr_)
        e = int(e)
        rs = int(rs)
        ks = int(ks)
        xG = ast.literal_eval(xG)
        srG = ast.literal_eval(srG)

        check = add_points(srG, xG) #P1 CHECKS WITH ECC
        sr_G = scalar_mult(sr_, g)
        assert(check == sr_G)
        ss = ks + e * rs
        ss = ss % n
        ss = ss % javaBigIntegerMAX
        ssERGO = BigInteger(str(ss))
        ssGERGO = dlogGroup().generator().multiply(ssERGO).normalize()
        finalSignatureObject = {
                "ss":  str(ssERGO),
                "ssG": "(" + str(ssGERGO.getXCoord().toBigInteger())  + ", " + str(ssGERGO.getYCoord().toBigInteger()) + ")"
        }
        return json.dumps(finalSignatureObject, indent=4)



    def p1Deduce(sr_, sr):
        p1x = int(sr_) - int(sr)  #p1 discovers x this way
        xObj = {
            "x": str(p1x)
        }
        return json.dumps(xObj, indent=4)
        #print("p1 can now spend value locked to hash/public pair xG with x and their signature")


    if len(args) > 1:
        command = args[1]
        if command == "p1Initiate":
            if len(args) > 2:
                if len(args) > 4:
                    sys.stdout.write(str(p1Initiate(args[2], args[3], args[4])))
                else:
                    print("followup args: [crossChainPubkey] [localChain] [crossChain]")
            else:
                print("enter chainPubkey as following arg")
        if command == "p2Respond":
            if len(args) > 3:
               sys.stdout.write(str(p2Response(args[2], args[3], args[4], args[5])))
            else:
                print("enter ksG, Message, srFilePath, and xFilePath as following args")
        if command == "p1Finalize":
            if len(args) > 4:
                sys.stdout.write(str(p1Finalize(args[2], args[3], args[4], args[5], args[6], args[7])))
            else:
                print("enter:\n sr_, xG, srG, e \nas followup arguments")
        if command == "p1Deduce":
            if len(args) > 3:
                sys.stdout.write(str(p1Deduce(args[2], args[3])))
            else:
                print("enter sr_ and sr as followup arguments")
#        else:
#            test()
    


























