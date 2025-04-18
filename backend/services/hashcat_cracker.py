import subprocess
import os
import os

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/data"))

HASHCAT_PATH = r"C:\Users\James Doonan\Downloads\hashcat-6.2.6\hashcat-6.2.6\hashcat.exe"
HASH_FILE = os.path.join(DATA_DIR, "password_hash.txt")
WORDLIST_FILE = os.path.join(DATA_DIR, "rockyou.txt")

def save_hash(password_hash):
    """Saves the given hash to a file for Hashcat processing."""
    with open(HASH_FILE, "w") as f:
        f.write(password_hash + "\n")

def crack_password_with_hashcat(hash_type="0", attack_mode="3"):
    """
    Runs Hashcat to attempt cracking the password.
    
    - hash_type: Hashcat mode for hashing algorithm (default: 0 for MD5).
    - attack_mode: Attack type (default: 3 for brute-force, 0 for dictionary attack).
    
    Returns:
        - Crack status (bool)
        - Cracked password (str) or None if unsuccessful.
    """

    if not os.path.exists(HASH_FILE):
        return False, " Hash file not found!"

    # Hashcat command
    command = [
        HASHCAT_PATH,
        "--force",
        "-m", hash_type,  # Hash type (MD5, SHA256, etc.)
        "-a", attack_mode,  # Attack mode (3 = brute-force, 0 = dictionary)
        HASH_FILE,
        "?a?a?a?a?a?a" if attack_mode == "3" else WORDLIST_FILE,  # Mask for brute-force, wordlist for dictionary
        "--show"  # Shows cracked passwords
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if password was cracked
        if result.returncode == 0 and result.stdout.strip():
            cracked_password = result.stdout.strip().split(":")[-1]  # Extract password
            return True, cracked_password
        else:
            return False, " No password cracked!"
    
    except Exception as e:
        return False, f" Error running Hashcat: {str(e)}"

