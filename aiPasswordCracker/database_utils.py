import sqlite3

DB_PATH = "passwords.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS hash_passwords (
        hash TEXT PRIMARY KEY,
        encrypted_password TEXT
    );
    """)
    conn.commit()
    conn.close()

def store_encrypted_password(audio_hash: str, encrypted_password: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO hash_passwords (hash, encrypted_password) VALUES (?, ?)",
        (audio_hash, encrypted_password)
    )
    conn.commit()
    conn.close()

def get_encrypted_password(audio_hash: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT encrypted_password FROM hash_passwords WHERE hash = ?", (audio_hash,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
