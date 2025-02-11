import os
import numpy as np
import librosa
from vocal_passwords.feature_extraction import extract_audio_features
from models.claude_password_generator import generate_password_with_claude

# 📌 Get absolute paths dynamically
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # This is `backend/services/`
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))  # Moves up to `sound-to-security/`

# ✅ Correct file paths for passphrase and voiceprint
PASSPHRASE_FILE = os.path.join(ROOT_DIR, "stored_passphrase.txt")
VOICEPRINT_FILE = os.path.join(ROOT_DIR, "stored_voiceprint.npy")

### ✅ PASSWORD GENERATION FUNCTION
def process_audio_and_generate_password(audio_path):
    """Process an audio file and generate a secure password."""
    audio, sr = librosa.load(audio_path, sr=22050)
    features = extract_audio_features(audio, sr)
    password = generate_password_with_claude(features)
    return password

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
