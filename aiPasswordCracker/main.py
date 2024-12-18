import os
import librosa
from audio_feature_extraction import extract_features, create_hash
from ai_password_generator import AIPasswordGenerator
from key_derivation import derive_key_from_hash
from encryption_utils import encrypt_password, decrypt_password
from database_utils import initialize_db, store_encrypted_password, get_encrypted_password
import numpy as np

AUDIO_FOLDER_PATH = "/media/sf_VM_Shared_Folder/Audio Files"

if not os.path.exists(AUDIO_FOLDER_PATH):
    print(f"The folder {AUDIO_FOLDER_PATH} does not exist.")
    exit()

# Initialize the database
initialize_db()

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
        print(f"\nGenerated Hash: {audio_hash}")

        # Derive key from hash
        key = derive_key_from_hash(audio_hash)

        # Check if an encrypted password exists in the DB for this hash
        encrypted_pw = get_encrypted_password(audio_hash)
        if encrypted_pw:
            # Decrypt the existing password
            password = decrypt_password(encrypted_pw, key)
            print(f"Retrieved Stored Password: {password}")
        else:
            # Generate a new AI password
            password = password_gen.generate_password(features)
            if password:
                print(f"Generated Thematic Password (new): {password}")
                # Encrypt and store it
                encrypted_pw = encrypt_password(password, key)
                store_encrypted_password(audio_hash, encrypted_pw)
            else:
                print("Failed to generate password.")

    except Exception as e:
        print(f"Failed to process the file: {e}")

    print("-" * 50)

print("Processing completed.")
