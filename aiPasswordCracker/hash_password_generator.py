import librosa
import numpy as np
import os
import hashlib

def extract_features(y, sr):
    """
    Extracts features from an audio signal using Librosa.
    """
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    harmonic, percussive = librosa.effects.hpss(y)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
    chroma_cens = librosa.feature.chroma_cens(y=y, sr=sr)

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

def create_hash(features):
    """
    Creates a unique hash based on the extracted features.
    """
    concatenated_features = np.concatenate([value for value in features.values()])
    feature_bytes = concatenated_features.tobytes()
    audio_hash = hashlib.md5(feature_bytes).hexdigest()
    return audio_hash

if __name__ == "__main__":
    audio_folder_path = "/media/sf_VM_Shared_Folder/Audio Files"

    if not os.path.exists(audio_folder_path):
        print(f"The folder {audio_folder_path} does not exist.")
        exit()

    for file_name in os.listdir(audio_folder_path):
        if file_name.endswith(".mp3"):
            file_path = os.path.join(audio_folder_path, file_name)
            print(f"\nProcessing file: {file_name}")
            try:
                print(f"Loading with librosa: {file_path}")
                y, sr = librosa.load(file_path, sr=None)
                print(f"Librosa Loaded: {len(y)} samples, Sample Rate: {sr}")

                features = extract_features(y, sr)
                print("Extracted Features:")
                for key, value in features.items():
                    print(f"{key}: {value.shape if isinstance(value, np.ndarray) else len(value)}")

                audio_hash = create_hash(features)
                print(f"Generated Hash for {file_name}: {audio_hash}")
                print("Hash Explanation: The hash is created by concatenating all extracted features, "
                      "converting them into bytes, and then computing an MD5 hash.")
            except Exception as e:
                print(f"Failed to process the file with Librosa: {e}")

            print("-" * 50)

    print("Processing completed.")
