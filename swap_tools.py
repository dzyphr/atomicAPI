import file_tools, os, uuid, responderInterface, json_tools, subprocess, sys, json

PossibleSwapStates = ["initiated", "uploadingResponseContract", "uploadedResponseContract", "fundingResponseContract", "fundedResponseContract", "responding", "responded_unsubmitted", "responded_submitted", "finalized", "verifyingFinalizedContractValues", "verifiedFinalizedContractValues", "claiming", "refunding", "claimed", "refunded", "terminated", "tbd"]

def setSwapState(swapName, state):
    if state not in PossibleSwapStates:
        print("Please provide valid state argument choice.\nChoices: initiated, uploadingResponseContract, fundingResponseContract, responded, finalized, verifyingFinalizedContractValues, claiming, refunding, claimed, refunded, terminated, tbd")
        return False
    if os.path.isdir(swapName) == False:
        print("Swap directory named: ", swapName, "not found!\nMake sure swap dir is created before setting it's state.")
        return False
    else:
        file_tools.clean_file_open(swapName + "/SwapState", "w", state)
        return True

def getSwapState(swapName):
    if os.path.isdir(swapName) == False:
        print("Swap directory named: ", swapName, "not found!\nMake sure swap dir is created before getting it's state.")
        return False
    if os.path.isfile(swapName + "/SwapState") == False:
        print("SwapState file not found!\nMake sure swap state has been set before getting it's state.")
        return False
    else:
        return file_tools.clean_file_open(swapName + "/SwapState", "r")

#probably defunct
def scanAllSwapStates():
    def is_uuidv3(s):
        try:
            uuid.UUID(s, version=3)
            return True
        except ValueError:
            return False

    swapDirs = [d for d in os.listdir() if os.path.isdir(d) and is_uuidv3(d)]
    print(swapDirs)
    for swapDir in swapDirs:
        SwapState = getSwapState(swapDir)
        if SwapState in PossibleSwapStates:
            if SwapState == PossibleSwapStates[0]:
                responderInterface.GeneralizeENC_ResponseSubroutine(hotReloadSwapState=PossibleSwapStates[0])
                #since this needs to be called w a password sometimes maybe entire routine should be carried out
                #by rest APIs... TODO TODO

        else:
            print("Error: Unexpected SwapState: ", SwapState)

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


def watchSwapLoop(swapName, localChainAccountPassword="", crossChainAccountPassword=""):
    #watches a specific swap, called after scanning swapstatemap or initiation
    #handles swap communication round responses, can be used for hot reload after shutdown
    #to make sure all swaps left in any limbo state are completely cleaned up
    #for now automatically claim swaps based on low level checks only
    #later add ability for UI to update swapStateMap with data about autoclaim minimum value

    #start by checking the swap's state in the swapstate map, if it exists grab its data
    SwapStateMap = json_tools.ojf("SwapStateMap")
    print("watchSwapLoop: swapStateMap: ", SwapStateMap)
    if swapName in SwapStateMap:
        swapState = SwapStateMap[swapName]["SwapState"]
        role = SwapStateMap[swapName]["SwapRole"]
        LocalChain = SwapStateMap[swapName]["LocalChain"]
        CrossChain = SwapStateMap[swapName]["CrossChain"]
        LocalChainAccountName = SwapStateMap[swapName]["LocalChainAccount"]
        CrossChainAccountName = SwapStateMap[swapName]["CrossChainAccount"]
        ClientElGamalKey = SwapStateMap[swapName]["ElGamalKey"]
        ServerElGamalKey = SwapStateMap[swapName]["ServerElGamalKey"]
        ElGamalKeyPath = SwapStateMap[swapName]["ElGamalKeyPath"]
        MarketAPIKey = SwapStateMap[swapName]["MarketAPIKey"]
        SwapAmount = SwapStateMap[swapName]["SwapAmount"]
        MarketOrderTypesURL = SwapStateMap[swapName]["MarketURL"]
        MarketPublicRequestsURL = MarketOrderTypesURL.replace("ordertypes", "publicrequests")
        if role == "Responder":
            if LocalChain == "Sepolia" and CrossChain == "TestnetErgo":
                if swapState in PossibleSwapStates:
                    if swapState == PossibleSwapStates[0]:
                        responderInterface.GeneralizeENC_ResponseSubroutine(
                            swapName, CrossChainAccountName, LocalChainAccountName, 
                            ServerElGamalKey, ElGamalKeyPath, CrossChain, LocalChain, SwapAmount,
                            localChainAccountPassword=localChainAccountPassword, 
                            crossChainAccountPassword=crossChainAccountPassword, 
                        )                       
                        #TODO run checklocktimerefund loop since contract is funded here
                        #TODO update SwapStateMap with active swap state
                        file_tools.wait_for_file(swapName + "/ENC_response_path.bin")
                        ActiveSwapState = file_tools.clean_file_open(swapName + "/SwapState", "r")
#                        print(ActiveSwapState, PossibleSwapStates[6])
                        if ActiveSwapState == PossibleSwapStates[6]: #responded unsubmitted
                            ENC_response = file_tools.clean_file_open(swapName + "/ENC_response_path.bin", "r")
                            ENC_finalization = submitEncryptedResponse_ClientEndpoint(
                                    swapName, MarketPublicRequestsURL, ENC_response, MarketAPIKey
                            ).replace("\\n", "\n").replace("\"", "")
                            file_tools.clean_file_open(swapName + "/ENC_finalization.bin", "w", ENC_finalization)
                            DecryptCommand = [
                                    "python3", "-u", "main.py", 
                                    "ElGamal_decrypt", swapName + "/ENC_finalization.bin",
                                    ServerElGamalKey, ElGamalKeyPath
                            ]
                            DEC_finalization = subprocess.run(DecryptCommand, capture_output=True, text=True).stdout
                            print(json.loads(DEC_finalization))



    else:
        print("swap: ", swapName, "not found in SwapStateMap!")
        
    

