import sys
import priceFeeds
import ast
import market_pricing
import json
import shutil
import configparser
import initiatorInterface
import responderInterface
import ElGamalInterface
import AtomicityInterface 
import SigmaParticleInterface 
import functional_tests
import json_tools
import time
import file_tools
import swap_tools
from ServerEndpoints import logInToPasswordEncryptedAccount_ServerEndpoint, publishNewOrderType_ServerEndpoint
from ClientEndpoints import submitEncryptedResponse_ClientEndpoint, requestEncryptedInitiation_ClientEndpoint, logInToPasswordEncryptedAccount_ClientEndpoint
from config_tools import firstRunCheck, updateMainEnv, initErgoAccountNonInteractive, initSepoliaAccountNonInteractive 
from bearerRESTAPIkeygen import generate_bearer_RESTAPI_key, add_RESTAPI_key_to_private_accepted_keys_JSON, starterAPIKeys, add_RESTAPI_key_to_public_accepted_keys_JSON
from passwordFileEncryption import proveEncEnvFilePasswordKnowledge
args = sys.argv

def test2pAtomicSwap(p1Chain1, p1Chain2, p2Chain1, p2Chain2):
    FT_ErgoToSepolia(p1Chain1, p1Chain2, p2Chain1, p2Chain2) 


#print("argslen: ", len(args))

if len(args) == 2:
    if args[1] == "firstRunCheck":
        firstRunCheck()
    if args[1] == "generateNewElGamalPubKey": #random q and g
        ElGamalInterface.generateNewElGamalPubKey()
    if args[1] == "generate_bearer_RESTAPI_key":
        generate_bearer_RESTAPI_key()
    if args[1] == "generate_bearer_RESTAPI_key_add_to_private_accepted":
        add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if args[1] == "generate_bearer_RESTAPI_key_add_to_public_accepted":
        add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if args[1] == "generate_starter_RESTAPI_key":
        starterAPIKeys(add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key()))
    if args[1] == "scanAllSwapStates":
        swap_tools.scanAllSwapStates()
    if args[1] == "marketPricingLoop":
        market_pricing.marketPricingLoop()
elif len(args) == 3:
    if args[1] == "BitPandaPrice":
        print(priceFeeds.BitPandaPrice(args[2]))
    if args[1] == "BitPandaPriceRounded":
        print(priceFeeds.BitPandaPrice(args[2], rounded=True))
    if args[1] == "CoinGeckoAvgPrice":
        print(priceFeeds.CoinGeckoAvgPrice(args[2]))
    if args[1] == "CoinGeckoSimplePrice":
        print(priceFeeds.CoinGeckoSimplePrice(args[2]))
    if args[1] == "CoinGeckoSimplePriceRounded":
        print(priceFeeds.CoinGeckoSimplePrice(args[2], rounded=True))
    if args[1] == "KucoinPrice":
        print(priceFeeds.KucoinPrice(args[2]))
    if args[1] == "KucoinPriceRounded":
        print(priceFeeds.KucoinPrice(args[2], rounded=True))
    if args[1] == "CoinExPriceLowHighAvg":
        print(priceFeeds.CoinExPriceLowHighAvg(args[2]))
    if args[1] == "CoinExPriceLowHighAvgRounded":
        print(priceFeeds.CoinExPriceLowHighAvg(args[2], rounded=True))
    if args[1] == "CoinExPriceLast":
        print(priceFeeds.CoinExPriceLast(args[2]))
    if args[1] == "CoinExPriceLastRounded":
        print(priceFeeds.CoinExPriceLast(args[2], rounded=True))
    if args[1] == "CoinExPriceLow":
        print(priceFeeds.CoinExPriceLow(args[2]))
    if args[1] == "CoinExPriceLowRounded":
        print(priceFeeds.CoinExPriceLow(args[2], rounded=True))
    if args[1] == "CoinExPriceHigh":
        print(priceFeeds.CoinExPriceHigh(args[2]))
    if args[1] == "CoinExPriceHighRounded":
        print(priceFeeds.CoinExPriceHigh(args[2], rounded=True))
    if args[1] == "KrakenPriceAsk":
        print(priceFeeds.KrakenPrice(args[2], kind="ask"))
    if args[1] == "KrakenPriceAskRounded":
        print(priceFeeds.KrakenPrice(args[2], kind="ask", rounded=True))
    if args[1] == "KrakenPriceBid":
        print(priceFeeds.KrakenPrice(args[2], kind="bid"))
    if args[1] == "KrakenPriceBidRounded":
        print(priceFeeds.KrakenPrice(args[2], kind="bid", rounded=True))
    if args[1] == "KrakenPriceVWAP":
        print(priceFeeds.KrakenPrice(args[2], kind="vwap"))
    if args[1] == "KrakenPriceVWAPRounded":
        print(priceFeeds.KrakenPrice(args[2], kind="vwap", rounded=True))
    if args[1] == "KrakenPriceLast":
        print(priceFeeds.KrakenPrice(args[2], kind="last"))
    if args[1] == "KrakenPriceLastRounded":
        print(priceFeeds.KrakenPrice(args[2], kind="last", rounded=True))
    if args[1] == "KrakenPriceLow":
        print(priceFeeds.KrakenPrice(args[2], kind="low"))
    if args[1] == "KrakenPriceLowRounded":
        print(priceFeeds.KrakenPrice(args[2], kind="low", rounded=True))
    if args[1] == "KrakenPriceHigh":
        print(priceFeeds.KrakenPrice(args[2], kind="high"))
    if args[1] == "KrakenPriceHighRounded":
        print(priceFeeds.KrakenPrice(args[2], kind="high", rounded=True))
    if args[1] == "KrakenPriceLowHighAvg":
        print(priceFeeds.KrakenPrice(args[2], kind="lowhighavg"))
    if args[1] == "KrakenPriceLowHighAvgRounded":
        print(priceFeeds.KrakenPrice(args[2], kind="lowhighavg", rounded=True))
    if args[1] == "CoinbasePriceSpot":
        print(priceFeeds.CoinbasePrice(args[2], kind="spot"))
    if args[1] == "CoinbasePriceSpotRounded":
        print(priceFeeds.CoinbasePrice(args[2], kind="spot", rounded=True))
    if args[1] == "CoinbasePriceBuy":
        print(priceFeeds.CoinbasePrice(args[2], kind="buy"))
    if args[1] == "CoinbasePriceBuyRounded":
        print(priceFeeds.CoinbasePrice(args[2], kind="buy", rounded=True))
    if args[1] == "CoinbasePriceSell":
        print(priceFeeds.CoinbasePrice(args[2], kind="sell"))
    if args[1] == "CoinbasePriceSellRounded":
        print(priceFeeds.CoinbasePrice(args[2], kind="sell", rounded=True))
    if args[1] == "BinancePrice":
        print(priceFeeds.BinancePrice(args[2]))
    if args[1] == "BinancePriceRounded":
        print(priceFeeds.BinancePrice(args[2], rounded=True))
    if args[1] == "generate_bearer_RESTAPI_key":
        generate_bearer_RESTAPI_key(length=args[2])
    if args[1] == "generate_bearer_RESTAPI_key_add_to_private_accepted":
        add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key(length=args[2]))
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine":
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(args[2])
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(args[2])
    if args[1] == "Responder_CheckLockTimeRefund":
        responderInterface.Responder_CheckLockTimeRefund(args[2])
    if args[1] == "SigmaParticle_box_to_addr":
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2]))
    if args[1] == "generateNewElGamalPubKey": #specific q
        ElGamalInterface.generateNewElGamalPubKey(q=args[2])
    if args[1] == "watchSwapLoop":
        swap_tools.watchSwapLoop(args[2])
elif len(args) == 4:
    if args[1] == "SigmaParticle_box_to_addr":
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2], args[3]))
    if args[1] == "Responder_CheckLockTimeRefund":
        responderInterface.Responder_CheckLockTimeRefund(args[2], password=args[3])
    if args[1] == "updateMainEnv":
        updateMainEnv(args[2], args[3])
    if args[1] == "init":
        accountName = args[2]
        chain = args[3]
        config_tools.initializeAccount(accountName, chain)
    if args[1] == "generateNewElGamalPubKey": #specific q and g
        q = args[2]
        g = args[3]
        ElGamalInterface.generateNewElGamalPubKey(q=q, g=g)
    if args[1] == "proveEncEnvFilePasswordKnowledge":
        proveEncEnvFilePasswordKnowledge(args[2], args[3])
    if args[1] == "GeneralizeENC_ResponseSubroutine_hotreload":
        responderInterface.GeneralizeENC_ResponseSubroutine(args[2], "", "", "", "", "", "", "", hotReloadSwapState=args[3])
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine_hotreload":
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(args[2], hotReloadSwapState=args[3])
    if args[1] == "watchSwapLoop_localEncOnly":
        swap_tools.watchSwapLoop(args[2], localChainAccountPassword=args[3])
    if args[1] == "watchSwapLoop_crossEncOnly":
        swap_tools.watchSwapLoop(args[2], crossChainAccountPassword=args[3])
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine_localENCOnly":
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(
                args[2], localchainpassword=args[3]
        )
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine_crossENCOnly":
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(
                args[2], crosschainpassword=args[3]
        )
elif len(args) == 5:
    if args[1] == "SigmaParticle_box_to_addr":
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2], args[3], password=args[4]))
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(args[2], localchainpassword=args[3], crosschainpassword=args[4])
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine":
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(\
                args[2], \
                localChainAccountPassword=args[3], \
                crossChainAccountPassword=args[4]\
        )

    if args[1] == "requestEncryptedInitiation_ClientEndpoint":
        requestEncryptedInitiation_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "submitEncryptedResponse_ClientEndpoint":
        submitEncryptedResponse_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(args[2], args[3], args[4])
    if args[1] == "ElGamal_decrypt":
        sys.stdout.write(ElGamalInterface.ElGamal_Decrypt(args[2], args[3], args[4]))#subjectFilePath, senderPubKey, userKeyFileName
    if args[1] == "checkBoxValue":
        sys.stdout.write(SigmaParticleInterface.checkBoxValue(args[2], args[3], args[4]))#boxID, boxValPATH, swapName
    if args[1] == "watchSwapLoop":
        swap_tools.watchSwapLoop(args[2], localChainAccountPassword=args[3], crossChainAccountPassword=args[4])
elif len(args) == 6:
    if args[1] == "logInToPasswordEncryptedAccount_Server":
        logInToPasswordEncryptedAccount_ServerEndpoint(args[2], args[3], args[4], args[5])
    if args[1] == "logInToPasswordEncryptedAccount_Client":
        logInToPasswordEncryptedAccount_ClientEndpoint(args[2], args[3], args[4], args[5])
    if args[1] == "test2pAtomicSwap":
        test2pAtomicSwap(args[2], args[3], args[4], args[5])
    if args[1] == "GeneralizeENC_ResponseSubroutine_hotreload":
        responderInterface.GeneralizeENC_ResponseSubroutine(
                args[2], "", "", "", "", "", "", "", 
                localChainAccountPassword=args[3], crossChainAccountPassword=args[4], hotReloadSwapState=args[5]
        )
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine_hotreload":
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(
                args[2], localChainAccountPassword=args[3], crossChainAccountPassword=args[4], hotReloadSwapState=args[5]
        )
    if args[1] == "GeneralizedENC_FinalizationSubroutine_crossENCOnly":#initiator refund checking starts here
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                args[2], args[3], args[4], crosschainpassword=args[5]
        )
    if args[1] == "GeneralizedENC_FinalizationSubroutine_localENCOnly":#initiator refund checking starts here
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                args[2], args[3], args[4], localchainpassword=args[5]
        )
elif len(args) == 7:
    if args[1] == "checkBoxValue":
        sys.stdout.write(SigmaParticleInterface.checkBoxValue(\
                args[2], args[3], args[4], ergopassword=args[5], \
                otherchainpassword=args[6]\
        ))#boxID, boxValPATH, swapName, password
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                args[2], args[3], args[4], localchainpassword=args[5], crosschainpassword=args[6]
        )
    if args[1] == "UpdateMarketOrderTypeUUIDsList":
        market_pricing.UpdateMarketOrderTypeUUIDsList(
            coins=ast.literal_eval(args[2]), 
            marketConfigJSON=args[3], 
            marketFeePercentage=args[4], 
            coinAVolumeMinMax=ast.literal_eval(args[5]), 
            rounded=ast.literal_eval(args[6])
        )
elif len(args) == 9:
    if args[1] == "GeneralizedENCInitiationSubroutine":    
        initiatorInterface.GeneralizedENC_InitiationSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8])
    if args[1] == "initErgoAccountNonInteractive":
        initErgoAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7],  args[8])
elif len(args) == 10:
    if args[1] == "initSepoliaAccountNonInteractive":
        initSepoliaAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "publishNewOrderType_ServerEndpoint":
        publishNewOrderType_ServerEndpoint(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "GeneralizeENC_ResponseSubroutine":
        responderInterface.GeneralizeENC_ResponseSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "GeneralizedENCInitiationSubroutine_crossENCOnly":
        initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                args[2], args[3], args[4], args[5], \
                args[6], args[7], args[8], crossChainAccountPassword=args[9])
    if args[1] == "GeneralizedENCInitiationSubroutine_localENCOnly":
        initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                args[2], args[3], args[4], args[5], \
                args[6], args[7], args[8], localChainAccountPassword=args[9])
elif len(args) == 11:
    if args[1] == "initErgoAccountNonInteractive_ENC":
        initErgoAccountNonInteractive(
            args[2], args[3], args[4], args[5], args[6], args[7], \
            args[8], args[9], password=args[10], enc=True\
        )
    if args[1] == "GeneralizedENCInitiationSubroutine":
        initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                args[2], args[3], args[4], args[5], \
                args[6], args[7], args[8], localChainAccountPassword=args[9], crossChainAccountPassword=args[10])
    if args[1] == "initSepoliaAccountNonInteractive_ENC": #TODO get rid of ID scan and compiler version args
        initSepoliaAccountNonInteractive(
            args[2], args[3], args[4], args[5], args[6], args[7],
            args[8], args[9], enc=True, password=args[10]
        )
    if args[1] == "GeneralizeENC_ResponseSubroutine_localEncOnly":
        responderInterface.GeneralizeENC_ResponseSubroutine(
                args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9],
                accountPasswordList=ast.literal_eval([args[10]])
        )
    if args[1] == "GeneralizeENC_ResponseSubroutine_crossEncOnly":
        responderInterface.GeneralizeENC_ResponseSubroutine(
                args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9],
                accountPasswordList=ast.literal_eval(["", args[10]])
        )
elif len(args) == 12:
    if args[1] == "GeneralizeENC_ResponseSubroutine": #both acc enc
        responderInterface.GeneralizeENC_ResponseSubroutine(
                args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9],
                accountPasswordList=ast.literal_eval([args[10], args[11]])
        )
