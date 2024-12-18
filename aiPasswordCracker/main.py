import os
import librosa
from audio_feature_extraction import extract_features, create_hash
from ai_password_generator import AIPasswordGenerator
import numpy as np

# Set your audio folder path
AUDIO_FOLDER_PATH = "/media/sf_VM_Shared_Folder/Audio Files"

if not os.path.exists(AUDIO_FOLDER_PATH):
    print(f"The folder {AUDIO_FOLDER_PATH} does not exist.")
    exit()

password_gen = AIPasswordGenerator()

for file_name in os.listdir(AUDIO_FOLDER_PATH):
    if not file_name.endswith(".mp3"):
        continue

    file_path = os.path.join(AUDIO_FOLDER_PATH, file_name)
    print(f"\nProcessing file: {file_name}")

    try:
        # Load and process audio
        y, sr = librosa.load(file_path, sr=None)
        print(f"Loaded: {len(y)} samples, Sample Rate: {sr}")

        # Extract features and create hash
        features = extract_features(y, sr)
        
        # Print a summary of the features
        print("\nFeature Summary:")
        for key, value in features.items():
            if isinstance(value, np.ndarray) and value.size > 0:
                stats = {
                    "mean": np.mean(value),
                    "max": np.max(value),
                    "min": np.min(value),
                    "std": np.std(value)
                }
                print(f"{key}: mean={stats['mean']:.4f}, max={stats['max']:.4f}, min={stats['min']:.4f}, std={stats['std']:.4f}")
            else:
                print(f"{key}: No data or invalid feature array.")

        audio_hash = create_hash(features)

        # Print the hash for reference
        print(f"\nGenerated Hash: {audio_hash}")

        # Generate AI password (thematic password)
        password = password_gen.generate_password(features)
        if password:
            print(f"Generated Thematic Password: {password}")
        else:
            print("Failed to generate password.")

    except Exception as e:
        print(f"Failed to process the file with Librosa: {e}")

    print("-" * 50)

print("Processing completed.")
