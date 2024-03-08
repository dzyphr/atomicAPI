from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
def derive_key(password, iterations=100000):
    kdf = PBKDF2HMAC(
            algorithm=hashes.sha256(),
            length=32,
            salt=os.urandom(16),
            iterations=iterations,
            backend=default_backend()
    )
    return kdf.derive(password.encode())

def decrypt_and_write_to_file(file_path, password, replace=False):
    with open(file_path, 'rb') as f:
        salt = f.read(16)  # Read the first 16 bytes as the salt
        encrypted_data = f.read()
    key = derive_key(password, salt)
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
    key = derive_key(password, salt)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)
    with open(file_path + '.encrypted', 'wb') as f:
        f.write(salt + encrypted_data)

def decrypt_file_return_contents(file_path, password):
    with open(file_path, 'rb') as f:
        salt = f.read(16)  # Read the first 16 bytes as the salt
        encrypted_data = f.read()
    key = derive_key(password, salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)

def update_password_encrypted_env_file_key_val(file_path, password, Key, Val, new=False):
    data = decrypt_file_return_contents(file_path, password)
    updated_data = envfile_data_pattern_re_update(data, Key, Val, new)
    salt = os.urandom(16)  
    key = derive_key(password, salt)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(updated_data)
    with open(file_path, 'wb') as f:
        f.write(salt + encrypted_data)

def envfile_data_pattern_re_update(envfile_data, var, val, new=False) #updates var=val in runtime/lifetime datastream instead of ondisk
    pattern = re.compile(rf"^{var}=.+", re.MULTILINE)
    if re.search(pattern, envfile_data):
        mod = re.sub(pattern, f"{var}={val}", envfile_data)
        return mod
    else:
        print("var not found in env yet")
        if new == True:
            mod = re.sub(pattern, f"{var}={val}", envfile_data)
            return mod

