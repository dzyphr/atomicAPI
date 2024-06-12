import priceFeeds, price_tools, json_tools, uuid

### should be able to set options such as
# available coins ie: ERG, ETH, BTC
# exchanges per coin (create functions for getting price for each from specific exchanges they are listed on)
# market fee

def UpdateMarketOrderTypeUUIDsList(coins=[], coinPriceFeedsConfigJSON="", marketFeePercentage=0, coinAVolumeMinMax=[], rounded=False):
    if len(coins) != 2:
        print("supply 2 coins at a time per order type update")
        return False

        
        
    integratedCoins = ["TestnetErgo", "Sepolia"]
    ErgoFeeds = ["CoinGecko", "CoinEx", "BitPanda", "Kucoin"]
    EthereumFeeds = ["CoinGecko", "CoinEx", "BitPanda", "Kucoin", "Coinbase", "Kraken", "Binance"]
    CoinExPriceTypes = ["LowHighAvg", "Low", "High", "Last"]
    KrakenPriceTypes = ["ask", "bid", "last", "vwap", "low", "high", "lowhighavg", "Default", "default"]
    CoinBasePriceTypes = ["spot", "buy", "sell", "default", "Default"
    if coins == []:
        print("Provide coin argument! options: ", integratedCoins)
        return False
    for coin in coins:
        if coin not in [integratedCoins]:
            print("Coin:", coin, "not integrated! options: ", integratedCoins)
            return False
    if coinPriceFeedsConfigJSON == "":
        #look for a version locally as the other option
        if os.path.isfile("coinPriceFeedsConfig.json") == False:
            print("No coinPriceFeedsConfig.json file found and no coinPriceFeedsConfigJSON Argument provided!\n \
                    make sure to provide at least one of these before calling this function!")
            return False
        else:
            #TODO for weighting a priceFeed you can just source the price again and add it to the averaging group
            #for example you can weight kraken higher by sourcing all of its price options as seperately in your
            #pricing configuration, you can also source the same pricing option from the same feed several times
            #it will bias the outcome of the average leading to a weighted result
            #format for coinPriceFeedsConfig.json
            #{"Coins":{"TestnetErgo":{"Feeds":{"CoinGecko": "Default", "CoinEx": "LowHighAvg"}}}}
            priceFeedsConfigJSON = json_tools.ojf("coinPriceFeedsConfig.json")
    else:
        priceFeedsConfigJSON = json.loads(coinPriceFeedsConfigJSON)
    prices = []
    for coin in coins:
        if ["Coins"] in priceFeedsConfigJSON:
            if coin in priceFeedsConfigJSON["Coins"]:
                if coin in integratedCoins:
                    if coin == "TestnetErgo":
                        feeds = priceFeedsConfigJSON["Coins"][coin]["Feeds"]
                        price = 0
                        for feed in feeds:
                            if feed in ErgoFeeds:
                                if feed == "CoinGecko":
                                    CGPrice = CoinGeckoSimplePrice("Ergo", rounded=rounded)
                                    price += CGPrice
                                if feed == "BitPanda":
                                    BPPrice = BitPandaPrice("ERG", rounded=rounded)
                                    price += BPPrice
                                if feed == "Kucoin":
                                    KCPrice = KucoinPrice("ERG", rounded=rounded)
                                    price += KCPrice
                                if feed == "CoinEx":
                                    pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                    if pricetype in CoinExPriceTypes:
                                        CEPrice = 0
                                        if pricetype == "LowHighAvg":
                                            CEPrice += CoinExPriceLowHighAvg("ERG", rounded=rounded)
                                        if pricetype == "Low":
                                            CEPrice += CoinExPriceLow("ERG", rounded=rounded)
                                        if pricetype == "High":
                                            CEPrice += CoinExPriceHigh("ERG", rounded=rounded)
                                        if pricetype == "Last":
                                            CEPrice += CoinExPriceLast("ERG", rounded=rounded)
                                        price += CEPrice
                        price = price / len(feeds) #average the price feeds
                        prices.append(price)
                    if coin == "Sepolia":
                        feeds = priceFeedsConfigJSON["Coins"][coin]["Feeds"]
                        price = 0
                        for feed in feeds:
                            if feed in EthereumFeeds:
                                if feed == "CoinGecko":
                                    CGPrice = CoinGeckoSimplePrice("Ethereum", rounded=rounded)
                                    price += CGPrice
                                if feed == "BitPanda":
                                    BPPrice = BitPandaPrice("ETH", rounded=rounded)
                                    price += BPPrice
                                if feed == "Kucoin":
                                    KCPrice = KucoinPrice("ETH", rounded=rounded)
                                    price += KCPrice
                                if feed == "CoinEx":
                                    pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                    if pricetype in CoinExPriceTypes:
                                        CEPrice = 0
                                        if pricetype == "LowHighAvg":
                                            CEPrice += CoinExPriceLowHighAvg("ETH", rounded=rounded)
                                        if pricetype == "Low":
                                            CEPrice += CoinExPriceLow("ETH", rounded=rounded)
                                        if pricetype == "High":
                                            CEPrice += CoinExPriceHigh("ETH", rounded=rounded)
                                        if pricetype == "Last":
                                            CEPrice += CoinExPriceLast("ETH", rounded=rounded)
                                        price += CEPrice
                                if feed == "Kraken":
                                    pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                    if pricetype in KrakenPriceTypes:
                                        if pricetype in ["Default", "default"]:
                                            pricetype = ""
                                        KPrice = KrakenPrice("ETH", kind=pricetype, rounded=rounded)
                                        price += KPrice
                                if feed == "Coinbase":
                                    pricetype = priceFeedsConfigJSON["Coins"][coin]["Feeds"][feed]
                                    if pricetype in CoinbasePriceTypes:
                                        if pricetype in ["Default", "default"]:
                                            pricetype = "spot"
                                        CBPrice = CoinbasePrice("ETH", kind=pricetype, rounded=rounded)
                                        price += CBPrice
                                if feed == "Binance":
                                    BPrice = BinancePrice("ETH", rounded=rounded)
                                    price += BPrice
                        price = price / len(feeds) #average the price feeds
                        prices.append(price)




    OrderTypesJSON = {}
    if os.path.isfile("OrderTypes.json") == True:
        OrderTypesJSON = json_tools.ojf("OrderTypes.json")
    found = False
    for UUID in OrderTypesJSON:
        if UUID["CoinA"] == coins[0] && UUID["CoinB"] == coins[1] && \
                UUID["MinVolCoinA"] == coinAVolumeMinMax[0] && UUID["MaxVolCoinA"] == coinAVolumeMinMax[1]:
            found = True
            UUID["CoinA_price"] = prices[0]
            UUID["CoinB_price"] = prices[1]
    if found == False:
        #create a new order type
        name = uuid.uuid4()
        OrderTypesJSON[name]["CoinA"] = coins[0]
        OrderTypesJSON[name]["CoinB"] = coins[1]
        OrderTypesJSON[name]["MinVolCoinA"] == coinAVolumeMinMax[0]
        OrderTypesJSON[name]["MaxVolCoinA"] == coinAVolumeMinMax[1]
        OrderTypesJSON[name]["CoinA_price"] = prices[0]
        OrderTypesJSON[name]["CoinB_price"] = prices[1]
    file_tools.clean_file_open("OrderTypes.json", "w", json.dumps(OrderTypesJSON, indent=4))
                                


            








