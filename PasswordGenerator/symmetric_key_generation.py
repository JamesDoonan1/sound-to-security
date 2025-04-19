import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def derive_key(audio_hash: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """
    Derive a 32‑byte Fernet key from the audio_hash and a random salt
    using PBKDF2‑HMAC‑SHA256.
    
    :param audio_hash: Hexadecimal MD5 hash of the audio features.
    :param salt: Random salt bytes.
    :param iterations: Number of PBKDF2 iterations (default: 100,000).
    :return: URL-safe base64‑encoded key suitable for Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    key_bytes = kdf.derive(audio_hash.encode("utf-8"))
    return base64.urlsafe_b64encode(key_bytes)

def new_salt(length: int = 16) -> bytes:
    if length <= 0:
        raise ValueError("Salt length must be positive")
    return os.urandom(length)

