from decimal import Decimal
def getPriceConversions(amountMod, CoinA_Price, CoinB_Price):
    ConversionFromCoinA = Decimal(\
            Decimal(\
                amountMod\
            ) * Decimal(\
            CoinA_Price.replace("\"", "")\
            ) / Decimal(\
            CoinB_Price.replace("\"", "")\
            )\
    )
    ConversionFromCoinB = Decimal(\
            Decimal(\
                amountMod\
            ) * Decimal(\
            CoinB_Price.replace("\"", "")\
            ) / Decimal(\
            CoinA_Price.replace("\"", "")\
            )\
    )
    print("{:,f}".format(ConversionFromCoinA), "{:,f}".format(ConversionFromCoinB))
    return [ConversionFromCoinA, ConversionFromCoinB]

def EthToWei(Eth):
    oneEthInWei = 1000000000000000000
    return int(Decimal(Eth) * oneEthInWei)

def weiToEth(wei):
    oneEthInWei = 1000000000000000000
    return Decimal(Decimal(wei) / oneEthInWei)

def ErgToNanoErg(Erg):
    oneErgInNanoErg = 1000000000
    return int(Decimal(Erg) * oneErgInNanoErg)

def NanoErgToErg(NanoErg):
    oneErgInNanoErg = 1000000000
    return Decimal(NanoErg / oneErgIneNanoErg)

