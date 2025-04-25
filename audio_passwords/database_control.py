import sqlite3
import os

# Ensure paths are properly handled
DB_PATH = "passwords.db"

def initialize_db():
    """Initialize the database with the updated schema that includes username and salt"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS hash_passwords (
        username TEXT,
        hash TEXT,
        salt TEXT,
        encrypted_password TEXT,
        PRIMARY KEY (username, hash)
    );
    """)
    conn.commit()
    conn.close()

def store_encrypted_password(username: str, audio_hash: str, salt: str, encrypted_password: str):
    """
    Store or update the encrypted password along with its salt and username.
    
    Args:
        username: The username associated with this password
        audio_hash: The hash of the audio features
        salt: The base64-encoded salt used for key derivation
        encrypted_password: The encrypted password string
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO hash_passwords (username, hash, salt, encrypted_password) VALUES (?, ?, ?, ?)",
        (username, audio_hash, salt, encrypted_password)
    )
    conn.commit()
    conn.close()

def get_encrypted_password(username: str, audio_hash: str) -> str:
    """
    Returns the encrypted_password if the record exists for the given username and hash; 
    otherwise, returns None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT encrypted_password FROM hash_passwords WHERE username = ? AND hash = ?",
        (username, audio_hash)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_encrypted_password_by_hash(audio_hash: str):
    """
    Returns a tuple (username, salt, encrypted_password) for the given hash,
    or (None, None, None) if not found.
    
    This allows looking up by hash only, which is useful for the initial login process
    before the username is verified.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT username, salt, encrypted_password FROM hash_passwords WHERE hash = ?",
        (audio_hash,)
    )
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None, None)