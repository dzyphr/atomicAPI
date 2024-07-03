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
        logger = logging.getLogger(__name__)
        logger.info(f'{logstr}\nsession:{sessionID_hash}')

#TODO use avaialable logging levels to seperate logging detail configurations
# https://docs.python.org/3/library/logging.html#logging-levels
