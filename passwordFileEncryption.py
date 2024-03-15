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

def decrypt_and_write_to_file(file_path, password, replace=False):
    with open(file_path, 'rb') as f:
        salt = f.read(16)  # Read the first 16 bytes as the salt
        encrypted_data = f.read()
    key = derive_key(password, salt=salt)
    fernet = Fernet(key)
    decrypted_data =  fernet.decrypt(encrypted_data)
    with open(file_path[:-10], 'wb') as f:  # remove the '.encrypted' extension
        f.write(decrypted_data)


def encrypt_file(file_path, password, delete=False): #d: if True delete the plaintext file on success case
    with open(file_path, 'rb') as f:
        data = f.read()
        if delete == True:
            os.remove(file_path)
    salt = os.urandom(16)  # Generate a random 16-byte salt
    key = derive_key(password, salt=salt)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)
    with open(file_path + '.encrypted', 'wb') as f:
        f.write(salt + encrypted_data)

def decrypt_file_return_contents(file_path, password):
    with open(file_path, 'rb') as f:
        salt = f.read(16)  # Read the first 16 bytes as the salt
        encrypted_data = f.read()
    key = derive_key(password, salt=salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)
   
def update_password_encrypted_env_file_key_val(file_path, password, Key, Val, new=False):
    data = decrypt_file_return_contents(file_path, password)
    updated_data = envfile_data_pattern_re_update(data, Key, Val, new)
    salt = os.urandom(16)  
    key = derive_key(password, salt=salt)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(updated_data)
    with open(file_path, 'wb') as f:
        f.write(salt + encrypted_data)

def get_val_from_envdata_key(key, envdata):
    pattern = re.compile(rb"^" + key.encode() + rb"=(.+)", re.MULTILINE)
    match = re.search(pattern, envdata)
    if match:
        return match.group(1).decode()
    else:
        print("key: ", key, "not found in env")
        return False

def envfile_data_pattern_re_update(envfile_data, var, val, new=False): #updates var=val in runtime/lifetime datastream instead of ondisk
    pattern = re.compile(rf"^{var}=.+", re.MULTILINE)
    if re.search(pattern, envfile_data):
        mod = re.sub(pattern, f"{var}={val}", envfile_data)
        return mod
    else:
        print("var not found in env yet")
        if new == True:
            mod = re.sub(pattern, f"{var}={val}", envfile_data)
            return mod

def proveEncEnvFilePasswordKnowledge(encenvfilepath, password):
    if os.path.isfile(encenvfilepath):
        data = decrypt_file_return_contents(encenvfilepath, password)
        if data.startswith(b'[default]'):
            print("True")
            return True
        else:
            print("False")
            return False
    else:
        print("path: ", encenvfilepath, "not found")
        return False
