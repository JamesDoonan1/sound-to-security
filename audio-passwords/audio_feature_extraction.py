import librosa
import numpy as np

def extract_features(y, sr):
    """
    Extracts features from an audio signal using Librosa.

    Args:
        y (numpy.ndarray): The audio time series.
        sr (int): The sample rate of the audio.

    Returns:
        dict: A dictionary containing extracted audio features.
    """
    try:
        # Extract MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Extract Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        
        # Extract Spectral Contrast
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        
        # Extract Tempo and Beats
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Harmonic and Percussive Components
        harmonic, percussive = librosa.effects.hpss(y)
        
        # Zero-Crossing Rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        # Chroma Features
        chroma_cens = librosa.feature.chroma_cens(y=y, sr=sr)

        # Return a dictionary of features
        return {
            "MFCCs": mfccs.flatten(),
            "Spectral Centroid": spectral_centroid.flatten(),
            "Spectral Contrast": spectral_contrast.flatten(),
            "Tempo": np.array([tempo]).flatten(),
            "Beats": beats.flatten(),
            "Harmonic Components": harmonic.flatten(),
            "Percussive Components": percussive.flatten(),
            "Zero-Crossing Rate": zero_crossing_rate.flatten(),
            "Chroma Features (CENS)": chroma_cens.flatten(),
        }
    except Exception as e:
        print(f"Error extracting features: {e}")
        return None
