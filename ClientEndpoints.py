def logInToPasswordEncryptedAccount_ClientEndpoint(Chain, AccountName, Password, auth):
    import requests, uuid
    url = "http://localhost:3031/v0.0.1/requests/" #server private requests url
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


def submitEncryptedResponse_ClientEndpoint(url, SwapTicketID, ENC_response_path):
    import requests, uuid
    ID = str(uuid.uuid4())
    headers = {"Authorization": "None"}
    resp = file_tools.clean_file_open(ENC_response_path, "r")
    requestobj = {
        "id": ID,
        "request_type":"submitEncryptedResponse",
        "SwapTicketID":SwapTicketID,
        "encryptedResponseBIN":  resp
    }
    respStr = requests.post(url, headers=headers, json = requestobj).text.replace("\"", "").replace("\\", "\n").replace("n", "")
    file_tools.clean_file_open(SwapTicketID + "/ENC_finalization.bin", "w", respStr)
    responderJSONPath = SwapTicketID + "/responder.json"
    responderInterface.GeneralizedENC_ResponderClaimSubroutine(responderJSONPath)

def requestEncryptedInitiation_ClientEndpoint(url, OrderTypeUUID, ElGamalPubkey):
    import requests, uuid
    ID = str(uuid.uuid4())
    headers = {"Authorization": "None"}
    requestobj = {
        "id": ID,
        "request_type":"requestEncryptedInitiation",
        "OrderTypeUUID":OrderTypeUUID,
        "ElGamalKey":ElGamalPubkey,
    }
    respStr = requests.post(url, headers=headers, json = requestobj).text
    respObj = json.loads(respStr[1:-1].encode().decode('unicode_escape'))
    swapname = respObj["SwapTicketID"]
    file_tools.clean_mkdir(swapname) #swapname
    file_tools.clean_file_open(respObj["SwapTicketID"] + "/ENC_init.bin", "w", respObj["ENC_init.bin"])
    
def submitEncryptedResponse_ClientEndpoint(swapID, marketPublicRequestsURL, ENC_response, auth):
    import requests, uuid
    url = marketPublicRequestsURL #server private requests url
    ID = str(uuid.uuid4())
    headers = {"Authorization": "Bearer " + auth}
    requestobj = {
            "id": ID,
            "request_type": "submitEncryptedResponse",
            "SwapTicketID": swapID,
            "encryptedResponseBIN": ENC_response
    }
    return requests.post(url, headers=headers,  json = requestobj).text

