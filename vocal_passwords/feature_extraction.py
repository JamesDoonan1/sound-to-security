import librosa
import numpy as np
import csv
import os

LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/logs"))  
FEATURE_LOG_FILE = os.path.join(LOGS_DIR, "voice_features_log.csv")
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/data"))

def log_voice_features(mfcc_mean, spectral_centroid_mean, tempo):
    """Logs extracted voice features to a CSV file."""
    os.makedirs(LOGS_DIR, exist_ok=True)  # ✅ Ensure `logs/` exists

    with open(FEATURE_LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not os.path.isfile(FEATURE_LOG_FILE):
            writer.writerow(["MFCC Mean", "Spectral Centroid", "Tempo (BPM)"])

        writer.writerow([mfcc_mean, spectral_centroid_mean, tempo])

def extract_rhythm_features(audio, sr):
    """Extract tempo (beats per minute) from the audio."""
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    return float(tempo)

def extract_audio_features(audio, sr):
    print("Step 2: Audio captured successfully. Proceeding to feature extraction...")

    # Extract MFCC features
    print("  Sub-step 2.1: Extracting MFCC features...")
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)

    # Extract Spectral Centroid
    print("  Sub-step 2.2: Extracting spectral centroid...")
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    spectral_centroid_mean = np.mean(spectral_centroid)

    # Extract Tempo
    print("  Sub-step 2.3: Extracting rhythm features (tempo)...")
    tempo = extract_rhythm_features(audio, sr)

    # ✅ Ensure features are numeric
    features = np.array([mfcc_mean[:5].mean(), spectral_centroid_mean, tempo], dtype=np.float32)
    print(f"  - Extracted Features (Numeric): {features}")

    # ✅ Log extracted features
    log_voice_features(features[0], features[1], features[2])

    return features
