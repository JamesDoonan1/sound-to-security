import sqlite3

DB_PATH = "passwords.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS hash_passwords (
        username TEXT,
        hash TEXT,
        encrypted_password TEXT,
        PRIMARY KEY (username, hash)
    );
    """)
    conn.commit()
    conn.close()

def store_encrypted_password(username: str, audio_hash: str, encrypted_password: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO hash_passwords (username, hash, encrypted_password) VALUES (?, ?, ?)",
        (username, audio_hash, encrypted_password)
    )
    conn.commit()
    conn.close()

def get_encrypted_password(username: str, audio_hash: str) -> str:
    """
    Returns the encrypted_password if the record exists; otherwise, returns None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT encrypted_password FROM hash_passwords WHERE username = ? AND hash = ?",
        (username, audio_hash)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
