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
    
    #Creates a unique hash based on the extracted features.
    
    # Flatten and concatenate all feature arrays into one long 1D array
    concatenated_features = np.concatenate([value for value in features.values()])
    
    # Convert the concatenated array into bytes
    feature_bytes = concatenated_features.tobytes()
    
    # Use MD5 hashing to generate a hash based on the feature bytes
    hash_object = hashlib.md5(feature_bytes)
    audio_hash = hash_object.hexdigest()  # Get the hexadecimal representation of the hash
    
    return audio_hash


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
            y, sr = librosa.load(file_path, sr=None)  # Load audio file without resampling
            print(f"Librosa Loaded: {len(y)} samples, Sample Rate: {sr}")

            
            features = extract_features(y, sr)
            print("Extracted Features:")
            for key, value in features.items():
                print(f"{key}: {value.shape if isinstance(value, np.ndarray) else len(value)}")


            audio_hash = create_hash(features)
            print(f"Generated Hash for {file_name}: {audio_hash}")
            print("Hash Explanation: The hash is created by concatenating all extracted features, converting them into bytes, and then computing an MD5 hash. This ensures a unique identifier for the audio file based on its content.")

        except Exception as e:
            print(f"Failed to process the file with Librosa: {e}")

        print("-" * 50)

print("Processing completed.")
