import librosa
import numpy as np
import os
import hashlib


def extract_features(y, sr):
    
    # Extracts features from an audio signal using Librosa.
    
    # 1. MFCCs (Mel-Frequency Cepstral Coefficients) - A common audio feature that summarizes frequency content.
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    # 2. Spectral Centroid - Indicates where the "center of mass" of the spectrum is located.
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)

    # 3. Spectral Contrast - Highlights the amplitude contrast in different frequency bands.
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

    # 4. Tempo and Beats - Extracts the tempo (in beats per minute) and the beat locations in the signal.
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # 5. Harmonic and Percussive Components - Splits the audio into harmonic (melodic) and percussive (rhythmic) components.
    harmonic, percussive = librosa.effects.hpss(y)

    # 6. Zero-Crossing Rate - Measures how often the signal crosses zero, commonly used for percussive sounds or noise.
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)

    # 7. Chroma Features (CENS) - Represents the pitch class (e.g., C, D, E, etc.) content over time.
    chroma_cens = librosa.feature.chroma_cens(y=y, sr=sr)

    # Return all extracted features as a dictionary. The values are flattened to 1D arrays to simplify processing.
    return {
        "MFCCs": mfccs.flatten(),
        "Spectral Centroid": spectral_centroid.flatten(),
        "Spectral Contrast": spectral_contrast.flatten(),
        "Tempo": np.array([tempo]).flatten(),  # Flatten Tempo into a 1D array
        "Beats": beats.flatten(),  # Flatten Beats array
        "Harmonic Components": harmonic.flatten(),
        "Percussive Components": percussive.flatten(),
        "Zero-Crossing Rate": zero_crossing_rate.flatten(),
        "Chroma Features (CENS)": chroma_cens.flatten(),
    }


def create_hash(features):
    
    