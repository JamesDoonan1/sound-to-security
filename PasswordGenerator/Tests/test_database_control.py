import sys, os
import sqlite3
import base64
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database_control

from database_control import (
    initialize_db,
    store_encrypted_password,
    get_encrypted_password,
    get_encrypted_password_by_hash,
    DB_PATH,
)

from symmetric_key_generation import derive_key, new_salt
from encrypt_decrypt_password import encrypt_password


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """
    Create a temporary SQLite database and patch DB_PATH to point at it.
    """
    db_file = tmp_path / "test_passwords.db"
    monkeypatch.setattr(database_control, "DB_PATH", str(db_file))
    return str(db_file)


def test_initialize_db_creates_table(tmp_db):
    # Should not raise
    initialize_db()
    conn = sqlite3.connect(tmp_db)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='hash_passwords';"
    )
    assert cursor.fetchone() is not None, "hash_passwords table was not created"
    conn.close()


def test_get_on_empty_db_returns_none(tmp_db):
    initialize_db()
    # No records, should return None or (None,None,None)
    pw = get_encrypted_password("alice", "hash1")
    assert pw is None
    user, salt, enc = get_encrypted_password_by_hash("hash1")
    assert (user, salt, enc) == (None, None, None)


def test_store_and_get_by_username_and_hash(tmp_db):
    initialize_db()
    # Prepare data
    username = "bob"
    audio_hash = "abcd1234"
    salt = new_salt()
    key = derive_key(audio_hash, salt)
    original_pw = "SecretPwd1!"
    encrypted = encrypt_password(original_pw, key)
    b64_salt = base64.b64encode(salt).decode("utf-8")

    # Store
    store_encrypted_password(username, audio_hash, b64_salt, encrypted)

    # Retrieve by username+hash
    retrieved = get_encrypted_password(username, audio_hash)
    assert retrieved == encrypted

    # Retrieve by hash only
    user2, salt2, enc2 = get_encrypted_password_by_hash(audio_hash)
    assert user2 == username
    assert salt2 == b64_salt
    assert enc2 == encrypted


def test_store_replaces_existing(tmp_db):
    initialize_db()
    username = "carol"
    audio_hash = "hashXYZ"
    # First store
    salt1 = new_salt()
    key1 = derive_key(audio_hash, salt1)
    pw1 = "FirstPwd"
    enc1 = encrypt_password(pw1, key1)
    b64_salt1 = base64.b64encode(salt1).decode()
    store_encrypted_password(username, audio_hash, b64_salt1, enc1)

    # Overwrite with new salt and password
    salt2 = new_salt()
    key2 = derive_key(audio_hash, salt2)
    pw2 = "SecondPwd"
    enc2 = encrypt_password(pw2, key2)
    b64_salt2 = base64.b64encode(salt2).decode()
    store_encrypted_password(username, audio_hash, b64_salt2, enc2)

    # Retrieval should reflect second values
    got = get_encrypted_password(username, audio_hash)
    assert got == enc2

    user, salt_ret, enc_ret = get_encrypted_password_by_hash(audio_hash)
    assert user == username
    assert salt_ret == b64_salt2
    assert enc_ret == enc2


def test_primary_key_constraints(tmp_db):
    initialize_db()
    username = "dave"
    audio_hash = "uniqueHash"
    salt = new_salt()
    key = derive_key(audio_hash, salt)
    pw = "Pwd123"
    enc = encrypt_password(pw, key)
    b64_salt = base64.b64encode(salt).decode()

    # Insert twice with same username+hash but different enc
    store_encrypted_password(username, audio_hash, b64_salt, enc)
    # Attempting a second insert with same PK but different encrypted password
    enc_new = encrypt_password(pw + "X", key)
    store_encrypted_password(username, audio_hash, b64_salt, enc_new)

    # The latest should prevail
    assert get_encrypted_password(username, audio_hash) == enc_new


def test_db_path_default_unchanged():
    # Ensure the module-level DB_PATH constant exists
    assert hasattr(database_control, "DB_PATH")
    assert isinstance(database_control.DB_PATH, str)
