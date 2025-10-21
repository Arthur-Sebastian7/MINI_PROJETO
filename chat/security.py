# chat/security.py
from cryptography.fernet import Fernet, InvalidToken
import hashlib
import base64

def generate_key(password: str) -> bytes:
    """Gera uma chave Fernet válida a partir da senha"""
    key_bytes = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

def encrypt_message(message: str, password: str) -> str:
    """Criptografa a mensagem usando senha"""
    key = generate_key(password)
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message: str, password: str) -> str:
    """Descriptografa a mensagem usando senha"""
    key = generate_key(password)
    f = Fernet(key)
    return f.decrypt(encrypted_message.encode()).decode()
