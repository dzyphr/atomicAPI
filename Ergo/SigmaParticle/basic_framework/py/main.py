import os, json, sys, time, random, jpype, java.lang, waits, coinSelection, scalaPipe, scala.math.BigInt as BigInt, file_tools
from jpype import *
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
from ergpy import helper_functions, appkit
from sigmastate.interpreter.CryptoConstants import *
from java.math import BigInteger
from sigmastate.eval.package import ecPointToGroupElement
interpreterClasspath = \
    "/home/" + os.getlogin() + "/Downloads/sigmastate-interpreter/target/scala-2.13/sigma-state-assembly-5.0.14.jar"
jpype.addClassPath(interpreterClasspath)

def main(contractName, ergo, wallet_mnemonic, mnemonic_password, senderAddress, senderEIP3Secret, args):
    print("Running", contractName)
    def atomicDeposit(verifyTreeOnly=None, password=""):
        sender = senderAddress[0]
        castedSender = ergo.castAddress(senderAddress[0])
        senderAddr = ""
        #prob public
        ergoAmountRaw = int(os.getenv('ergoAmount'))
        receiver = Address.create(os.getenv('receiverAddr'))
        senderPubkey = senderAddress
#        senderEIP3Secret = int(senderEIP3Secret)
        senderWalletMnemonic = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
        senderProver = ergo._ctx.newProverBuilder().withMnemonic(senderWalletMnemonic[0]).withEip3Secret(int(senderEIP3Secret)).build()
        if verifyTreeOnly != None:
            if verifyTreeOnly == True:
                senderPubkey = Address.create(os.getenv('senderAddr')).getPublicKey()
        else:
            senderPubkey = Address.create(sender).getPublicKey()
#        senderWalletMnemonic = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
#        senderEIP3Secret = int(os.getenv('senderEIP3Secret'))
#        senderProver = ergo._ctx.newProverBuilder().withMnemonic(senderWalletMnemonic[0]).withEip3Secret(senderEIP3Secret).build()
#        ergoAmountRaw = int(os.getenv('ergoAmount'))
        ergoAmount = ergoAmountRaw 
        ergoAmountFeeIncluded = ergoAmount #+ Parameters.MinFee #fee seems to include itself
        if ergoAmountFeeIncluded <= 123841 + Parameters.MinFee: #if someone tries to deposit lower than the fee it cannot be profitably spent
            #if they deposit more than the minimum + fee the fee can be taken from the box when claiming or withdrawing
            #IRL dont spend such low amounts because fees will always be more than the amount itself just for testing purposes
            ergoAmountFeeIncluded = ergoAmountFeeIncluded + Parameters.MinFee
        ECC_Generator = dlogGroup().generator().getEncoded(True)

        #Public Key Points for coordinating / proof of nonces specific to swap
        krGX = BigInteger(os.getenv('krGX'))
        krGY = BigInteger(os.getenv('krGY'))
        krG = dlogGroup().curve().createPoint(krGX, krGY)
        GE_krG = ecPointToGroupElement(krG)
        ksGX = BigInteger(os.getenv('ksGX'))
        ksGY = BigInteger(os.getenv('ksGY'))
        ksG = dlogGroup().curve().createPoint(ksGX, ksGY)
        GE_ksG = ecPointToGroupElement(ksG)

        #Public Key Points for claiming / proof of swap finality
#        if verifyTreeOnly == None or verifyTreeOnly == False:
        srGX = BigInteger(os.getenv('srGX'))
        srGY = BigInteger(os.getenv('srGY'))
        srG = dlogGroup().curve().createPoint(srGX, srGY)
        GE_srG = ecPointToGroupElement(srG)
        ssGX = BigInteger(os.getenv('ssGX'))
        ssGY = BigInteger(os.getenv('ssGY'))
        ssG = dlogGroup().curve().createPoint(ssGX, ssGY)
        GE_ssG = ecPointToGroupElement(ssG)
#        receiver = Address.create(os.getenv('receiverAddr'))
        lockHeight = ""
        if verifyTreeOnly != None:
            if verifyTreeOnly == True:
                print("verifying tree")
                lockHeight = int(os.getenv('staticLockHeight'))
                strlockHeight = str(lockHeight)
        else:
            lockHeight = ergo._ctx.getHeight() + int(os.getenv('refundDuration')) #irl set relatively large height on BOTH sides of swap for max cooperation
            strlockHeight = str(lockHeight)
        atomicLockScript = \
            "{ \
                val srBYTES = OUTPUTS(0).R4[Coll[Byte]].get; \
                val sr = byteArrayToBigInt(srBYTES); \
                val ssBYTES = OUTPUTS(0).R5[Coll[Byte]].get;  \
                val ss = byteArrayToBigInt(ssBYTES);   \
                val receiver_krG = OUTPUTS(0).R6[GroupElement].get;  \
                val receiver_ksG = OUTPUTS(0).R7[GroupElement].get;   \
                val G = decodePoint(generator);   \
                sigmaProp(   \
                    receiver &&   \
                    G.exp(sr) == srG &&  \
                    G.exp(ss) == ssG &&  \
                    receiver_krG == krG &&   \
                    receiver_ksG == ksG ||   \
                    sender && (HEIGHT > lockHeight)   \
                )   \
            }" 
        AtomicContract = ergo._ctx.compileContract( \
                ConstantsBuilder.create()\
                .item("receiver", receiver.getPublicKey())\
                .item("sender", senderPubkey)\
                .item("srG", srG)\
                .item("ssG", ssG)\
                .item("krG", krG)\
                .item("ksG", ksG)\
                .item("generator", ECC_Generator)\
                .item("lockHeight", int(strlockHeight))\
                .build(),
                atomicLockScript)
        ergoTree = AtomicContract.getErgoTree().bytesHex()
        file_tools.clean_file_open("ergoTree", "w", str(ergoTree))
        '''
        f = open("ergoTree", "w")
        f.write(str(ergoTree))
        f.close()
        '''
        if verifyTreeOnly != None:
            if verifyTreeOnly == True:
                exit()
#        print(dir(ergo))
        #TODO Optionally get boxes from this extraIndex (not certain needs extraIndex yet) node endpoint:
        #http://127.0.0.1:9052/blockchain/box/unspent/byAddress/ ADDRESS ?offset=0&limit=20&sortDirection=asc
        #also TODO deal with double spends from client side to avoid double spending error from naive box choice
        inputBoxes = BoxOperations.createForSender(Address.create(sender), ergo._ctx).withAmountToSpend(ergoAmountFeeIncluded).loadTop()
#        inputBoxes =  ergo.getInputBox(sender_address=castedSender, amount_list=[ergoAmountRaw], tokenList=None)
        AtomicBox = ergo._ctx.newTxBuilder().outBoxBuilder() \
            .value(ergoAmountFeeIncluded) \
            .contract(AtomicContract)\
            .build()
        unsignedTx = ergo.buildUnsignedTransaction(\
            input_box =coinSelection.pruneToIndex(1, inputBoxes) , outBox=[AtomicBox],\
            sender_address=castedSender\
        )
        signedTx = senderProver.sign(unsignedTx)
        ergo.txId(signedTx) #DEPOSIT
        signedTxJSON = senderProver.sign(unsignedTx).toJson(True)
#        sys.stdout.write(str(signedTxJSON))
        j = json.loads(str(signedTxJSON))
        print(j["outputs"][0]["boxId"])
        '''
        f = open("boxId", "w")
        f.write(j["outputs"][0]["boxId"]) 
        f.close()
        f = open("lockHeight", "w")
        f.write(strlockHeight)
        f.close()
        '''
        file_tools.clean_file_open("boxId", "w", j["outputs"][0]["boxId"])
        file_tools.clean_file_open("lockHeight", "w", strlockHeight)


    def atomicReceiverClaim():
        receiver = senderAddress[0]
        castedReceiver = ergo.castAddress(senderAddress[0])
        receiverPubkey = Address.create(receiver).getPublicKey()
        receiverWalletMnemonic = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
        receiverEIP3Secret = int(senderEIP3Secret)
        receiverProver = ergo._ctx.newProverBuilder().withMnemonic(receiverWalletMnemonic[0]).withEip3Secret(receiverEIP3Secret).build()
        atomicBoxID = os.getenv('atomicBox')
#        ergoAmountRaw = int(os.getenv('ergoAmount'))
#        ergoAmountFeeSubtracted = ergoAmountRaw - Parameters.MinFee
        krGX = BigInteger(os.getenv('krGX'))
        krGY = BigInteger(os.getenv('krGY'))
        krG = ecPointToGroupElement(dlogGroup().curve().createPoint(krGX, krGY))
        ev_krG = ErgoValue.of(krG)
        ksGX = BigInteger(os.getenv('ksGX'))
        ksGY = BigInteger(os.getenv('ksGY'))
        ksG = ecPointToGroupElement(dlogGroup().curve().createPoint(ksGX, ksGY))
        ev_ksG = ErgoValue.of(ksG)
        sr = BigInteger(os.getenv('sr'))
        sr_array =  BigInt.javaBigInteger2bigInt(sr).toByteArray()
        ev_sr_array = ErgoValue.of(sr_array)
        ss = BigInteger(os.getenv('ss'))
        ss_array =  BigInt.javaBigInteger2bigInt(ss).toByteArray()
        ev_ss_array = ErgoValue.of(ss_array)
        receiverErgoTree = ErgoTreeContract(castedReceiver.getErgoAddress().script(), ergo._networkType)
        unlockBox = ergo._ctx.newTxBuilder().outBoxBuilder() \
            .value(java.util.Arrays.asList(ergo._ctx.getBoxesById(atomicBoxID))[0].getValue() - Parameters.MinFee) \
            .contract(receiverErgoTree)\
            .registers([ev_sr_array, ev_ss_array, ev_krG, ev_ksG])\
            .build()
        inputBoxes = java.util.Arrays.asList(ergo._ctx.getBoxesById(atomicBoxID))
        unsignedTx = ergo.buildUnsignedTransaction(\
            input_box = inputBoxes, outBox=[unlockBox],\
            sender_address=castedReceiver\
        )
        signedTx = receiverProver.sign(unsignedTx)
        ergo.txId(signedTx) #CLAIM
        signedTxJSON = receiverProver.sign(unsignedTx).toJson(True)
        sys.stdout.write(str(signedTxJSON))

    def atomicSenderRefund():
        sender = senderAddress[0]
        castedSender = ergo.castAddress(senderAddress[0])
        senderPubkey = Address.create(sender).getPublicKey()
        senderWalletMnemonic = ergo.getMnemonic(wallet_mnemonic, mnemonic_password=mnemonic_password)
        senderEIP3Secret = int(os.getenv('senderEIP3Secret'))
        senderProver = ergo._ctx.newProverBuilder().withMnemonic(senderWalletMnemonic[0]).withEip3Secret(senderEIP3Secret).build()
        senderErgoTree = ErgoTreeContract(castedSender.getErgoAddress().script(), ergo._networkType)
        atomicBoxID = str(os.getenv('atomicBox'))
        refundBox = ergo._ctx.newTxBuilder().outBoxBuilder() \
            .value(java.util.Arrays.asList(ergo._ctx.getBoxesById(atomicBoxID))[0].getValue() - Parameters.MinFee) \
            .contract(senderErgoTree)\
            .registers([ 
                ErgoValue.of(BigInt.javaBigInteger2bigInt(BigInteger("0")).toByteArray()), \
                ErgoValue.of(BigInt.javaBigInteger2bigInt(BigInteger("0")).toByteArray()), \
                ErgoValue.of(dlogGroup().generator()), \
                ErgoValue.of(dlogGroup().generator())
            ]).build()
        inputBoxes = java.util.Arrays.asList(ergo._ctx.getBoxesById(atomicBoxID))
        unsignedTx = ergo.buildUnsignedTransaction(\
            input_box = inputBoxes, outBox=[refundBox],\
            sender_address=castedSender\
        )
        signedTx = senderProver.sign(unsignedTx)
        ergo.txId(signedTx) #REFUND (after timelock height)
        signedTxJSON = senderProver.sign(unsignedTx).toJson(True)
        sys.stdout.write(str(signedTxJSON))


        

    




    if len(args) > 1:
        if args[1] == "deposit":
            if len(args) >= 3:
                if args[2] == "verifyTreeOnly":
                    atomicDeposit(verifyTreeOnly=True)
                    exit()
            atomicDeposit()
        elif args[1] == "claim":
            atomicReceiverClaim()
        elif args[1] == "refund":
            atomicSenderRefund()
        else:
            print("unknown arg.\nchoices: deposit, claim, refund")
    else:
        print("enter argument.\nchoices: deposit, claim, refund")

