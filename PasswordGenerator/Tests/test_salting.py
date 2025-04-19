import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import base64
import sqlite3

import pytest

import database_control
from symmetric_key_generation import derive_key, new_salt
from encrypt_decrypt_password import encrypt_password, decrypt_password
from database_control import (
    initialize_db,
    store_encrypted_password,
    get_encrypted_password_by_hash,
)

def test_salts_are_random():
    salt1 = new_salt()
    salt2 = new_salt()
    assert isinstance(salt1, bytes) and isinstance(salt2, bytes)
    assert salt1 != salt2, "new_salt() should produce different bytes each time"

def test_key_derivation_deterministic():
    audio_hash = "abcdef1234567890abcdef1234567890"
    salt = new_salt()
    key1 = derive_key(audio_hash, salt)
    key2 = derive_key(audio_hash, salt)
    assert key1 == key2
    key3 = derive_key(audio_hash, new_salt())
    assert key3 != key1

def test_encrypt_decrypt_roundtrip():
    audio_hash = "abcdef1234567890abcdef1234567890"
    salt = new_salt()
    key = derive_key(audio_hash, salt)

    original = "S3cureP@ssw0rd"
    encrypted = encrypt_password(original, key)
    decrypted = decrypt_password(encrypted, key)
    assert decrypted == original

def test_full_db_flow(tmp_path):
    # Create a temp database file
    db_file = tmp_path / "test.db"
    # Override the DB_PATH in the module under test
    database_control.DB_PATH = str(db_file)

    # Initialize fresh database
    initialize_db()

    audio_hash = "deadbeefdeadbeefdeadbeefdeadbeef"
    salt = new_salt()
    key = derive_key(audio_hash, salt)
    original_pw = "MyT3stP@ss"

    # Store a record
    store_encrypted_password(
        username="testuser",
        audio_hash=audio_hash,
        salt=base64.b64encode(salt).decode("utf-8"),
        encrypted_password=encrypt_password(original_pw, key)
    )

    # Retrieve it and decrypt
    usr, b64_salt, enc_pw = get_encrypted_password_by_hash(audio_hash)
    assert usr == "testuser"
    salt_db = base64.b64decode(b64_salt)
    key_db = derive_key(audio_hash, salt_db)
    assert decrypt_password(enc_pw, key_db) == original_pw

if __name__ == "__main__":
    pytest.main([__file__])
