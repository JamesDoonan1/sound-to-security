from cryptography.fernet import Fernet

def encrypt_password(password: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted = f.encrypt(password.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_password(encrypted_password: str, key: bytes) -> str:
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_password.encode('utf-8'))
    return decrypted.decode('utf-8')
