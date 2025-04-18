import os
import numpy as np
import librosa
from vocal_passwords.feature_extraction import extract_audio_features
from models.claude_password_generator import generate_password_with_claude
from backend.utils.password_comparator import compare_passwords
from backend.utils.password_comparator import calculate_entropy, brute_force_complexity
import string
import random
import csv
import time  


#  Get absolute paths dynamically
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # This is `backend/services/`
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))  # Moves up to `sound-to-security/`
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))  
ENTROPY_LOG_FILE = os.path.join(LOGS_DIR, "entropy_results_log.csv")

#  Correct file paths for passphrase and voiceprint
PASSPHRASE_FILE = os.path.join(DATA_DIR, "stored_passphrase.txt")
VOICEPRINT_FILE = os.path.join(ROOT_DIR, "stored_voiceprint.npy")
###  PASSWORD GENERATION FUNCTION

def generate_traditional_password(length=12):
    """Generate a traditional password with a given length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

###  PASSWORD GENERATION FUNCTION
def process_audio_and_generate_password(audio_path):
    """Process an audio file and generate a secure password, then compare it with traditional passwords."""
    audio, sr = librosa.load(audio_path, sr=22050)
    features = extract_audio_features(audio, sr)

    #  Generate AI Password
    ai_password = generate_password_with_claude(features) or generate_traditional_password()

    #  Generate Traditional Passwords (10 variations)
    traditional_passwords = [generate_traditional_password() for _ in range(10)]

    #  Compare Passwords (Entropy & Brute-Force Complexity)
    comparison_results = []

    #  AI Password Entropy Calculation
    ai_entropy = calculate_entropy(ai_password)
    ai_brute_time = brute_force_complexity(ai_password)
    comparison_results.append({
        "Type": "AI-Generated",
        "Password": ai_password,
        "Entropy": ai_entropy,
        "Brute-Force Time (s)": ai_brute_time
    })
    
    #  Traditional Passwords Entropy Calculation
    for pwd in traditional_passwords:
        entropy = calculate_entropy(pwd)
        brute_time = brute_force_complexity(pwd)
        comparison_results.append({
            "Type": "Traditional",
            "Password": pwd,
            "Entropy": entropy,
            "Brute-Force Time (s)": brute_time
        })
        
    #  Log entropy results in a separate file
    log_entropy_results(comparison_results)

    return {
        "ai_password": ai_password,
        "traditional_passwords": traditional_passwords,
        "comparison": comparison_results
    }

    
def log_entropy_results(results):
    """Logs entropy and brute-force complexity results to a separate file."""
    os.makedirs(LOGS_DIR, exist_ok=True)  # Ensures `logs/` exists
    log_file = os.path.join(LOGS_DIR, "entropy_results_log.csv")
    
    if not results or len(results) == 0:
        print(" ERROR: No entropy results to log!")
        return  # Exit early if there are no results

    print(f" Logging {len(results)} passwords to entropy log...")

    #  Convert results into a dictionary format like `log_test_results()`
    entropy_results = {
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "AI_Password": None,
        "AI_Entropy": None,
        "AI_Brute_Force_Time": None,
        "Traditional_Passwords": []
    }

    traditional_password_metrics = []

    for entry in results:
        if entry["Type"] == "AI-Generated":
            entropy_results["AI_Password"] = entry["Password"]
            entropy_results["AI_Entropy"] = entry["Entropy"]
            entropy_results["AI_Brute_Force_Time"] = entry["Brute-Force Time (s)"]
        else:
            traditional_password_metrics.append(
                f"{entry['Password']} (Entropy: {entry['Entropy']}, Time: {entry['Brute-Force Time (s)']}s)"
            )

    entropy_results["Traditional_Passwords"] = "; ".join(traditional_password_metrics)

   
    print(f" Final Entropy Results → {entropy_results}")

    try:
        file_exists = os.path.isfile(log_file)

        with open(log_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)

            #  Write headers only if file does not exist
            if not file_exists:
                writer.writerow(["Timestamp", "AI_Password", "AI_Entropy", "AI_Brute_Force_Time", "Traditional_Passwords"])

            writer.writerow([
                entropy_results["Timestamp"],
                entropy_results["AI_Password"],
                entropy_results["AI_Entropy"],
                entropy_results["AI_Brute_Force_Time"],
                entropy_results["Traditional_Passwords"]
            ])

        print(f" Entropy results logged in {log_file}")

    except Exception as e:
        print(f" Error logging entropy results: {e}")

###  PASS-PHRASE FUNCTIONS
def extract_passphrase():
    """Retrieve the stored passphrase from the correct location."""
    try:
        # Ensure the file exists
        if not os.path.exists(PASSPHRASE_FILE):
            print(f" ERROR: Passphrase file missing at: {PASSPHRASE_FILE}")
            return None

        # Read the passphrase
        with open(PASSPHRASE_FILE, "r") as f:
            passphrase = f.read().strip()
            if not passphrase:
                print(" ERROR: Passphrase file is empty!")
                return None
            print(f"🛠 DEBUG: Extracted Passphrase → {passphrase}")
            return passphrase
    except Exception as e:
        print(f" ERROR: Failed to read passphrase file: {e}")
        return None   

def save_passphrase(passphrase):
    """Save passphrase to the correct file."""
    with open(PASSPHRASE_FILE, "w") as f:
        f.write(passphrase)
    print(f" Passphrase saved successfully at {PASSPHRASE_FILE}")

###  VOICEPRINT FUNCTIONS
def extract_voice_features():
    """Retrieve stored voice features from the correct location."""
    if os.path.exists(VOICEPRINT_FILE):
        voiceprint = np.load(VOICEPRINT_FILE).astype(np.float32)
        print(f"🛠 DEBUG: Extracted Voice Features → {voiceprint}")  
        return {
            "mfcc": float(voiceprint[0]),
            "spectral_centroid": float(voiceprint[1]),
            "tempo": float(voiceprint[2])
        }
    print(" ERROR: Voiceprint file missing!")
    return None  

def save_voiceprint(voice_features):
    """Save extracted voice features."""
    np.save(VOICEPRINT_FILE, np.array(voice_features, dtype=np.float32))
    print(f" Voiceprint saved successfully at {VOICEPRINT_FILE}")
