import librosa
import numpy as np

def extract_rhythm_features(audio, sr):
    """Extract tempo (beats per minute) from the audio."""
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    tempo = float(tempo)  # Ensure tempo is scalar
    print("  - Tempo (BPM): {:.2f}".format(tempo))
    return tempo

def extract_audio_features(audio, sr):
    print("Step 2: Audio captured successfully. Proceeding to feature extraction...")
    
    # Check if audio is too short
    if len(audio) < 512:
        raise ValueError("Audio is too short for feature extraction.")

    # Extract MFCC features
    print("  Sub-step 2.1: Extracting MFCC features...")
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=512)
    mfcc_mean = np.mean(mfcc, axis=1)
    print(f"    - MFCC mean values: {mfcc_mean}")

    # Extract Spectral Centroid
    print("  Sub-step 2.2: Extracting spectral centroid...")
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr, n_fft=512)
    spectral_centroid_mean = np.mean(spectral_centroid)
    print(f"    - Spectral centroid mean: {spectral_centroid_mean}")

    # Extract Tempo
    print("  Sub-step 2.3: Extracting rhythm features (tempo)...")
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    tempo = float(tempo)  # Ensure tempo is a scalar value
    print(f"    - Tempo (BPM): {tempo:.2f}")

    # Combine features into a string
    features = f"{mfcc_mean[:5].mean():.2f},{spectral_centroid_mean:.2f},{tempo:.2f}"
    print(f"  - Combined features string: {features}")
    return features
