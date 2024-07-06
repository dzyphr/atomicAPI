import hashlib, secrets, config_tools, logging
def randsha256():
    sha256 = hashlib.sha256()
    sha256.update(secrets.randbits(256).to_bytes(64, "big"))
    return sha256.digest().hex()



sessionID_hash = randsha256()

def LOG(logstr):
    if config_tools.valFromConf(".env", "LOGGING").strip("\"") == "True":
        logger = logging.getLogger(__name__)
        logging.basicConfig(filename="atomicAPI.log", level=logging.INFO)
        logger.info(f'{logstr}\nsession:{sessionID_hash}')

#TODO use avaialable logging levels to seperate logging detail configurations
# https://docs.python.org/3/library/logging.html#logging-levels


def AUTOTESTLOG(logstr, kind):
    logger = logging.getLogger(sessionID_hash)
    filename = f'autotest-{sessionID_hash}.log'
    if not logger.handlers:
        autotesthandler = logging.FileHandler(filename)
        autotesthandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(autotesthandler)
    if kind == "err":
        autotesthandler = logging.FileHandler(filename)
        autotesthandler.setLevel(logging.ERROR)
        logger.error(f'{logstr}')
        return
    elif kind == "info":
        autotesthandler = logging.FileHandler(filename)
        autotesthandler.setLevel(logging.INFO)
        logger.info(f'{logstr}')
        return 
