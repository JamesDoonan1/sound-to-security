import numpy as np
import os
import csv
import speech_recognition as sr


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/data"))

# File paths for stored data
VOICEPRINT_FILE = "stored_voiceprint.npy"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
PASSPHRASE_FILE = os.path.join(DATA_DIR, "stored_passphrase.txt")

### 🛠 VOICEPRINT STORAGE & VERIFICATION ###
def save_voiceprint(voice_features):
    """Saves extracted voice features for authentication."""
    try:
        np.save(VOICEPRINT_FILE, np.array(voice_features, dtype=np.float32))
        print(f" Voiceprint saved successfully to {VOICEPRINT_FILE}")
    except Exception as e:
        print(f" ERROR: Could not save voiceprint: {e}")

def load_voiceprint():
    """Loads the stored voiceprint if it exists."""
    if os.path.exists(VOICEPRINT_FILE):
        return np.load(VOICEPRINT_FILE).astype(np.float32)  #  Ensure it's float
    return None

def verify_voice(new_voice_features, threshold=50):
    """Compares new voice with stored voiceprint."""
    stored_voiceprint = load_voiceprint()
    
    if stored_voiceprint is None:
        print(" No stored voiceprint found. Please generate a password first.")
        return False

    new_voice_features = np.array(new_voice_features, dtype=np.float32)

    #  Compute similarity (Euclidean distance)
    similarity = np.linalg.norm(stored_voiceprint - new_voice_features)
    print(f"🔍 Voice similarity score: {similarity}")

    #  Dynamically adjust threshold based on stored voiceprint length
    dynamic_threshold = np.linalg.norm(stored_voiceprint) * 0.2  # 20% variation allowed
    final_threshold = max(threshold, dynamic_threshold)  # Use max of default or dynamic

    return similarity < final_threshold  #  Pass if within similarity threshold


### 🛠 PASSPHRASE STORAGE & VERIFICATION ###
def save_passphrase(passphrase):
    """Stores the user's spoken passphrase."""
    try:
        with open(PASSPHRASE_FILE, "w") as f:
            f.write(passphrase)
        print(f" Passphrase saved successfully: {passphrase}")
    except Exception as e:
        print(f" ERROR: Could not save passphrase: {e}")

def load_passphrase():
    """Loads the stored passphrase if it exists."""
    if os.path.exists(PASSPHRASE_FILE):
        with open(PASSPHRASE_FILE, "r") as f:
            return f.read().strip()
    return "NO_PASSPHRASE"  #  Instead of returning None, return a default value

def verify_passphrase(spoken_passphrase):
    """Compares the spoken phrase to the stored passphrase."""
    stored_passphrase = load_passphrase()
    
    if stored_passphrase is None:
        print(" No stored passphrase found. Please generate a password first.")
        return False

    return stored_passphrase.lower() == spoken_passphrase.lower()


### 🛠 SPEECH TO TEXT (FOR PASSPHRASE AUTHENTICATION) ###
def recognize_speech(audio_path):
    """Converts recorded speech to text using SpeechRecognition."""
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)  #  Using Google Speech-to-Text API
        print(f" Recognized phrase: {text}")
        return text
    except sr.UnknownValueError:
        print(" Could not understand audio.")
        return "UNKNOWN_PHRASE"  #  Instead of returning None, return a default value
    except sr.RequestError:
        print(" Error with speech recognition API.")
        return "ERROR"

