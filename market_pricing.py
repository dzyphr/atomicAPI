import priceFeeds, price_tools, json_tools, uuid, file_tools, os, json, ast, time, numbers
from decimal import *

### should be able to set options such as
# available coins ie: ERG, ETH, BTC
# exchanges per coin (create functions for getting price for each from specific exchanges they are listed on)
# market fee

def is_num(val):
    return isinstance(val, numbers.Number)

def UpdateMarketOrderTypeUUIDsList(coins=[], marketConfigJSON="", marketFeePercentage=0, coinAVolumeMinMax=[], rounded=False):
    if len(coins) != 2:
        print("supply 2 coins at a time per order type update")
        return False

    #TODO catch and reject major price outliers to prevent unrealistic price average output 
    #
        
    integratedCoins = ["TestnetErgo", "Sepolia"]
    ErgoFeeds = ["CoinGecko", "CoinEx", "BitPanda", "Kucoin"]
    EthereumFeeds = ["CoinGecko", "CoinEx", "BitPanda", "Kucoin", "Coinbase", "Kraken", "Binance"]
    CoinExPriceTypes = ["LowHighAvg", "Low", "High", "Last", "default", "Default"]
    KrakenPriceTypes = ["ask", "bid", "last", "vwap", "low", "high", "lowhighavg", "Default", "default"]
    CoinbasePriceTypes = ["spot", "buy", "sell", "default", "Default"]
    if coins == []:
        print("Provide coin argument! options: ", integratedCoins)
        return False
    for coin in coins:
        if coin not in integratedCoins:
            print("Coin:", coin, "not integrated! options: ", integratedCoins)
            return False
    if marketConfigJSON == "":
        #look for a version locally as the other option
        if os.path.isfile("marketConfig.json") == False:
            print("No marketConfig.json file found and no coinPriceFeedsConfigJSON Argument provided!\n \
                    make sure to provide at least one of these before calling this function!")
            return False
        else:
            #TODO for weighting a priceFeed you can just source the price again and add it to the averaging group
            #for example you can weight kraken higher by sourcing all of its price options as seperately in your
            #pricing configuration, you can also source the same pricing option from the same feed several times
            #it will bias the outcome of the average leading to a weighted result
            #format for marketConfig.json
            #{"Coins":{"TestnetErgo":{"Feeds":{"CoinGecko": "Default", "CoinEx": "LowHighAvg"}}}}
            priceFeedsConfigJSON = json_tools.ojf("marketConfig.json")
    else:
        priceFeedsConfigJSON = json.loads(marketConfigJSON)
    prices = []
    for coin in coins:
        if "Coins" in priceFeedsConfigJSON: #we can remove this check by havig a function that checks json struct ran before
            if coin in priceFeedsConfigJSON["Coins"]:
                if coin == "TestnetErgo":
                    feeds = priceFeedsConfigJSON["Coins"][coin]["Feeds"]
                    price = 0
                    feedslen = len(feeds)
                    for feed in feeds:
                        if feed in ErgoFeeds:
                            if feed == "CoinGecko":
                                CGPrice = priceFeeds.CoinGeckoSimplePrice("ergo", rounded=rounded)
                                if is_num(CGPrice):
                                    price += CGPrice
                                else:
                                    feedslen -= 1 #if we get a bad result we must remove the relative feed 
                            if feed == "BitPanda":
                                BPPrice = priceFeeds.BitPandaPrice("ERG", rounded=rounded)
                                if is_num(BPPrice):
                                    price += BPPrice
                                else:
                                    feedslen -= 1
                            if feed == "Kucoin":
                                KCPrice = priceFeeds.KucoinPrice("ERG", rounded=rounded)
                                if is_num(KCPrice):
                                    price += KCPrice
                                else:
                                    feedslen -= 1
                            if feed == "CoinEx":
                                pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                if pricetype in CoinExPriceTypes:
                                    CEPrice = 0
                                    if pricetype in ["default", "Default"]:
                                        pricetype = "Last"
                                    if pricetype == "LowHighAvg":
                                        CEPrice += priceFeeds.CoinExPriceLowHighAvg("ERG", rounded=rounded)
                                    if pricetype == "Low":
                                        CEPrice += priceFeeds.CoinExPriceLow("ERG", rounded=rounded)
                                    if pricetype == "High":
                                        CEPrice += priceFeeds.CoinExPriceHigh("ERG", rounded=rounded)
                                    if pricetype == "Last":
                                        CEPrice += priceFeeds.CoinExPriceLast("ERG", rounded=rounded)
                                    if is_num(CEPrice):
                                        price += CEPrice
                                    else:
                                        feedslen -= 1
                        else:
                            feedslen -= 1 #important to remove a feed that wont be called from the averaging group
                    price = price / feedslen #average the price feeds
                    if rounded == True:
                        price = price.quantize(Decimal('0.01'), ROUND_DOWN)
                    prices.append(price)
                if coin == "Sepolia":
                    feeds = priceFeedsConfigJSON["Coins"][coin]["Feeds"]
                    price = 0
                    feedslen  = len(feeds)
                    for feed in feeds:
                        if feed in EthereumFeeds:
                            if feed == "CoinGecko":
                                CGPrice = priceFeeds.CoinGeckoSimplePrice("ethereum", rounded=rounded)
                                if is_num(CGPrice):
                                    price += CGPrice
                                else:
                                    feedslen -= 1
                            if feed == "BitPanda":
                                BPPrice = priceFeeds.BitPandaPrice("ETH", rounded=rounded)
                                if is_num(BPPrice):
                                    price += BPPrice
                                else:
                                    feedslen -= 1
                            if feed == "Kucoin":
                                KCPrice = priceFeeds.KucoinPrice("ETH", rounded=rounded)
                                if is_num(KCPrice):
                                    price += KCPrice
                                else:
                                    feedslen -= 1
                            if feed == "CoinEx":
                                pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                if pricetype in CoinExPriceTypes:
                                    CEPrice = 0
                                    if pricetype in ["default", "Default"]:
                                        pricetype = "Last"
                                    if pricetype == "LowHighAvg":
                                        CEPrice += priceFeeds.CoinExPriceLowHighAvg("ETH", rounded=rounded)
                                    if pricetype == "Low":
                                        CEPrice += priceFeeds.CoinExPriceLow("ETH", rounded=rounded)
                                    if pricetype == "High":
                                        CEPrice += priceFeeds.CoinExPriceHigh("ETH", rounded=rounded)
                                    if pricetype == "Last":
                                        CEPrice += priceFeeds.CoinExPriceLast("ETH", rounded=rounded)
                                    if is_num(CEPrice):
                                        price += CEPrice
                                    else:
                                        feedslen -= 1
                            if feed == "Kraken":
                                pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                if pricetype in KrakenPriceTypes:
                                    if pricetype in ["Default", "default"]:
                                        pricetype = ""
                                    KPrice = priceFeeds.KrakenPrice("ETH", kind=pricetype, rounded=rounded)
                                    if is_num(KPrice):
                                        price += KPrice
                                    else:
                                        feedslen -= 1
                            if feed == "Coinbase":
                                pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                if pricetype in CoinbasePriceTypes:
                                    if pricetype in ["Default", "default"]:
                                        pricetype = "spot"
                                    CBPrice = priceFeeds.CoinbasePrice("ETH", kind=pricetype, rounded=rounded)
                                    if is_num(CBPrice):
                                        price += CBPrice
                                    else:
                                        feedslen -= 1
                            if feed == "Binance":
                                BPrice = priceFeeds.BinancePrice("ETH", rounded=rounded)
                                if is_num(BPrice):
                                    price += BPrice
                                else:
                                    feedslen -= 1
                        else:
                            feedslen -= 1 #important to remove a feed that wont be called from the averaging group
                    price = price / feedslen #average the price feeds
                    if rounded == True:
                        price = price.quantize(Decimal('0.01'), ROUND_DOWN)
                    prices.append(price)

    OrderTypesJSON = {}
    if os.path.isfile("OrderTypes.json") == True:
        OrderTypesJSON = json_tools.ojf("OrderTypes.json")
    found = False
    for UUID in OrderTypesJSON:
        if OrderTypesJSON[UUID]["CoinA"] == coins[0] and OrderTypesJSON[UUID]["CoinB"] == coins[1] and \
                OrderTypesJSON[UUID]["MinVolCoinA"] == str(coinAVolumeMinMax[0]) \
                and OrderTypesJSON[UUID]["MaxVolCoinA"] == str(coinAVolumeMinMax[1]):
            found = True
            OrderTypesJSON[UUID]["CoinA_price"] = str(prices[0])
            OrderTypesJSON[UUID]["CoinB_price"] = str(prices[1])
            OrderTypesJSON[UUID]["MarketFeePercentage"] = str(marketFeePercentage)
    if found == False:
        #create a new order type
        name = str(uuid.uuid4())
        newobj = {
                "CoinA": coins[0],
                "CoinB": coins[1],
                "MinVolCoinA": str(coinAVolumeMinMax[0]),
                "MaxVolCoinA": str(coinAVolumeMinMax[1]),
                "CoinA_price": str(prices[0]),
                "CoinB_price": str(prices[1]),
                "MarketFeePercentage": str(marketFeePercentage)
        }
        OrderTypesJSON.setdefault(name, newobj)
    file_tools.clean_file_open("OrderTypes.json", "w", json.dumps(OrderTypesJSON, indent=4))
                                

def marketPricingLoop(frequency=15):
    marketConf = json_tools.ojf("marketConfig.json")
    if "OrderTypes" in marketConf:
        while True:
            for orderType in marketConf["OrderTypes"]:
                UpdateMarketOrderTypeUUIDsList(
                        coins=[marketConf["OrderTypes"][orderType]["CoinA"], marketConf["OrderTypes"][orderType]["CoinB"]],
                        marketConfigJSON="", 
                        marketFeePercentage=marketConf["OrderTypes"][orderType]["MarketFeePercentage"], 
                        coinAVolumeMinMax=[
                            marketConf["OrderTypes"][orderType]["MinVolCoinA"], marketConf["OrderTypes"][orderType]["MaxVolCoinA"]
                        ], 
                        rounded=ast.literal_eval(marketConf["OrderTypes"][orderType]["Rounded"])
                )
            time.sleep(frequency)
    else:
        print("No OrderTypes Found! Create OrderTypes in your marketConfig.json before running marketPricingLoop")

            








