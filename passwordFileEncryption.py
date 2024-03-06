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

def encrypt_file(file_path, password):
    with open(file_path, 'rb') as f:
        data = f.read()
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
#    with open(file_path[:-10], 'wb') as f:  # remove the '.encrypted' extension
#        f.write(decrypted_data)


