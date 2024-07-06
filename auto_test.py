#automated tests
import requests, json, uuid, json_tools
from LOG import AUTOTESTLOG
def automated_test_local_client_side():
    localMarketServerOrderTypesURL = "http://127.0.0.1:3030/v0.0.1/ordertypes"
    OrderTypes = json.loads(requests.get(localMarketServerOrderTypesURL).json())
    if len(OrderTypes) == 0:
        AUTOTESTLOG("no order types found!", "err")
        print("no order types found!")
        exit()
    def getOrder(OrderTypesJSON):
        for orderType in OrderTypesJSON:
            return orderType

    OrderTypeUUID = getOrder(OrderTypes)
    
    #TODO for now client is only ETH in future need to modularize this to make sense of amounts likely

    amount = 0.14

    localClientAccountsMapURL = "http://localhost:3031/v0.0.1/AllChainAccountsMap"
    clientAccounts = json.loads(requests.get(localClientAccountsMapURL).json())
    
    #get non encrypted accounts #TODO comprise testing for encrypted accounts (slightly more complexity)
    localChainAccount = ""
    crossChainAccount = ""
    localChain = OrderTypes[OrderTypeUUID]["CoinB"]
    crossChain = OrderTypes[OrderTypeUUID]["CoinA"] 

    for account in clientAccounts:
        if ".encrypted" not in account and localChain == "Sepolia" and localChainAccount == "" and "EVM" in account:
            localChainAccount = account.replace("EVM/Atomicity/", "").replace("/.env", "")
        if ".encrypted" not in account and crossChain == "TestnetErgo" and crossChainAccount == "" and "Ergo" in account:
            crossChainAccount = account.replace("Ergo/SigmaParticle/", "").replace("/.env", "")
        if localChainAccount != "" and crossChainAccount != "":
            break

    if localChainAccount == "":
        AUTOTESTLOG(f'{localChain} account not found!', "err")
        print(f'{localChain} account not found!')
        exit()
    elif crossChainAccount == "":
        AUTOTESTLOG(f'{crossChain} account not found!', "err")
        print(f'{crossChain} account not found!')
        exit()

    CoinA_price = OrderTypes[OrderTypeUUID]["CoinA_price"]
    CoinB_price = OrderTypes[OrderTypeUUID]["CoinB_price"]

    MarketQGChannelsURL = localMarketServerOrderTypesURL.replace("ordertypes", "publicrequests/ElGamalQGChannels")
    MarketPubKeysURL = localMarketServerOrderTypesURL.replace("ordertypes", "publicrequests/ElGamalPubs")
    MarketQGPubKeyArrayURL = localMarketServerOrderTypesURL.replace("ordertypes", "publicrequests/QGPubkeyArray")
    
    MarketQGPubKeyArray = json.loads(requests.get(MarketQGPubKeyArrayURL).json())

    privateAPIKey = json_tools.ojf("accepted_private_api_keys.json")["0"]

    #If you get badapikey you're probably running this from your server, this test is for client side
    def checkElGQGChannelCorrectness(QG):
        url = "http://localhost:3031/v0.0.1/requests"
        data = json.dumps({
            "id": str(uuid.uuid4()),
            "request_type": "checkElGQGChannelCorrectness",
            "QGChannel": QG
        })
        headers = {
            "Authorization": f"Bearer {privateAPIKey}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, data=data, headers=headers).text
        return response

    localQGPubkeyArrayURL = "http://localhost:3031/v0.0.1/QGPubkeyArray"
    localQGPubkeyArray = json.loads(requests.get(localQGPubkeyArrayURL).json())

    localElGamalPubsURL = "http://localhost:3031/v0.0.1/ElGamalPubs"
    localElGamalPubs = json.loads(requests.get(localElGamalPubsURL).json())

    compatchannel = ""
    compatkey = ""
    marketElGKey = ""
    #get a compatible ElGamal Key
    for channel in MarketQGPubKeyArray:
        if checkElGQGChannelCorrectness(channel).strip("\"") == "true":
            if channel in localQGPubkeyArray.keys():
                compatkey = localQGPubkeyArray[channel][0]
                compatchannel = channel
                marketElGKeys = MarketQGPubKeyArray[channel]
                if type(marketElGKeys) == list:
                    marketElGKey = marketElGKeys[0]
                else:
                    marketElGKey = marketElGKeys
                break
            else:
                #TODO untested
                generateElGKeySpecificQGdata = {
                        "id": uuidv4(),
                        "request_type": "generateElGKeySpecificQG",
                        "QGChannel": QG
                }
                url = "http://localhost:3031/v0.0.1/requests"
                headers = {
                    "Authorization": f"Bearer {privateAPIKey}",
                    "Content-Type": "application/json"
                }
                response = requests.post(url, data=data, headers=headers).text
                compatkey = response.split(" ")[0]
                compatchannel = channel
                marketElGKey = MarketQGPubKeyArray[channel][0]
                break
    
    ElGKeyIndex = [key for key, val in localElGamalPubs.items() if val == compatkey][0]

    ElGKeyPath = f'Key{ElGKeyIndex}.ElGamalKey'


    starterAPIKeysURL = localMarketServerOrderTypesURL.replace("ordertypes", "publicrequests/starterAPIKeys")
    starterAPIKeys = json.loads(requests.get(starterAPIKeysURL).json())
    marketAPIKey = starterAPIKeys["0"]

    startSwapFromUIData = json.dumps({
            "id": str(uuid.uuid4()),
            "request_type": "startSwapFromUI",
            "OrderTypeUUID": OrderTypeUUID,
            "QGChannel": compatchannel,
            "ElGamalKey": compatkey,
            "ServerElGamalKey": marketElGKey,
            "ElGamalKeyPath": ElGKeyPath,
            "MarketURL": localMarketServerOrderTypesURL,
            "MarketAPIKey": marketAPIKey,
            "LocalChain": localChain,
            "CrossChain": crossChain,
            "LocalChainAccount": localChainAccount,
            "CrossChainAccount": crossChainAccount,
            "SwapRole": "Responder",
            "swapAmount": str(amount)
    })
    headers = {
            "Authorization": f"Bearer {privateAPIKey}",
            "Content-Type": "application/json"
    }
    url = "http://localhost:3031/v0.0.1/requests"
    AUTOTESTLOG(f'Client Data Collected Successfully, Starting Swap', "info")
    response = requests.post( \
            url, data=startSwapFromUIData, headers=headers \
            )\
            .text.replace("\n", "").replace("\r","").replace("\t","")[1:-1].replace("\\", '')[1:-1]
    j = json.loads(response)
    SwapTicketID = json.loads(response)["SwapTicketID"]

    AUTOTESTLOG(f'Returned SwapTicketID: {SwapTicketID}', "info")
    AUTOTESTLOG('AutoTest finished!', "info")



