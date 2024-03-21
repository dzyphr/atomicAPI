from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import re
def derive_key(password, salt=None, iterations=None):
    if salt == None:
        salt = os.urandom(16)
    if iterations == None:
        iterations = 1000000
    kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=int(iterations),
            backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

def decrypt_file_return_contents(file_path, password):
    with open(file_path, 'rb') as f:
        salt = f.read(16)  # Read the first 16 bytes as the salt
        encrypted_data = f.read()
    key = derive_key(password, salt=salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)

def get_val_from_envdata_key(key, envdata):
    pattern = re.compile(rb"^" + key.encode() + rb"=(.+)", re.MULTILINE)
    match = re.search(pattern, envdata)
    if match:
        return match.group(1).decode()
    else:
        print("key: ", key, "not found in env")
        return False

