import subprocess
import os

# Dynamic path detection to make it more portable
def find_hashcat_path():
    """Try to locate hashcat executable in common locations"""
    possible_paths = [
        # Windows paths
        r"C:\Program Files\hashcat\hashcat.exe",
        r"C:\Program Files (x86)\hashcat\hashcat.exe",
        r"C:\hashcat\hashcat.exe",
        r"C:\Users\James Doonan\Downloads\hashcat-6.2.6\hashcat-6.2.6\hashcat.exe",
        # Linux/Mac paths
        "/usr/bin/hashcat",
        "/usr/local/bin/hashcat",
        # Add more potential paths here
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found Hashcat at: {path}")
            return path
    
    # If we can't find it, return the original path as fallback
    default_path = r"C:\Users\James Doonan\Downloads\hashcat-6.2.6\hashcat-6.2.6\hashcat.exe"
    print(f"⚠️ Hashcat not found in common locations. Using default: {default_path}")
    return default_path

# Updated path settings
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/data"))
HASHCAT_PATH = find_hashcat_path()
HASH_FILE = os.path.join(DATA_DIR, "hashed_password.txt")  # Using your existing hashed_password.txt file
TEMP_HASH_FILE = os.path.join(DATA_DIR, "temp_hash_for_hashcat.txt")
WORDLIST_FILE = os.path.join(DATA_DIR, "rockyou.txt")

def save_hash(password_hash):
    """Saves the given hash to a temporary file for Hashcat processing."""
    # Ensure the DATA_DIR exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Save to a temporary file so we don't overwrite the existing password file
    with open(TEMP_HASH_FILE, "w") as f:
        f.write(password_hash + "\n")
    print(f"✅ Hash saved to: {TEMP_HASH_FILE}")
    return TEMP_HASH_FILE

def crack_password_with_hashcat(hash_type="0", attack_mode="3", password_hash=None):
    """
    Runs Hashcat to attempt cracking the password.
    
    - hash_type: Hashcat mode for hashing algorithm (default: 0 for MD5).
    - attack_mode: Attack type (default: 3 for brute-force, 0 for dictionary attack).
    - password_hash: Optional specific hash to test (if not using the saved file)
    
    Returns:
        - Crack status (bool)
        - Cracked password (str) or None if unsuccessful.
    """
    
    # If a specific hash is provided, save it first
    hash_file_to_use = TEMP_HASH_FILE
    if password_hash:
        hash_file_to_use = save_hash(password_hash)
    elif not os.path.exists(TEMP_HASH_FILE):
        # If no specific hash provided and temp file doesn't exist, create it
        return False, "❌ No hash provided and no temp hash file found!"

    if not os.path.exists(HASHCAT_PATH):
        return False, f"❌ Hashcat executable not found at {HASHCAT_PATH}!"

    # Create wordlist file if it doesn't exist and using dictionary attack
    if attack_mode == "0" and not os.path.exists(WORDLIST_FILE):
        with open(WORDLIST_FILE, "w") as f:
            # Add some common passwords for testing
            f.write("password\n123456\nadmin\nwelcome\nqwerty\n12345678\nabc123\npassword1\n")
        print(f"✅ Created basic wordlist at: {WORDLIST_FILE}")

    # Hashcat command
    command = [
        HASHCAT_PATH,
        "--force",
        "-m", hash_type,  # Hash type (MD5, SHA256, etc.)
        "-a", attack_mode,  # Attack mode (3 = brute-force, 0 = dictionary)
        hash_file_to_use,
        "?a?a?a?a?a?a" if attack_mode == "3" else WORDLIST_FILE,  # Mask for brute-force, wordlist for dictionary
        "--show"  # Shows cracked passwords
    ]

    print(f"🔨 Running Hashcat command: {' '.join(command)}")

    try:
        # First, run without --show to crack the password
        crack_command = command[:-1]  # Remove --show for the actual cracking
        print(f"🔨 Running Hashcat crack: {' '.join(crack_command)}")
        
        # Set a timeout for the cracking process (30 seconds)
        crack_result = subprocess.run(
            crack_command, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        # Then check if password was cracked
        check_result = subprocess.run(command, capture_output=True, text=True)
        
        # Debugging output
        print(f"Hashcat STDOUT: {check_result.stdout}")
        print(f"Hashcat STDERR: {check_result.stderr}")
        
        # Check if password was cracked
        if check_result.returncode == 0 and check_result.stdout.strip():
            cracked_password = check_result.stdout.strip().split(":")[-1]  # Extract password
            return True, cracked_password
        else:
            return False, "❌ Password not cracked within the time limit or hash type not supported!"
    
    except subprocess.TimeoutExpired:
        return False, "⏱️ Hashcat cracking timed out (30s limit)"
    except Exception as e:
        return False, f"❌ Error running Hashcat: {str(e)}"
    finally:
        # Clean up temporary hash file
        if os.path.exists(TEMP_HASH_FILE):
            try:
                os.remove(TEMP_HASH_FILE)
                print(f"✅ Removed temporary hash file: {TEMP_HASH_FILE}")
            except:
                pass