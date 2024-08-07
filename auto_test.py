#automated tests
import requests, json, uuid, json_tools, file_tools, AtomicityInterface, SigmaParticleInterface, time, os, psutil, signal, swap_tools
from threading import Thread, Event
from LOG import AUTOTESTLOG
def pid_by_name(procName):
    for proc in psutil.process_iter(['pid', 'name']):
        if procName == proc.info['name']:
            return proc.info['pid']
    return False

def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return (gone, alive)


def state_reload_test_checkpoint(swapID, role="", stateReloadTest="", platform=""):
    if stateReloadTest == "":
        return None
    if checkSwapState(swapID, stateReloadTest) == False:
        return None
    if role == "Client":
        procName = "AASwapClientRESTAPI"
    elif role == "Server":
        procName = "AASwapServerRESTAPI"
    if platform == "Ubuntu":
        cmd = f'gnome-terminal -- bash -c "./{procName}"'
    else:
        print(f'Unhandled Platform: {platform}')
        AUTOTESTLOG(f'Unhandled Platform: {platform}', "err")
        return False
    while pid_by_name(procName) != False:
        pid = pid_by_name(procName)
        AUTOTESTLOG(f'StateReloadTest: Killing {procName} Proccess ID: {pid}', "info")
        pgid = os.getpgid(pid)
        kptres = kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None)
        print(kptres)
    AUTOTESTLOG(f'StateReloadTest: Restarting {procName}', "info")
    os.popen(cmd).read()
    return True


#states = []

def state_reload_test_worker(stop_event, swapID, role="", stateReloadTest="", platform=""):
    states = []
    while not stop_event.is_set():
        if stateReloadTest != "all":
            if state_reload_test_checkpoint(swapID, role=role, stateReloadTest=stateReloadTest, platform=platform) == True:
                AUTOTESTLOG(f"Reloading on SwapState: {stateReloadTest}", "info")
                break
            else:
                continue
        elif stateReloadTest == "all":
            if role == "Client":
                PossibleStates = swap_tools.PossibleSwapStates
            elif role == "Server":
                PossibleStates = swap_tools.PossibleSwapStatesInitiator
            for state in PossibleStates:
                if state in [ \
                        *swap_tools.PossibleSwapStates[12:16], \
                        *swap_tools.PossibleSwapStatesInitiator[10:14] \
                ]: #ignore end states for now
                    return
                print(state)
                if state not in states:
                    states.append(state)
                else:
                    break
                AUTOTESTLOG(f"Reloading on SwapState: {state}", "info")
                if state in [ \
                        *swap_tools.PossibleSwapStates[5:8], \
                        *swap_tools.PossibleSwapStatesInitiator[0:2] \
                ]: #these states happen near instantly so give them few tries only to prevent hang
                    retries = 3
                    while retries > 0:
                        if state_reload_test_checkpoint(swapID, role=role, stateReloadTest=state, platform=platform) == True:
                            break
                        else:
                            retries -= 1
                            continue
                else:
                    while True:
                        if state_reload_test_checkpoint(swapID, role=role, stateReloadTest=state, platform=platform) == True:
                            break
                        else:
                            continue



def checkSwapState(swapID, state):
    SwapState = file_tools.clean_file_open(f'{swapID}/SwapState', "r") #swaptools getswapstate?
    if SwapState == state:
        return True
    elif SwapState != state:
        return False

def checkElGQGChannelCorrectness(QG, privateAPIKey):
    url = "http://localhost:3031/v0.0.1/requests"
    data = json.dumps({
        "id": str(uuid.uuid4()),
        "request_type": "checkElGQGChannelCorrectness",
        "QGChannel": QG
    })
    headers = {
        "Authorization": f'Bearer {privateAPIKey}',
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=data, headers=headers).text
    return response

def automated_test_local_server_side(watch=False, platform="Ubuntu", stateReloadTest="", clientTargetPath=""):
    SwapTicketID = start_swap_from_local_client(watch=watch, clientTargetPath=clientTargetPath)
    if stateReloadTest != "":
        stop_event = Event()
        thread = Thread(target=state_reload_test_worker, args=( \
                stop_event, SwapTicketID, "Server", stateReloadTest, platform \
        ))
        thread.start()
    AUTOTESTLOG(f'Started SwapTicketID: {SwapTicketID}', "info")
    init_J_filepath = f'{SwapTicketID}/initiator.json'
    file_tools.wait_for_file(init_J_filepath)
    init_J = json_tools.ojf(init_J_filepath)  
    ENC_init_filepath = init_J["ENC_Init_PATH"]
    file_tools.wait_for_file(ENC_init_filepath)
    AUTOTESTLOG(f'Swap {SwapTicketID} Intiated on Server', "info")
    DEC_Response_PATH = init_J["DEC_Response_PATH"]
    file_tools.wait_for_file(DEC_Response_PATH)
    while True:
        try:
            init_J = json_tools.ojf(init_J_filepath)
            init_J["counterpartyContractFundedAmount"]
            break
        except (KeyError, json.decoder.JSONDecodeError) as e:
            time.sleep(3)
            continue
    AUTOTESTLOG( \
            f'Swap {SwapTicketID} got a  Response from the Client. \nAmount Funded: {init_J["counterpartyContractFundedAmount"]}', \
            'info' \
    )
    AUTOTESTLOG('Finalizing...', "info")
    ENC_finalizationPATH = init_J["ENC_finalizationPATH"]
    file_tools.wait_for_file(ENC_finalizationPATH)
    AUTOTESTLOG(f'Swap {SwapTicketID} Finalized on Server', "info")
    atomicClaim_tx1path = f'{SwapTicketID}/atomicClaim_tx1'
    file_tools.wait_for_file(atomicClaim_tx1path)
    atomicClaim_tx = json_tools.ojf(atomicClaim_tx1path)["outputs"][0]

    AUTOTESTLOG(f'Swap {SwapTicketID} Claimed by Client.\nTx: {atomicClaim_tx}\nClaiming from responder\'s contract.', "info")
    init_J = json_tools.ojf(init_J_filepath)
    while int(AtomicityInterface.Atomicity_CheckContractFunds(SwapTicketID, init_J)) != 0:
        init_J = json_tools.ojf(init_J_filepath)
        time.sleep(10)
    AUTOTESTLOG(f'Swap {SwapTicketID} Claimed by Server', 'info')
    #TODO find receiverClaim tx from contract addr to ensure claim
    AUTOTESTLOG(f'Succesful Claim. AutoTest finished!', "info")
    if stateReloadTest != "":
       stop_event.set()

def start_swap_from_local_client(watch=False, clientTargetPath=""):
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

    amount = 0.02

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
        AUTOTESTLOG(f'{localChain} account not found!', "err", watch=watch)
        print(f'{localChain} account not found!')
        exit()
    elif crossChainAccount == "":
        AUTOTESTLOG(f'{crossChain} account not found!', "err", watch=watch)
        print(f'{crossChain} account not found!')
        exit()

    CoinA_price = OrderTypes[OrderTypeUUID]["CoinA_price"]
    CoinB_price = OrderTypes[OrderTypeUUID]["CoinB_price"]

    MarketQGChannelsURL = localMarketServerOrderTypesURL.replace("ordertypes", "publicrequests/ElGamalQGChannels")
    MarketPubKeysURL = localMarketServerOrderTypesURL.replace("ordertypes", "publicrequests/ElGamalPubs")
    MarketQGPubKeyArrayURL = localMarketServerOrderTypesURL.replace("ordertypes", "publicrequests/QGPubkeyArray")
    
    MarketQGPubKeyArray = json.loads(requests.get(MarketQGPubKeyArrayURL).json())

    privateAPIKey = json_tools.ojf(f"{clientTargetPath}accepted_private_api_keys.json")["0"]

    #If you get badapikey you're probably running this from your server, this test is for client side

    localQGPubkeyArrayURL = "http://localhost:3031/v0.0.1/QGPubkeyArray"
    localQGPubkeyArray = json.loads(requests.get(localQGPubkeyArrayURL).json())

    localElGamalPubsURL = "http://localhost:3031/v0.0.1/ElGamalPubs"
    localElGamalPubs = json.loads(requests.get(localElGamalPubsURL).json())

    compatchannel = ""
    compatkey = ""
    marketElGKey = ""
    #get a compatible ElGamal Key
    for channel in MarketQGPubKeyArray:
        if checkElGQGChannelCorrectness(channel, privateAPIKey).strip("\"") == "true":
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
                        "id": uuid.uuid4(),
                        "request_type": "generateElGKeySpecificQG",
                        "QGChannel": QG
                }
                url = "http://localhost:3031/v0.0.1/requests"
                headers = {
                    "Authorization": f'Bearer {privateAPIKey}',
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
            "Authorization": f'Bearer {privateAPIKey}',
            "Content-Type": "application/json"
    }
    url = "http://localhost:3031/v0.0.1/requests"
    AUTOTESTLOG(f'Client Data Collected Successfully, Starting Swap', "info", watch=watch)

    #TODO create stateReloadAll test, either constantly kill and restart the state during the same swap, or run a 
    #new swap for each state reload test possible


    response = requests.post( \
        url, data=startSwapFromUIData, headers=headers \
    ).text.replace("\n", "").replace("\r","").replace("\t","")[1:-1].replace("\\", '')[1:-1]
    SwapTicketID = json.loads(response)["SwapTicketID"]
    return SwapTicketID

def automated_test_local_client_side(watch=False, platform="Ubuntu", stateReloadTest=""):
    SwapTicketID = start_swap_from_local_client(watch=watch)

    if stateReloadTest != "":
        stop_event = Event()
        thread = Thread(target=state_reload_test_worker, args=( \
                stop_event, SwapTicketID, "Client", stateReloadTest, platform \
        ))
        thread.start()
    AUTOTESTLOG(f'Returned SwapTicketID: {SwapTicketID}', "info")

    #Check for contract upload
    responderJSONPath = f'{SwapTicketID}/responder.json'
    file_tools.wait_for_file(responderJSONPath)
    responderJSON = json_tools.ojf(f'{SwapTicketID}/responder.json')
    while "responderContractAddr" not in json_tools.ojf(f'{SwapTicketID}/responder.json').keys():
        time.sleep(5)
    responderJSON = json_tools.ojf(f'{SwapTicketID}/responder.json')
    AUTOTESTLOG(f'Contract Deployed: {responderJSON["responderContractAddr"]}', "info")

    #Check for contract funding
    while True:
        ContactFundedAmount = int(AtomicityInterface.Atomicity_CheckContractFunds(SwapTicketID, responderJSON))
        if ContactFundedAmount == 0:
            time.sleep(5)
        else:
            break

#    ContactFundedAmount = AtomicityInterface.Atomicity_CheckContractFunds(SwapTicketID, responderJSON)
    AUTOTESTLOG(f'Contract Funded: {ContactFundedAmount}', "info", watch=watch)

    #Check for finalization contract
    while "boxId" not in json_tools.ojf(f'{SwapTicketID}/responder.json').keys():
        time.sleep(5)

    responderJSON = json_tools.ojf(f'{SwapTicketID}/responder.json')
    AUTOTESTLOG(f'Finalization Contract BoxID: {responderJSON["boxId"]}', "info")
    BoxID = responderJSON["boxId"]
    addr = SigmaParticleInterface.SigmaParticle_box_to_addr(BoxID, SwapTicketID)

    #Check claim from finalization contract was successful
    while os.path.isfile(SwapTicketID + "/atomicClaim_tx1") == False:
        boxFilterCmd = \
            "cd " + SigmaParticleInterface.SigmaParticlePath + "boxFilter && " + \
            "./deploy.sh " + addr + " " + BoxID + " ../../../" + SwapTicketID + "/atomicClaim "
        boxFilter = os.popen(boxFilterCmd).read()
        time.sleep(5)
    txjson = json_tools.ojf(SwapTicketID + "/atomicClaim_tx1")
    txid = txjson["id"]
    AUTOTESTLOG(f'Succesful Claim! Claim Transaction ID: {txid}\nAutoTest finished!', "info")
    if stateReloadTest != "":
       stop_event.set() 
