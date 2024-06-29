import sys, priceFeeds, secrets, ast, market_pricing, json, shutil, configparser, config_tools, initiatorInterface, responderInterface
import ElGamalInterface, AtomicityInterface, SigmaParticleInterface, functional_tests, json_tools, json_tools, json_tools, swap_tools
from ServerEndpoints import logInToPasswordEncryptedAccount_ServerEndpoint, publishNewOrderType_ServerEndpoint
from ClientEndpoints import submitEncryptedResponse_ClientEndpoint, requestEncryptedInitiation_ClientEndpoint, logInToPasswordEncryptedAccount_ClientEndpoint
from config_tools import firstRunCheck, updateMainEnv, initErgoAccountNonInteractive, initSepoliaAccountNonInteractive 
from bearerRESTAPIkeygen import generate_bearer_RESTAPI_key, add_RESTAPI_key_to_private_accepted_keys_JSON, starterAPIKeys, add_RESTAPI_key_to_public_accepted_keys_JSON
from passwordFileEncryption import proveEncEnvFilePasswordKnowledge
from LOG import LOG
args = sys.argv

argstr =  " ".join(args)

def test2pAtomicSwap(p1Chain1, p1Chain2, p2Chain1, p2Chain2):
    FT_ErgoToSepolia(p1Chain1, p1Chain2, p2Chain1, p2Chain2) 

LOG('Atomic API Logger Started')

if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'CLI Args: {argstr}')

if len(args) == 2:
    if args[1] == "firstRunCheck":
        LOG('running firstRunCheck()')
        firstRunCheck()
    if args[1] == "generateNewElGamalPubKey": #random q and g
        LOG('running ElGamalInterface.generateNewElGamalPubKey()')
        ElGamalInterface.generateNewElGamalPubKey()
    if args[1] == "generate_bearer_RESTAPI_key":
        LOG('running generate_bearer_RESTAPI_key()')
        generate_bearer_RESTAPI_key()
    if args[1] == "generate_bearer_RESTAPI_key_add_to_private_accepted":
        LOG('running add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key())')
        add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if args[1] == "generate_bearer_RESTAPI_key_add_to_public_accepted":
        LOG('running add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key()')
        add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key())
    if args[1] == "generate_starter_RESTAPI_key":
        LOG('running starterAPIKeys(add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key()))')
        starterAPIKeys(add_RESTAPI_key_to_public_accepted_keys_JSON(generate_bearer_RESTAPI_key()))
    if args[1] == "scanAllSwapStates":
        LOG('running swap_tools.scanAllSwapStates()')
        swap_tools.scanAllSwapStates()
    if args[1] == "marketPricingLoop":
        LOG('running market_pricing.marketPricingLoop()')
        market_pricing.marketPricingLoop()
elif len(args) == 3:
    if args[1] == "BitPandaPrice":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.BitPandaPrice("{args[2]}")')
        print(priceFeeds.BitPandaPrice(args[2]))
    if args[1] == "BitPandaPriceRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.BitPandaPrice("{args[2]}", rounded=True)')
        print(priceFeeds.BitPandaPrice(args[2], rounded=True))
    if args[1] == "CoinGeckoAvgPrice":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinGeckoAvgPrice("{args[2]}")')
        print(priceFeeds.CoinGeckoAvgPrice(args[2]))
    if args[1] == "CoinGeckoSimplePrice":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinGeckoSimplePrice("{args[2]}")')
        print(priceFeeds.CoinGeckoSimplePrice(args[2]))
    if args[1] == "CoinGeckoSimplePriceRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinGeckoSimplePrice("{args[2]}", rounded=True)')
        print(priceFeeds.CoinGeckoSimplePrice(args[2], rounded=True))
    if args[1] == "KucoinPrice":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KucoinPrice("{args[2]}")')
        print(priceFeeds.KucoinPrice(args[2]))
    if args[1] == "KucoinPriceRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KucoinPrice("{args[2]}", rounded=True)')
        print(priceFeeds.KucoinPrice(args[2], rounded=True))
    if args[1] == "CoinExPriceLowHighAvg":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceLowHighAvg("{args[2]}")')
        print(priceFeeds.CoinExPriceLowHighAvg(args[2]))
    if args[1] == "CoinExPriceLowHighAvgRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceLowHighAvg("{args[2]}", rounded=True)')
        print(priceFeeds.CoinExPriceLowHighAvg(args[2], rounded=True))
    if args[1] == "CoinExPriceLast":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceLast("{args[2]}")')
        print(priceFeeds.CoinExPriceLast(args[2]))
    if args[1] == "CoinExPriceLastRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceLast("{args[2]}", rounded=True)')
        print(priceFeeds.CoinExPriceLast(args[2], rounded=True))
    if args[1] == "CoinExPriceLow":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceLow("{args[2]}")')
        print(priceFeeds.CoinExPriceLow(args[2]))
    if args[1] == "CoinExPriceLowRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceLow("{args[2]}", rounded=True)')
        print(priceFeeds.CoinExPriceLow(args[2], rounded=True))
    if args[1] == "CoinExPriceHigh":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceHigh("{args[2]}")')
        print(priceFeeds.CoinExPriceHigh(args[2]))
    if args[1] == "CoinExPriceHighRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinExPriceHigh("{args[2]}", rounded=True)')
        print(priceFeeds.CoinExPriceHigh(args[2], rounded=True))
    if args[1] == "KrakenPriceAsk":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="ask")')
        print(priceFeeds.KrakenPrice(args[2], kind="ask"))
    if args[1] == "KrakenPriceAskRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="ask", rounded=True)')
        print(priceFeeds.KrakenPrice(args[2], kind="ask", rounded=True))
    if args[1] == "KrakenPriceBid":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="bid")')
        print(priceFeeds.KrakenPrice(args[2], kind="bid"))
    if args[1] == "KrakenPriceBidRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="bid", rounded=True)')
        print(priceFeeds.KrakenPrice(args[2], kind="bid", rounded=True))
    if args[1] == "KrakenPriceVWAP":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="vwap")')
        print(priceFeeds.KrakenPrice(args[2], kind="vwap"))
    if args[1] == "KrakenPriceVWAPRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'runnng priceFeeds.KrakenPrice("{args[2]}", kind="vwap", rounded=True)')
        print(priceFeeds.KrakenPrice(args[2], kind="vwap", rounded=True))
    if args[1] == "KrakenPriceLast":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="last")')
        print(priceFeeds.KrakenPrice(args[2], kind="last"))
    if args[1] == "KrakenPriceLastRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="last", rounded=True)')
        print(priceFeeds.KrakenPrice(args[2], kind="last", rounded=True))
    if args[1] == "KrakenPriceLow":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="low")')
        print(priceFeeds.KrakenPrice(args[2], kind="low"))
    if args[1] == "KrakenPriceLowRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="low", rounded=True)')
        print(priceFeeds.KrakenPrice(args[2], kind="low", rounded=True))
    if args[1] == "KrakenPriceHigh":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="high")')
        print(priceFeeds.KrakenPrice(args[2], kind="high"))
    if args[1] == "KrakenPriceHighRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="high", rounded=True))')
        print(priceFeeds.KrakenPrice(args[2], kind="high", rounded=True))
    if args[1] == "KrakenPriceLowHighAvg":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="lowhighavg")')
        print(priceFeeds.KrakenPrice(args[2], kind="lowhighavg"))
    if args[1] == "KrakenPriceLowHighAvgRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.KrakenPrice("{args[2]}", kind="lowhighavg", rounded=True)')
        print(priceFeeds.KrakenPrice(args[2], kind="lowhighavg", rounded=True))
    if args[1] == "CoinbasePriceSpot":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinbasePrice("{args[2]}", kind="spot")')
        print(priceFeeds.CoinbasePrice(args[2], kind="spot"))
    if args[1] == "CoinbasePriceSpotRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinbasePrice("{args[2]}", kind="spot", rounded=True)')
        print(priceFeeds.CoinbasePrice(args[2], kind="spot", rounded=True))
    if args[1] == "CoinbasePriceBuy":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinbasePrice("{args[2]}", kind="buy")')
        print(priceFeeds.CoinbasePrice(args[2], kind="buy"))
    if args[1] == "CoinbasePriceBuyRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinbasePrice("{args[2]}", kind="buy", rounded=True')
        print(priceFeeds.CoinbasePrice(args[2], kind="buy", rounded=True))
    if args[1] == "CoinbasePriceSell":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinbasePrice("{args[2]}", kind="sell")')
        print(priceFeeds.CoinbasePrice(args[2], kind="sell"))
    if args[1] == "CoinbasePriceSellRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.CoinbasePrice("{args[2]}", kind="sell", rounded=True)')
        print(priceFeeds.CoinbasePrice(args[2], kind="sell", rounded=True))
    if args[1] == "BinancePrice":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.BinancePrice("{args[2]}")')
        print(priceFeeds.BinancePrice(args[2]))
    if args[1] == "BinancePriceRounded":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running priceFeeds.BinancePrice("{args[2]}", rounded=True)')
        print(priceFeeds.BinancePrice(args[2], rounded=True))
    if args[1] == "generate_bearer_RESTAPI_key":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running generate_bearer_RESTAPI_key(length="{args[2]}")')
        generate_bearer_RESTAPI_key(length=args[2])
    if args[1] == "generate_bearer_RESTAPI_key_add_to_private_accepted":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key(length="{args[2]}"))')
        add_RESTAPI_key_to_private_accepted_keys_JSON(generate_bearer_RESTAPI_key(length=args[2]))
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running responderInterface.GeneralizedENC_ResponderClaimSubroutine("{args[2]}")')
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(args[2])
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine("{args[2]}")')
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(args[2])
    if args[1] == "Responder_CheckLockTimeRefund":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running responderInterface.Responder_CheckLockTimeRefund("{args[2]}")')
        responderInterface.Responder_CheckLockTimeRefund(args[2])
    if args[1] == "SigmaParticle_box_to_addr":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr("{args[2]}"))')
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2]))
    if args[1] == "generateNewElGamalPubKey": #specific q
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running ElGamalInterface.generateNewElGamalPubKey(q="{args[2]}")')
        ElGamalInterface.generateNewElGamalPubKey(q=args[2])
    if args[1] == "watchSwapLoop":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running swap_tools.watchSwapLoop("{args[2]}")')
        swap_tools.watchSwapLoop(args[2])
elif len(args) == 4:
    if args[1] == "SigmaParticle_box_to_addr":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr("{args[2]}", "{args[3]}"))')
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2], args[3]))
    if args[1] == "Responder_CheckLockTimeRefund":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running responderInterface.Responder_CheckLockTimeRefund("{args[2]}", password="{args[3]}")')
        responderInterface.Responder_CheckLockTimeRefund(args[2], password=args[3])
    if args[1] == "updateMainEnv":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running updateMainEnv("{args[2]}", "{args[3]}")')
        updateMainEnv(args[2], args[3])
    if args[1] == "init":
        accountName = args[2]
        chain = args[3]
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running config_tools.initializeAccount("{accountName}", "{chain}")')
        config_tools.initializeAccount(accountName, chain)
    if args[1] == "generateNewElGamalPubKey": #specific q and g
        q = args[2]
        g = args[3]
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running ElGamalInterface.generateNewElGamalPubKey(q="{q}", g="{g}")')
        ElGamalInterface.generateNewElGamalPubKey(q=q, g=g)
    if args[1] == "proveEncEnvFilePasswordKnowledge":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running proveEncEnvFilePasswordKnowledge("{args[2]}", "{args[3]}")')
        proveEncEnvFilePasswordKnowledge(args[2], args[3])
    if args[1] == "GeneralizeENC_ResponseSubroutine_hotreload":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                responderInterface.GeneralizeENC_ResponseSubroutine("{args[2]}",\
                "", "", "", "", "", "", "", hotReloadSwapState="{args[3]}")')
        responderInterface.GeneralizeENC_ResponseSubroutine(args[2], "", "", "", "", "", "", "", hotReloadSwapState=args[3])
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine_hotreload":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running responderInterface.GeneralizedENC_ResponderClaimSubroutine("{args[2]}", hotReloadSwapState="{args[3]}")')
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(args[2], hotReloadSwapState=args[3])
    if args[1] == "watchSwapLoop_localEncOnly":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running swap_tools.watchSwapLoop("{args[2]}", localChainAccountPassword="{args[3]}")')
        swap_tools.watchSwapLoop(args[2], localChainAccountPassword=args[3])
    if args[1] == "watchSwapLoop_crossEncOnly":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running swap_tools.watchSwapLoop("{args[2]}", crossChainAccountPassword="{args[3]}")')
        swap_tools.watchSwapLoop(args[2], crossChainAccountPassword=args[3])
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine_localENCOnly":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine("{args[2]}", localchainpassword="{args[3]}")')
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(
                args[2], localchainpassword=args[3]
        )
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine_crossENCOnly":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine("{args[2]}", crosschainpassword="{args[3]}")')
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(
                args[2], crosschainpassword=args[3]
        )
elif len(args) == 5:
    if args[1] == "SigmaParticle_box_to_addr":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr("{args[2]}", "{args[3]}", password="{args[4]}"))')
        sys.stdout.write(SigmaParticleInterface.SigmaParticle_box_to_addr(args[2], args[3], password=args[4]))
    if args[1] == "GeneralizedENC_InitiatorClaimSubroutine":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(\
                "{args[2]}", localchainpassword="{args[3]}", crosschainpassword="{args[4]}"\
        )')
        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(args[2], localchainpassword=args[3], crosschainpassword=args[4])
    if args[1] == "GeneralizedENC_ResponderClaimSubroutine":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running\
                responderInterface.GeneralizedENC_ResponderClaimSubroutine(\
                "{args[2]}", \
                localChainAccountPassword="{args[3]}", \
                crossChainAccountPassword="{args[4]}"\
        )')
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(\
                args[2], \
                localChainAccountPassword=args[3], \
                crossChainAccountPassword=args[4]\
        )
    if args[1] == "requestEncryptedInitiation_ClientEndpoint":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running requestEncryptedInitiation_ClientEndpoint("{args[2]}", "{args[3]}", "{args[4]}")')
        requestEncryptedInitiation_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "submitEncryptedResponse_ClientEndpoint":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running submitEncryptedResponse_ClientEndpoint("{args[2]}", "{args[3]}", "{args[4]}")')
        submitEncryptedResponse_ClientEndpoint(args[2], args[3], args[4])
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initiatorInterface.GeneralizedENC_FinalizationSubroutine("{args[2]}", "{args[3]}", "{args[4]}")')
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(args[2], args[3], args[4])
    if args[1] == "ElGamal_decrypt":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running sys.stdout.write(ElGamalInterface.ElGamal_Decrypt("{args[2]}", "{args[3]}", "{args[4]}"))')
        sys.stdout.write(ElGamalInterface.ElGamal_Decrypt(args[2], args[3], args[4]))#subjectFilePath, senderPubKey, userKeyFileName
    if args[1] == "checkBoxValue":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running sys.stdout.write(SigmaParticleInterface.checkBoxValue("{args[2]}", "{args[3]}", "{args[4]}"))')
        sys.stdout.write(SigmaParticleInterface.checkBoxValue(args[2], args[3], args[4]))#boxID, boxValPATH, swapName
    if args[1] == "watchSwapLoop":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                swap_tools.watchSwapLoop("{args[2]}", localChainAccountPassword="{args[3]}", crossChainAccountPassword="{args[4]}")')
        swap_tools.watchSwapLoop(args[2], localChainAccountPassword=args[3], crossChainAccountPassword=args[4])
elif len(args) == 6:
    if args[1] == "logInToPasswordEncryptedAccount_Server":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running logInToPasswordEncryptedAccount_ServerEndpoint("{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}")')
        logInToPasswordEncryptedAccount_ServerEndpoint(args[2], args[3], args[4], args[5])
    if args[1] == "logInToPasswordEncryptedAccount_Client":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running logInToPasswordEncryptedAccount_ClientEndpoint("{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}")')
        logInToPasswordEncryptedAccount_ClientEndpoint(args[2], args[3], args[4], args[5])
    if args[1] == "test2pAtomicSwap":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running test2pAtomicSwap("{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}")')
        test2pAtomicSwap(args[2], args[3], args[4], args[5])
    if args[1] == "GeneralizeENC_ResponseSubroutine_hotreload":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                responderInterface.GeneralizeENC_ResponseSubroutine( \
                "{args[2]}", "", "", "", "", "", "", "", \
                localChainAccountPassword="{args[3]}", crossChainAccountPassword="{args[4]}", hotReloadSwapState="{args[5]}" \
        )')
        responderInterface.GeneralizeENC_ResponseSubroutine(
                args[2], "", "", "", "", "", "", "",
                localChainAccountPassword=args[3], crossChainAccountPassword=args[4], hotReloadSwapState=args[5]
        )

    if args[1] == "GeneralizedENC_ResponderClaimSubroutine_hotreload":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running responderInterface.GeneralizedENC_ResponderClaimSubroutine( \
                "{args[2]}", localChainAccountPassword="{args[3]}"], \
                        crossChainAccountPassword="{args[4]}", hotReloadSwapState="{args[5]}" \
        )')
        responderInterface.GeneralizedENC_ResponderClaimSubroutine(
                args[2], localChainAccountPassword=args[3], crossChainAccountPassword=args[4], hotReloadSwapState=args[5]
        )
    if args[1] == "GeneralizedENC_FinalizationSubroutine_crossENCOnly":#initiator refund checking starts here
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initiatorInterface.GeneralizedENC_FinalizationSubroutine( \
                "{args[2]}", "{args[3]}", "{args[4]}", crosschainpassword="{args[5]}" \
        )')
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                args[2], args[3], args[4], crosschainpassword=args[5]
        )
    if args[1] == "GeneralizedENC_FinalizationSubroutine_localENCOnly":#initiator refund checking starts here
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initiatorInterface.GeneralizedENC_FinalizationSubroutine( \
                "{args[2]}", "{args[3]}", "{args[4]}", localchainpassword="{args[5]}" \
        )')
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                args[2], args[3], args[4], localchainpassword=args[5]
        )
elif len(args) == 7:
    if args[1] == "checkBoxValue":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running\
                sys.stdout.write(SigmaParticleInterface.checkBoxValue(\
                "{args[2]}", "{args[3]}", "{args[4]}", ergopassword="{args[5]}", \
                otherchainpassword="{args[6]}"\
        ))')
        sys.stdout.write(SigmaParticleInterface.checkBoxValue(\
                args[2], args[3], args[4], ergopassword=args[5], \
                otherchainpassword=args[6]\
        ))#boxID, boxValPATH, swapName, password
    if args[1] == "GeneralizedENC_FinalizationSubroutine":#initiator refund checking starts here
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running\
                initiatorInterface.GeneralizedENC_FinalizationSubroutine( \
                "{args[2]}", "{args[3]}", "{args[4]}", localchainpassword="{args[5]}", crosschainpassword="{args[6]}" \
        )')
        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                args[2], args[3], args[4], localchainpassword=args[5], crosschainpassword=args[6]
        )
    if args[1] == "UpdateMarketOrderTypeUUIDsList":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
            market_pricing.UpdateMarketOrderTypeUUIDsList( \
                coins={ast.literal_eval(args[2])}, \
                marketConfigJSON="{args[3]}", \
                marketFeePercentage="{args[4]}", \
                coinAVolumeMinMax={ast.literal_eval(args[5])}, \
                rounded={ast.literal_eval(args[6])} \
        )')
        market_pricing.UpdateMarketOrderTypeUUIDsList(
            coins=ast.literal_eval(args[2]),
            marketConfigJSON=args[3],
            marketFeePercentage=args[4],
            coinAVolumeMinMax=ast.literal_eval(args[5]),
            rounded=ast.literal_eval(args[6])
        )
elif len(args) == 9:
    if args[1] == "GeneralizedENCInitiationSubroutine":    
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                initiatorInterface.GeneralizedENC_InitiationSubroutine( \
                "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", "{args[6]}", "{args[7]}", "{args[8]}" \
        )')
        initiatorInterface.GeneralizedENC_InitiationSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8])
    if args[1] == "initErgoAccountNonInteractive":
        LOG('running \
                initErgoAccountNonInteractive( \
                "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", "{args[6]}", "{args[7]}",  "{args[8]}" \
        )')
        initErgoAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7],  args[8])
elif len(args) == 10:
    if args[1] == "initSepoliaAccountNonInteractive":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                initSepoliaAccountNonInteractive( \
                "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", \
                "{args[6]}", "{args[7]}", "{args[8]}", "{args[9]}" \
        )')
        initSepoliaAccountNonInteractive(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "publishNewOrderType_ServerEndpoint":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                publishNewOrderType_ServerEndpoint( \
                "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", \
                "{args[6]}", "{args[7]}", "{args[8]}", "{args[9]}" \
        )')
        publishNewOrderType_ServerEndpoint(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "GeneralizeENC_ResponseSubroutine":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                responderInterface.GeneralizeENC_ResponseSubroutine( \
                    "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", \
                    "{args[6]}", "{args[7]}", "{args[8]}", "{args[9]}" \
        )')
        responderInterface.GeneralizeENC_ResponseSubroutine(args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    if args[1] == "GeneralizedENCInitiationSubroutine_crossENCOnly":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", \
                "{args[6]}", "{args[7]}", "{args[8]}", crossChainAccountPassword="{args[9]}" \
        )')
        initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                args[2], args[3], args[4], args[5], \
                args[6], args[7], args[8], crossChainAccountPassword=args[9])
    if args[1] == "GeneralizedENCInitiationSubroutine_localENCOnly":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", \
                "{args[6]}", "{args[7]}", "{args[8]}", localChainAccountPassword="{args[9]}" \
        )')
        initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                args[2], args[3], args[4], args[5], \
                args[6], args[7], args[8], localChainAccountPassword=args[9])
elif len(args) == 11:
    if args[1] == "initErgoAccountNonInteractive_ENC":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initErgoAccountNonInteractive("{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", "{args[6]}", "{args[7]}", "{args[8]}", "{args[9]}", password="{args[10]}", enc=True  )')
        initErgoAccountNonInteractive(
            args[2], args[3], args[4], args[5], args[6], args[7], \
            args[8], args[9], password=args[10], enc=True \
        )
    if args[1] == "GeneralizedENCInitiationSubroutine":
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running \
                initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                "{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", \
                "{args[6]}", "{args[7]}", "{args[8]}", localChainAccountPassword="{args[9]}", crossChainAccountPassword="{args[10]}"\
        )')
        initiatorInterface.GeneralizedENC_InitiationSubroutine(\
                args[2], args[3], args[4], args[5], \
                args[6], args[7], args[8], localChainAccountPassword=args[9], crossChainAccountPassword=args[10])
    if args[1] == "initSepoliaAccountNonInteractive_ENC": #TODO get rid of ID scan and compiler version args
        if config_tools.valFromConf(".env", "LOGMAINARGS").strip("\"") == "True": LOG(f'running initSepoliaAccountNonInteractive("{args[2]}", "{args[3]}", "{args[4]}", "{args[5]}", "{args[6]}", "{args[7]}", "{args[8]}", "{args[9]}", enc=True, password="{args[10]}")')
        initSepoliaAccountNonInteractive(
            args[2], args[3], args[4], args[5], args[6], args[7],
            args[8], args[9], enc=True, password=args[10]
        )

LOG('Atomic API Logger Finished')
