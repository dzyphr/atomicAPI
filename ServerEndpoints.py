def logInToPasswordEncryptedAccount_ServerEndpoint(Chain, AccountName, Password, auth):
    import requests, uuid
    url = "http://localhost:3030/v0.0.1/requests/" #server private requests url
    ID = str(uuid.uuid4())
    headers = {"Authorization": "Bearer " + auth}
    requestobj = {
            "id": ID,
            "request_type": "logInToPasswordEncryptedAccount",
            "Chain": Chain,
            "AccountName": AccountName,
            "Password": Password
    }
    print(requests.post(url, headers=headers,  json = requestobj).text)

def publishNewOrderType_ServerEndpoint(url, CoinA, CoinB, CoinA_price, CoinB_price, MaxVolCoinA, MinVolCoinA, auth):
    import requests, uuid
    ID = str(uuid.uuid4())
    headers = {"Authorization": "Bearer " + auth}
    requestobj = {
        "id": ID,
        "request_type": "publishNewOrderType",
        "OrderTypeUUID": ID,
        "CoinA": CoinA,
        "CoinB": CoinB,
        "CoinA_price": CoinA_price,
        "CoinB_price": CoinB_price,
        "MaxVolCoinA": MaxVolCoinA,
        "MinVolCoinA": MinVolCoinA
    }
    print(requests.post(url, headers=headers,  json = requestobj).text)

