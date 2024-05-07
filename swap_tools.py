import file_tools, os, uuid, responderInterface

PossibleSwapStates = ["initiated", "uploadingResponseContract", "uploadedResponseContract", "fundingResponseContract", "fundedResponseContract", "responding", "responded", "finalized", "verifyingFinalizedContractValues", "claiming", "refunding", "claimed", "refunded", "terminated", "tbd"]

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
