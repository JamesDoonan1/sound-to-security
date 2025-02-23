import os
import numpy as np
import librosa
from vocal_passwords.feature_extraction import extract_audio_features
from models.claude_password_generator import generate_password_with_claude
from backend.utils.password_comparator import compare_passwords
from backend.utils.password_comparator import calculate_entropy, brute_force_complexity
import string
import random

# 📌 Get absolute paths dynamically
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # This is `backend/services/`
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))  # Moves up to `sound-to-security/`

# ✅ Correct file paths for passphrase and voiceprint
PASSPHRASE_FILE = os.path.join(ROOT_DIR, "stored_passphrase.txt")
VOICEPRINT_FILE = os.path.join(ROOT_DIR, "stored_voiceprint.npy")
### ✅ PASSWORD GENERATION FUNCTION

def generate_traditional_password(length=5):
    """Generate a traditional password with a given length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

### ✅ PASSWORD GENERATION FUNCTION
def process_audio_and_generate_password(audio_path):
    """Process an audio file and generate a secure password, then compare it with traditional passwords."""
    audio, sr = librosa.load(audio_path, sr=22050)
    features = extract_audio_features(audio, sr)

    # ✅ Generate AI Password (Claude or Fallback Traditional)
    ai_password = generate_password_with_claude(features) or generate_traditional_password()

    # ✅ Generate Traditional Passwords (10 variations)
    traditional_passwords = [generate_traditional_password() for _ in range(10)]

    # ✅ Compare Passwords
    comparison_results = [{"Type": "AI-Generated", "Password": ai_password, "Entropy": calculate_entropy(ai_password), "Brute-Force Time (s)": brute_force_complexity(ai_password)}]

    for pwd in traditional_passwords:
        comparison_results.append({"Type": "Traditional", "Password": pwd, "Entropy": calculate_entropy(pwd), "Brute-Force Time (s)": brute_force_complexity(pwd)})

    # ✅ Return Traditional Passwords alongside AI password results
    return {
        "ai_password": ai_password,
        "traditional_passwords": traditional_passwords,
        "comparison": comparison_results
    }

    


### ✅ PASS-PHRASE FUNCTIONS
def extract_passphrase():
    """Retrieve the stored passphrase from the correct location."""
    if os.path.exists(PASSPHRASE_FILE):
        with open(PASSPHRASE_FILE, "r") as f:
            passphrase = f.read().strip()
            print(f"🛠 DEBUG: Extracted Passphrase → {passphrase}")  # ✅ Should print: "Georgie Porgie"
            return passphrase
    print("❌ ERROR: Passphrase file missing!")
    return None  # 🔥 Fix: Don't return "UNKNOWN_PASSPHRASE", just return `None`.

def save_passphrase(passphrase):
    """Save passphrase to the correct file."""
    with open(PASSPHRASE_FILE, "w") as f:
        f.write(passphrase)
    print(f"✅ Passphrase saved successfully at {PASSPHRASE_FILE}")

### ✅ VOICEPRINT FUNCTIONS
def extract_voice_features():
    """Retrieve stored voice features from the correct location."""
    if os.path.exists(VOICEPRINT_FILE):
        voiceprint = np.load(VOICEPRINT_FILE).astype(np.float32)
        print(f"🛠 DEBUG: Extracted Voice Features → {voiceprint}")  # ✅ Should print actual values
        return {
            "mfcc": float(voiceprint[0]),
            "spectral_centroid": float(voiceprint[1]),
            "tempo": float(voiceprint[2])
        }
    print("❌ ERROR: Voiceprint file missing!")
    return None  # 🔥 Fix: Don't return fake values like `-999.0`, just return `None`.

def save_voiceprint(voice_features):
    """Save extracted voice features."""
    np.save(VOICEPRINT_FILE, np.array(voice_features, dtype=np.float32))
    print(f"✅ Voiceprint saved successfully at {VOICEPRINT_FILE}")
