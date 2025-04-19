import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from cryptography.fernet import Fernet, InvalidToken

from encrypt_decrypt_password import encrypt_password, decrypt_password

def test_round_trip_encryption_decryption():
    # Generate a valid Fernet key
    key = Fernet.generate_key()
    original = "My$ecretPässw0rd😊"
    # Encrypt then decrypt
    encrypted = encrypt_password(original, key)
    assert isinstance(encrypted, str), "Encrypted output should be a string"
    decrypted = decrypt_password(encrypted, key)
    assert decrypted == original, "Decrypted output must match the original password"

def test_empty_password_round_trip():
    key = Fernet.generate_key()
    original = ""
    encrypted = encrypt_password(original, key)
    assert isinstance(encrypted, str)
    decrypted = decrypt_password(encrypted, key)
    assert decrypted == original

def test_decrypt_with_wrong_key_raises_invalid_token():
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    original = "AnotherSecret123"
    encrypted = encrypt_password(original, key1)
    # Attempting to decrypt with a different key should raise InvalidToken
    with pytest.raises(InvalidToken):
        decrypt_password(encrypted, key2)

def test_decrypt_with_corrupted_ciphertext_raises_invalid_token():
    key = Fernet.generate_key()
    original = "Test123"
    encrypted = encrypt_password(original, key)
    # Corrupt the ciphertext by altering characters
    corrupted = encrypted[:-1] + ("A" if encrypted[-1] != "A" else "B")
    with pytest.raises(InvalidToken):
        decrypt_password(corrupted, key)

def test_invalid_key_format_raises_error():
    # Passing a completely invalid key (wrong length/type) should raise an error on Fernet(key)
    bad_key = b"not-a-valid-fernet-key"
    with pytest.raises(Exception):
        encrypt_password("pw", bad_key)
    with pytest.raises(Exception):
        # Even decrypt should error if the key object cannot be constructed
        decrypt_password("token", bad_key)
