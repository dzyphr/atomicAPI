import requests, os, json, time, http
import urllib.request
from decimal import *
from dotenv import load_dotenv
load_dotenv()

def CoinGeckoTickerByID(coinname):
    url = f'https://api.coingecko.com/api/v3/coins/{coinname}/tickers'
    if os.getenv("CoinGeckoMarketAPIKey") == None:
        print("CoinGeckoMarketAPIKey not found! ")
        return "CoinGeckoMarketAPIKey not found! "
    else:
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": os.getenv("CoinGeckoMarketAPIKey")
        }
        return requests.get(url, headers=headers).text


def CoinGeckoAvgPrice(coinname): #optimistic average
    data = CoinGeckoTickerByID(coinname)
    jdata = json.loads(data)
    if data == "{\"error\":\"coin not found\"}":
        return "error: coin not found (use full name not ticker)"
    tickers = jdata["tickers"]
    pricesum = 0
    for market in tickers:
#        print("Market Name: ", market["market"]["name"], " Price: ", market["converted_last"]["usd"])
        pricesum += Decimal(market["converted_last"]["usd"])
    #NOTE this is not weighted by market volume so it is a rather optimistic average
    priceavg = Decimal(pricesum / len(tickers)).quantize(Decimal('0.01'), ROUND_DOWN)
    return priceavg

def CoinGeckoSimplePrice(coinname, rounded=False):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={coinname}&vs_currencies=USD'
    request =  requests.get(url)
    rt = request.text
    if rt == "{}":
        return f'{coinname} not found, make sure to use full name not ticker'
    try:
        rj = request.json()
        while True:
            if coinname in rj:
                if rounded == False:
                    return Decimal(rj[coinname]["usd"])
                else:
                    return Decimal(rj[coinname]["usd"]).quantize(Decimal('0.01'), ROUND_DOWN)
            else:
                print(rj)
                time.sleep(1)
                continue
    except:
        print("CoinGecko response was not json! Response: ", rt)


def BitPandaTicker(ticker):
    url = "https://api.bitpanda.com/v1/ticker"
    requestJSON = requests.get(url).json()
    if ticker.upper() in requestJSON:
        return requestJSON[ticker.upper()]
    else:
        return f'{ticker} not found! Make sure to use ticker not full name.'

def BitPandaPrice(ticker, rounded=False):
    tickers = BitPandaTicker(ticker)
    if type(tickers) == dict:
        if rounded == False:
            return Decimal(BitPandaTicker(ticker)["USD"])
        else:
            return Decimal(BitPandaTicker(ticker)["USD"]).quantize(Decimal('0.01'), ROUND_DOWN)
    else:
        return tickers

def KucoinPrice(ticker, rounded=False):
    url = "https://api.kucoin.com/api/v1/prices"
    get = requests.get(url)
    try:
        requestJSON = get.json()
        if requestJSON["code"] == "200000":
            if ticker.upper() in requestJSON["data"]:
                if rounded == False:
                    return Decimal(requestJSON["data"][ticker.upper()])
                else:
                    return Decimal(requestJSON["data"][ticker.upper()]).quantize(Decimal('0.01'), ROUND_DOWN)
            else:
                return f'{ticker} not found! Make sure to use ticker not full name.'
    except:
        print("KucoinPrice response was not json! Response: ", get)

def CoinExPriceLast(ticker, rounded=False):
    url = f'https://api.coinex.com/v2/spot/ticker?market={ticker}USDT'
    get = requests.get(url)
    try:
        requestJSON = get.json()
        if requestJSON["code"] == 0:
            last = requestJSON["data"][0]["last"]
            if rounded == False:
                return Decimal(last)
            else:
                return Decimal(last).quantize(Decimal('0.01'), ROUND_DOWN)
    except:
        print("CoinEx response was not json! Response: ", get)

def CoinExPriceLowHighAvg(ticker, rounded=False):
    url = f'https://api.coinex.com/v2/spot/ticker?market={ticker}USDT'
    get = requests.get(url)
    try:
        requestJSON = get.json()
        if requestJSON["code"] == 0:
            low = Decimal(requestJSON["data"][0]["low"])
            high = Decimal(requestJSON["data"][0]["high"])
            avg = Decimal( (high + low) / 2 )
            if rounded == False:
               return avg
            else:
                return avg.quantize(Decimal('0.01'), ROUND_DOWN)
    except:
        print("CoinEx response was not json! Response: ", get)

def CoinExPriceLow(ticker, rounded=False):
    url = f'https://api.coinex.com/v2/spot/ticker?market={ticker}USDT'
    get = requests.get(url)
    try:
        requestJSON = get.json()
        if requestJSON["code"] == 0:
            low = Decimal(requestJSON["data"][0]["low"])
            if rounded == False:
               return low
            else:
                return low.quantize(Decimal('0.01'), ROUND_DOWN)
    except:
        print("CoinEx response was not json! Response: ", get)

def CoinExPriceHigh(ticker, rounded=False):
    url = f'https://api.coinex.com/v2/spot/ticker?market={ticker}USDT'
    get = requests.get(url)
    try:
        requestJSON = get.json()
        if requestJSON["code"] == 0:
            high = Decimal(requestJSON["data"][0]["high"])
            if rounded == False:
               return high
            else:
                return high.quantize(Decimal('0.01'), ROUND_DOWN)
    except:
        print("CoinEx response was not json! Response: ", get)


def KrakenPrice(ticker, kind="", rounded=False):
    url = f'https://api.kraken.com/0/public/Ticker?pair={ticker}USD'
    r = requests.get(url)
    requesttext = r.text
    try:
        requestJSON = r.json()
        if requesttext == "{\"error\":[\"EQuery:Unknown asset pair\"]}":
            return f'error: Unknown asset: {ticker}. Make sure to use Ticker not full name'
        pricekinds = ["ask", "bid", "last", "vwap", "low", "high", "lowhighavg"]
        if kind != "":
            if kind not in pricekinds:
                print("unknown price kind: ", kind, " options: ", pricekinds)
            if kind == "ask":
                price = requestJSON["result"][next(iter(requestJSON["result"]))]["a"][0]
                if rounded == False:
                    return Decimal(price)
                else:
                    return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
            if kind == "bid":
                price = requestJSON["result"][next(iter(requestJSON["result"]))]["b"][0]
                if rounded == False:
                    return Decimal(price)
                else:
                    return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
            if kind == "last":
                price = requestJSON["result"][next(iter(requestJSON["result"]))]["c"][0]
                if rounded == False:
                    return Decimal(price)
                else:
                    return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
            if kind == "vwap":
                price = requestJSON["result"][next(iter(requestJSON["result"]))]["p"][0]
                if rounded == False:
                    return Decimal(price)
                else:
                    return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
            if kind == "low":
                price = requestJSON["result"][next(iter(requestJSON["result"]))]["l"][0]
                if rounded == False:
                    return Decimal(price)
                else:
                    return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
            if kind == "high":
                price = requestJSON["result"][next(iter(requestJSON["result"]))]["h"][0]
                if rounded == False:
                    return Decimal(price)
                else:
                    return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
            if kind == "lowhighavg":
                low = Decimal(requestJSON["result"][next(iter(requestJSON["result"]))]["l"][0])
                high = Decimal(requestJSON["result"][next(iter(requestJSON["result"]))]["h"][0])
                avg = Decimal( (high + low) / 2 )
                if rounded == False:
                    return avg
                else:
                    return avg.quantize(Decimal('0.01'), ROUND_DOWN)
        else:
            price = requestJSON["result"][next(iter(requestJSON["result"]))]["p"][0] #vwap as default option
            if rounded == False:
                return Decimal(price)
            else:
                return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
    except:
        print("Kraken response was not json! Response: ", requesttext)

def CoinbasePrice(ticker, kind="", rounded=False):
    pricekinds = ["spot", "buy", "sell"]
    if kind not in pricekinds:
        print("kind: ", kind, "not found! Choices: ", pricekinds)
    url = f'https://api.coinbase.com/v2/prices/{ticker}-USD/{kind}'
    r = requests.get(url)
    rText = r.text
    try:
        rJSON = r.json()
        if rText == "{\"error\":\"not found\",\"code\":5,\"message\":\"not found\"}":
            return "Ticker: " + ticker + " not found! Use ticker not full coin name."
        price = Decimal(rJSON["data"]["amount"])
        if rounded == False:
            return price
        else:
            return price.quantize(Decimal('0.01'), ROUND_DOWN)
    except:
            print("Coinbase response was not json! Response: ", rText)

def BinancePrice(ticker, rounded=False):
    url = 'https://www.binance.com/api/v3/ticker/price'
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            try:
                data = response.read().decode()
                prices = json.loads(data)
                found = False
                for tickerdata in prices:
                    symbol = tickerdata["symbol"]
                    if tickerdata["symbol"] == f'{ticker.upper()}USDT':
                        price = tickerdata["price"]
                        found = True
                        if rounded == False:
                            return Decimal(price)
                        else:
                            return Decimal(price).quantize(Decimal('0.01'), ROUND_DOWN)
                if found == False:
                    return "ticker: " + ticker + " not found! Use ticker not full coin name."
            except http.client.IncompleteRead:
                print("http incomplete read error")
            except: 
                print("Binance response was not json! Response: ", data)
        else:
            print(f"Failed to retrieve data. Status code: {response.status}")






