import librosa
import numpy as np
import os
from vocal_passwords.feature_extraction import extract_audio_features
from models.claude_password_generator import generate_password_with_claude

# File paths
PASSPHRASE_FILE = "stored_passphrase.txt"
VOICEPRINT_FILE = "stored_voiceprint.npy"

def process_audio_and_generate_password(audio_path):
    """Process an audio file and generate a secure password."""
    audio, sr = librosa.load(audio_path, sr=22050)
    features = extract_audio_features(audio, sr)
    password = generate_password_with_claude(features)
    return password

def extract_passphrase():
    """Retrieve the stored passphrase."""
    if os.path.exists(PASSPHRASE_FILE):
        with open(PASSPHRASE_FILE, "r") as f:
            passphrase = f.read().strip()
            print(f"✅ Passphrase successfully loaded: {passphrase}")  # ✅ Debugging
            return passphrase
    print("❌ Passphrase file missing!")  # 🚨 Debugging
    return None

def extract_voice_features():
    """Retrieve the stored voiceprint (features)."""
    if os.path.exists(VOICEPRINT_FILE):
        voiceprint = np.load(VOICEPRINT_FILE).astype(np.float32)
        print(f"✅ Voiceprint successfully loaded: {voiceprint}")  # ✅ Debugging
        return voiceprint
    print("❌ Voiceprint file missing!")  # 🚨 Debugging
    return None
