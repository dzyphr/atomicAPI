import secrets
import string

def generate_bearer_RESTAPI_key(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))
