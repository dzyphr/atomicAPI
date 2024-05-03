import file_tools, os

def setSwapState(swapName, state):
    if state not in ["initiated", "uploadingResponseContract", "fundingResponseContract", "responded", "finalized", "verifyingFinalizedContractValues", "claiming", "refunding", "claimed", "refunded", "terminated", "tbd"]:
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


