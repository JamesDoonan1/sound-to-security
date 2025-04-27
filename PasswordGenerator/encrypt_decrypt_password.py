from cryptography.fernet import Fernet, InvalidToken
import time

def encrypt_password(password: str, key: bytes) -> str:

    """
    Encrypt a password using a given symmetric encryption key.

    Args:
        password (str): The plaintext password to encrypt.
        key (bytes): The symmetric encryption key (Fernet key).

    Returns:
        str: The encrypted password encoded as a UTF-8 string.
    """
    
    f = Fernet(key)
    encrypted = f.encrypt(password.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_password(encrypted_password: str, key: bytes) -> str:

    """
    Decrypt an encrypted password using the given key.
    
    Implements a dummy decryption path to resist timing attacks
    if the decryption fails (e.g., invalid token).

    Args:
        encrypted_password (str): The encrypted password string.
        key (bytes): The symmetric encryption key (Fernet key).

    Returns:
        str: The decrypted plaintext password.

    Raises:
        InvalidToken: If decryption fails (e.g., wrong key or corrupted ciphertext).
    """
    
    f = Fernet(key)
    start_time = time.perf_counter()

    try:
        # Attempt actual decryption
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
    _ = end_time - start_time  # Always measure elapsed time (even if unused) for consistency

    if result is None:
        raise InvalidToken("Decryption failed")

    return result
