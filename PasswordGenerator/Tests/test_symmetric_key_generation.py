import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest

from symmetric_key_generation import derive_key, new_salt

def test_new_salt_default_length():
    salt = new_salt()
    assert isinstance(salt, bytes)
    assert len(salt) == 16

def test_new_salt_custom_length():
    salt = new_salt(32)
    assert isinstance(salt, bytes)
    assert len(salt) == 32

def test_new_salt_randomness():
    salts = {new_salt() for _ in range(50)}
    assert len(salts) >= 45  # Ensure high randomness

def test_derive_key_returns_bytes():
    key = derive_key("hash123", new_salt())
    assert isinstance(key, bytes)
    assert len(key) == 44  # Base64-encoded 32 bytes

def test_derive_key_is_deterministic_for_same_input():
    salt = b'\x00' * 16
    hash_val = "testhash"
    key1 = derive_key(hash_val, salt)
    key2 = derive_key(hash_val, salt)
    assert key1 == key2

def test_derive_key_changes_with_different_salts():
    h = "sample"
    key1 = derive_key(h, b"A" * 16)
    key2 = derive_key(h, b"B" * 16)
    assert key1 != key2

def test_derive_key_changes_with_different_hashes():
    salt = b"\x10" * 16
    key1 = derive_key("hash1", salt)
    key2 = derive_key("hash2", salt)
    assert key1 != key2

def test_derive_key_different_iterations_yield_different_keys():
    salt = b"\x01" * 16
    key1 = derive_key("mypassword", salt, iterations=10000)
    key2 = derive_key("mypassword", salt, iterations=20000)
    assert key1 != key2

def test_derive_key_empty_string_hash():
    salt = new_salt()
    key = derive_key("", salt)
    assert isinstance(key, bytes)
    assert len(key) == 44

def test_derive_key_invalid_hash_type():
    with pytest.raises(AttributeError):
        derive_key(None, new_salt())

def test_derive_key_invalid_salt_type():
    with pytest.raises(TypeError):
        derive_key("validhash", "not_bytes")

def test_new_salt_invalid_zero_length():
    with pytest.raises(ValueError):
        new_salt(0)

def test_new_salt_invalid_negative_length():
    with pytest.raises(ValueError):
        new_salt(-5)
