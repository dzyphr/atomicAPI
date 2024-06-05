import file_tools, os, uuid, responderInterface, json_tools, subprocess, sys, json, ClientEndpoints

PossibleSwapStates = ["initiated", "uploadingResponseContract", "uploadedResponseContract", "fundingResponseContract", "fundedResponseContract", "responding", "responded_unsubmitted", "responded_submitted", "finalized", "verifyingFinalizedContractValues", "verifiedFinalizedContractValues", "claiming", "refunding", "claimed", "refunded", "terminated", "tbd"]
#TODO possibleSwapStates Responder and possibleSwapStates Initiatior should be seperated
#probably also seperate based on specific swap scenarios down the line

PossibleSwapStatesInitiator = ["initiating", "initiated_unsubmitted", "initiated_submitted", "responded", "verifying_response", "verified_response", "finalizing", "finalized_unsubmitted", "finalized_submitted", "claiming", "refunding", "claimed", "refunded", "terminated", "tbd"]

def setSwapState(swapName, state, setMap=False):
    if state not in PossibleSwapStates and state not in PossibleSwapStatesInitiator:
        print("Please provide valid state argument choice.\nChoices: initiated, uploadingResponseContract, fundingResponseContract, responded, finalized, verifyingFinalizedContractValues, claiming, refunding, claimed, refunded, terminated, tbd")
        return False
    if os.path.isdir(swapName) == False:
        print("Swap directory named: ", swapName, "not found!\nMake sure swap dir is created before setting it's state.")
        return False
    else:
        if setMap == True:
            if os.path.isfile("SwapStateMap") == False:
                file_tools.clean_file_open("SwapStateMap", "w", "{}")
            SwapStateMap = json_tools.ojf("SwapStateMap")
            if swapName not in SwapStateMap.keys():
                keyValList = [{swapName: {"SwapState": state}}]
                json_tools.keyVal_list_update(keyValList, "SwapStateMap")
            else:
                SwapStateMap[swapName]["SwapState"] = state
    #            file_tools.clean_file_open("SwapStateMap", "w", SwapStateMap)
                mapfile = open('SwapStateMap', 'w') 
                json.dump(SwapStateMap, mapfile, indent=2)
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




def watchSwapLoop(swapName, localChainAccountPassword="", crossChainAccountPassword=""):
    #watches a specific swap, called after scanning swapstatemap or initiation
    #handles swap communication round responses, can be used for reload after shutdown
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
        ElGamalKeyPath = SwapStateMap[swapName]["ElGamalKeyPath"]
        if role == "Responder":
            SwapAmount = SwapStateMap[swapName]["SwapAmount"]
            ClientElGamalKey = SwapStateMap[swapName]["ElGamalKey"]
            MarketAPIKey = SwapStateMap[swapName]["MarketAPIKey"]
            ServerElGamalKey = SwapStateMap[swapName]["ServerElGamalKey"]
            MarketOrderTypesURL = SwapStateMap[swapName]["MarketURL"]
            MarketPublicRequestsURL = MarketOrderTypesURL.replace("ordertypes", "publicrequests")
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
                        file_tools.wait_for_file(swapName + "/ENC_response_path.bin")
                        ActiveSwapState = file_tools.clean_file_open(swapName + "/SwapState", "r")
                        setSwapState(swapName, ActiveSwapState, setMap=True)
#                        if ActiveSwapState == PossibleSwapStates[6]: #responded unsubmitted
                        ENC_response = file_tools.clean_file_open(swapName + "/ENC_response_path.bin", "r")
                        ENC_finalization = ClientEndpoints.submitEncryptedResponse_ClientEndpoint(
                                swapName, MarketPublicRequestsURL, ENC_response, MarketAPIKey
                        ).replace("\\n", "\n").replace("\"", "")
                        file_tools.clean_file_open(swapName + "/ENC_finalization.bin", "w", ENC_finalization)
                        setSwapState(swapName, PossibleSwapStates[7], setMap=True) #responded submitted
                        responderInterface.GeneralizedENC_ResponderClaimSubroutine(
                            swapName + "/responder.json", 
                            localChainAccountPassword=localChainAccountPassword, 
                            crossChainAccountPassword=crossChainAccountPassword
                        )
                    elif swapState in [
                            PossibleSwapStates[1], PossibleSwapStates[2], PossibleSwapStates[3], PossibleSwapStates[4],
                            PossibleSwapStates[5]
                    ]:
                        responderInterface.GeneralizeENC_ResponseSubroutine(
                            swapName, "", "", "", "", "", "", "",
                            localChainAccountPassword=localChainAccountPassword,
                            crossChainAccountPassword=crossChainAccountPassword,
                            reloadSwapState=swapState
                        )
                        file_tools.wait_for_file(swapName + "/ENC_response_path.bin")
                        ActiveSwapState = file_tools.clean_file_open(swapName + "/SwapState", "r")
                        setSwapState(swapName, ActiveSwapState, setMap=True)
#                       if ActiveSwapState == PossibleSwapStates[6]: #responded unsubmitted
                        ENC_response = file_tools.clean_file_open(swapName + "/ENC_response_path.bin", "r")
                        ENC_finalization = ClientEndpoints.submitEncryptedResponse_ClientEndpoint(
                                swapName, MarketPublicRequestsURL, ENC_response, MarketAPIKey
                        ).replace("\\n", "\n").replace("\"", "")
                        file_tools.clean_file_open(swapName + "/ENC_finalization.bin", "w", ENC_finalization)
                        setSwapState(swapName, PossibleSwapStates[7], setMap=True) #responded submitted
                        responderInterface.GeneralizedENC_ResponderClaimSubroutine(
                            swapName + "/responder.json",
                            localChainAccountPassword=localChainAccountPassword,
                            crossChainAccountPassword=crossChainAccountPassword
                        )
                    elif swapState == PossibleSwapStates[6]:
                        ENC_response = file_tools.clean_file_open(swapName + "/ENC_response_path.bin", "r")
                        ENC_finalization = ClientEndpoints.submitEncryptedResponse_ClientEndpoint(
                                swapName, MarketPublicRequestsURL, ENC_response, MarketAPIKey
                        ).replace("\\n", "\n").replace("\"", "")
                        file_tools.clean_file_open(swapName + "/ENC_finalization.bin", "w", ENC_finalization)
                        setSwapState(swapName, PossibleSwapStates[7], setMap=True) #responded submitted
                        responderInterface.GeneralizedENC_ResponderClaimSubroutine(
                            swapName + "/responder.json",
                            localChainAccountPassword=localChainAccountPassword,
                            crossChainAccountPassword=crossChainAccountPassword
                        )
                    elif swapState in [
                            PossibleSwapStates[7], PossibleSwapStates[8], PossibleSwapStates[9], PossibleSwapStates[10],
                            PossibleSwapStates[11]
                    ]:
                        responderInterface.GeneralizedENC_ResponderClaimSubroutine(
                            swapName + "/responder.json",
                            localChainAccountPassword=localChainAccountPassword,
                            crossChainAccountPassword=crossChainAccountPassword,
                            reloadSwapState=swapState
                        )
        elif role == "Initiator":
            if LocalChain == "TestnetErgo" and CrossChain == "Sepolia":
                if swapState in PossibleSwapStatesInitiator:
                    if swapState == PossibleSwapStatesInitiator[0]:
                        GeneralizedENC_InitiationSubroutine(\
                            swapName, LocalChainAccountName, CrossChainAccountName, \
                            ElGamalKey, ElGamalKeyPath, LocalChain, CrossChain,\
                            localChainAccountPassword=localChainAccountPassword, crossChainAccountPassword=crossChainAccountPassword
                        )










    else:
        print("swap: ", swapName, "not found in SwapStateMap!")
        
    

