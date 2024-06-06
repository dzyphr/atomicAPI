import file_tools, os, uuid, responderInterface, json_tools, subprocess, sys, json, ClientEndpoints, initiatorInterface

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
#            if os.path.isfile("SwapStateMap") == False: #should be handled by REST APIS
#                file_tools.clean_file_open("SwapStateMap", "w", "{}") 
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
                OrderTypeUUID = file_tools.clean_file_open(swapName + "/OrderTypeUUID", "r")
                OrderTypesJSON =  json_tools.ojf("OrderTypes.json")
                CoinA_Price = OrderTypesJSON[OrderTypeUUID]["CoinA_price"]
                CoinB_Price = OrderTypesJSON[OrderTypeUUID]["CoinB_price"]
                if swapState in PossibleSwapStatesInitiator:
                    initiatorJSONPath = swapName + "/initiator.json"

                    if swapState == PossibleSwapStatesInitiator[0]: #initiating
                        #swaps that break here should just be reinitiated
                        #no reason to reload
                        return
                    if swapState == PossibleSwapStatesInitiator[1]: #initiated_unsubmitted
                        #have to return because basically waiting for client to request initiation again from their state reload
                        #probably very rare case
                        return
                    if swapState == PossibleSwapStatesInitiator[2]: #initiated_submitted
                        #technically we're still waiting for a response here
                        #so because of that we shouldn't move forward with finalizing
                        return
                    if swapState == PossibleSwapStatesInitiator[3]: #responded
                        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                            initiatorJSONPath, CoinA_Price, CoinB_Price, 
                            localchainpassword=localChainAccountPassword, crosschainpassword=crossChainAccountPassword
                        )
                        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(
                            initiatorJSONPath, 
                            localchainpassword=localChainAccountPassword, crosschainpassword=crossChainAccountPassword
                        )
                    if swapState in [
                           PossibleSwapStatesInitiator[4], #verifying_response
                           PossibleSwapStatesInitiator[5], #verified_response
                           PossibleSwapStatesInitiator[6]  #finalizing
                    ]:
                        initiatorInterface.GeneralizedENC_FinalizationSubroutine(
                            initiatorJSONPath, CoinA_Price, CoinB_Price,
                            localchainpassword=localChainAccountPassword, crosschainpassword=crossChainAccountPassword,
                            swapStateReload=swapState
                        )
                        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(
                            initiatorJSONPath, 
                            localchainpassword=localChainAccountPassword, crosschainpasswordcross=ChainAccountPassword
                        )
                    if swapState in [
                            PossibleSwapStatesInitiator[7], PossibleSwapStatesInitiator[8], 
                            PossibleSwapStatesInitiator[9], PossibleSwapStatesInitiator[10]
                    ]:      #finalized_unsubmitted finalized_submitted claiming or refunding
                        initiatorInterface.GeneralizedENC_InitiatorClaimSubroutine(
                            initiatorJSONPath, 
                            localchainpassword=localChainAccountPassword, crosschainpassword=crossChainAccountPassword
                        )

                    #if the state is something like initiating or responded in which case we had a shutdown when prompted to
                    #generate swap data and return it to the client, we should generate the data, expecting that the client 
                    #will reconnect because we cant force a reconnection to the client
                    #client could call state reload if they shutdown or lose connection with server
                    #this facilitates state reload for server although server still should
                    #keep track of whether its already generated the swap data asked for
                    #or if its already uploaded or is uploading the finalization contract
                    #to prevent the server being confused and running duplicate commands for the same data
                    #if the state is finalized we can run checkschnorrtreeforclaim aka GeneralizedENC_InitiatorClaimSubroutine
                    #to handle a refund


    else:
        print("swap: ", swapName, "not found in SwapStateMap!")
        
    

