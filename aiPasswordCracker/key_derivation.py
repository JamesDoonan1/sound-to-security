import hashlib
import base64

def derive_key_from_hash(audio_hash: str) -> bytes:
    # audio_hash: MD5 hex string
    # Convert hex to bytes
    hash_bytes = bytes.fromhex(audio_hash)
    # Use SHA-256 to derive a 32-byte key
    sha_key = hashlib.sha256(hash_bytes).digest()
    # Fernet keys must be URL-safe base64-encoded 32-byte keys
    key = base64.urlsafe_b64encode(sha_key)
    return key
