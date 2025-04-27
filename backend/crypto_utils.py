from cryptography.fernet import Fernet
import os

# Load or generate secret key
key_file = "secret.key"

if os.path.exists(key_file):
    with open(key_file, "rb") as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)

cipher = Fernet(key)

def encrypt_text(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()