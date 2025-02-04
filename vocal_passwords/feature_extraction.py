import librosa
import numpy as np

def extract_rhythm_features(audio, sr):
    """Extracts tempo (beats per minute) from the audio."""
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)

    if isinstance(tempo, np.ndarray):  # Ensure tempo is a scalar
        tempo = float(tempo[0]) if len(tempo) > 0 else 0.0

    print(f"  - Tempo (BPM): {tempo:.2f}")  # ✅ Now it's a single number
    return tempo

def extract_audio_features(audio, sr):
    """Extracts vocal features from the recorded audio for password generation."""
    print("🔍 Extracting vocal features...")

    # Check if audio is too short
    if len(audio) < 512:
        raise ValueError("Audio is too short for feature extraction.")

    # Extract MFCC features
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=512)
    mfcc_mean = np.mean(mfcc, axis=1)

    # Extract Spectral Centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=512)
    spectral_centroid_mean = np.mean(spectral_centroid)

    # Extract Tempo
    tempo = extract_rhythm_features(audio, sr)

    # Combine features into a string
    features = f"{mfcc_mean[:5].mean():.2f},{spectral_centroid_mean:.2f},{tempo:.2f}"
    print(f"🎤 Extracted Features: {features}")

    return features
