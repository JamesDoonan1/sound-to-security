import os
import json
import librosa
import numpy as np

from hash_password_generator import extract_features, create_hash
from ai_password_generator import AIPasswordGenerator
from symmetric_key_generation import derive_key_from_hash
from encrypt_decrypt_password import encrypt_password, decrypt_password
from database_control import initialize_db, store_encrypted_password, get_encrypted_password

AUDIO_FOLDER_PATH = "/media/sf_VM_Shared_Folder/Audio Files"
OUTPUT_JSON_FILE = "audio_data.json"

# A global list to store data for JSON
audio_data_list = []

def print_feature_summary(features):
    """
    Prints a statistical summary of extracted features.
    """
    print("\nFeature Summary:\n")
    for key, value in features.items():
        if isinstance(value, np.ndarray) and value.size > 0:
            stats = {
                "mean": np.mean(value),
                "max": np.max(value),
                "min": np.min(value),
                "std": np.std(value)
            }
            print(f"{key}: mean={stats['mean']:.4f}, max={stats['max']:.4f}, "
                  f"min={stats['min']:.4f}, std={stats['std']:.4f}")
        else:
            print(f"{key}: No data or invalid feature array.")

def summarize_array(arr: np.ndarray) -> dict:
    """
    Takes a NumPy array and returns a dictionary of summary stats.
    """
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max())
    }

def process_audio_file(file_name, y, sr, password_gen):
    """
    Handles password generation, encryption, and database storage for an audio file.
    Also collects summarized data for JSON output.
    """
    try:
        # 1) Extract features (full arrays)
        features = extract_features(y, sr)
        if not features:
            print(f"Failed to extract features for {file_name}.")
            return

        # 2) Print feature summary (existing logic)
        print_feature_summary(features)

        # 3) Generate hash
        audio_hash = create_hash(features)
        print(f"\nGenerated Hash: {audio_hash}\n")

        # 4) Derive key from hash
        key = derive_key_from_hash(audio_hash)

        # 5) Check if password already exists in database
        encrypted_pw = get_encrypted_password(audio_hash)
        if encrypted_pw:
            # Retrieve and decrypt stored password
            password = decrypt_password(encrypted_pw, key)
            print(f"Retrieved Stored Password: {password}")
        else:
            # Generate new password
            password = password_gen.generate_password(features)
            if password:
                print(f"Generated Thematic Password (new): {password}")
                encrypted_pw = encrypt_password(password, key)
                store_encrypted_password(audio_hash, encrypted_pw)
                print("Password encrypted and stored in database.")
            else:
                print("Failed to generate password.")
                password = None

        # NEW: Summarize each feature array instead of storing the entire array
        summarized_features = {}
        for k, v in features.items():
            if isinstance(v, np.ndarray) and v.size > 0:
                summarized_features[k] = summarize_array(v)
            else:
                summarized_features[k] = None

        # Build a record to store in our global list
        audio_entry = {
            "file_name": file_name,
            "sample_rate": sr,
            "features": summarized_features,  # Only summary stats
            "hash": audio_hash,
            "password": password  # Optional: store the generated password
        }

        # Append to the global list
        audio_data_list.append(audio_entry)

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

if __name__ == "__main__":
    if not os.path.exists(AUDIO_FOLDER_PATH):
        print(f"The folder {AUDIO_FOLDER_PATH} does not exist.")
        exit()

    initialize_db()
    password_gen = AIPasswordGenerator()

    # Loop over each .mp3 file in one pass
    for file_name in os.listdir(AUDIO_FOLDER_PATH):
        if not file_name.endswith(".mp3"):
            continue

        file_path = os.path.join(AUDIO_FOLDER_PATH, file_name)
        print(f"\nProcessing file: {file_name}")

        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=None)
            print(f"Loaded: {len(y)} samples, Sample Rate: {sr}")

            # Process the audio file (extract features, generate password, etc.)
            process_audio_file(file_name, y, sr, password_gen)

        except Exception as e:
            print(f"Failed to process the file: {e}")

        print("-" * 50)

    print("Processing completed.")

    # Write the entire list to JSON (only summary stats)
    if audio_data_list:
        with open(OUTPUT_JSON_FILE, "w") as f:
            json.dump(audio_data_list, f, indent=4)
        print(f"\nSaved {len(audio_data_list)} entries to '{OUTPUT_JSON_FILE}'.")
    else:
        print("No features extracted; nothing to save.")
