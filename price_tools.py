import decimal
def getPriceConversions(amountMod, CoinA_Price, CoinB_Price):
    ConversionCoinA = decimal.Decimal(amountMod) * decimal.Decimal(CoinA_Price.replace("\"", "")) / decimal.Decimal(CoinB_Price.replace("\"", ""))
    ConversionCoinB = (decimal.Decimal(amountMod) * decimal.Decimal(CoinB_Price.replace("\"", ""))) / decimal.Decimal(CoinA_Price.replace("\"", ""))
    print(ConversionCoinA, ConversionCoinB)
    return [ConversionCoinA, ConversionCoinB]

def EthToWei(Eth):
    oneEthInWei = 1000000000000000000
    return int(decimal.Decimal(Eth) * oneEthInWei)

def weiToEth(wei):
    oneEthInWei = 1000000000000000000
    return decimal.Decimal(decimal.Decimal(wei) / oneEthInWei)

def ErgToNanoErg(Erg):
    oneErgInNanoErg = 1000000000
    return int(decimal.Decimal(Erg) * oneErgInNanoErg)

def NanoErgToErg(NanoErg):
    oneErgInNanoErg = 1000000000
    return decimal.Decimal(NanoErg / oneErgIneNanoErg)

