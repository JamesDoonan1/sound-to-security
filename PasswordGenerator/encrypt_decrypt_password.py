from cryptography.fernet import Fernet, InvalidToken
import time

def encrypt_password(password: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted = f.encrypt(password.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_password(encrypted_password: str, key: bytes) -> str:
    f = Fernet(key)
    start_time = time.perf_counter()

    try:
        decrypted = f.decrypt(encrypted_password.encode('utf-8'))
        result = decrypted.decode('utf-8')
    except Exception:
        # Simulate decryption time using dummy cryptographic work
        dummy_token = Fernet.generate_key()
        dummy_f = Fernet(dummy_token)
        try:
            dummy_f.decrypt(encrypted_password.encode('utf-8'))
        except Exception:
            pass
        result = None

    end_time = time.perf_counter()
    _ = end_time - start_time  # Always compute elapsed time

    if result is None:
        raise InvalidToken("Decryption failed")

    return result
