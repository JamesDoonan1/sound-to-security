import librosa
import numpy as np

def extract_rhythm_features(audio, sr):
    """Extract tempo (beats per minute) from the audio."""
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    return float(tempo)  # Ensure tempo is scalar

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
    return features
