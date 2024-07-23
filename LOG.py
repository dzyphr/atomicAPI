import hashlib, secrets, config_tools, logging, os
def randsha256():
    sha256 = hashlib.sha256()
    sha256.update(secrets.randbits(256).to_bytes(64, "big"))
    return sha256.digest().hex()



sessionID_hash = str(randsha256())

def LOG(logstr):
    if config_tools.valFromConf(".env", "LOGGING").strip("\"") == "True":
        logger = logging.getLogger(sessionID_hash)
        if not logger.handlers:
            logHandler = logging.FileHandler("atomicAPI.log")
            logHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(logHandler)
#            logging.basicConfig(filename="atomicAPI.log")
        logger.setLevel(logging.INFO)
        logger.info(f'{logstr}\nsession:{sessionID_hash}')

#TODO use avaialable logging levels to seperate logging detail configurations
# https://docs.python.org/3/library/logging.html#logging-levels


def AUTOTESTLOG(logstr, kind, watch=False, platform="Ubuntu"):
    filename = f'autotest-{sessionID_hash}.log'
    logger = logging.getLogger(filename)
    if not logger.handlers:
        autotesthandler = logging.FileHandler(filename)
        autotesthandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(autotesthandler)
        if watch == True:
            if platform == "Ubuntu":
                os.popen(f'gnome-terminal -- bash -c "watch -n 1 \'tail -48 {filename}\'"').read()
        print(f'Logging to: {filename}')
    if kind == "err":
        autotesthandler = logging.FileHandler(filename)
        autotesthandler.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
        logger.error(f'{logstr}')
        return
    elif kind == "info":
        autotesthandler = logging.FileHandler(filename)
        autotesthandler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.info(f'{logstr}')
        return 
