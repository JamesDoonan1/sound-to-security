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
    Extracts features, generates hash & password, stores summarized features + hash + password in JSON.
    """
    try:
        # 1) Extract full features
        features = extract_features(y, sr)
        if not features:
            print(f"Failed to extract features for {file_name}.")
            return

        # 2) Generate hash
        audio_hash = create_hash(features)

        # 3) Derive key
        key = derive_key_from_hash(audio_hash)

        # 4) Check if there's an existing password in DB
        encrypted_pw = get_encrypted_password(audio_hash)
        if encrypted_pw:
            # Retrieve stored password
            password = decrypt_password(encrypted_pw, key)
            print(f"Retrieved Stored Password: {password}")
        else:
            # Generate new password
            password = password_gen.generate_password(features)
            if password:
                encrypted_pw = encrypt_password(password, key)
                store_encrypted_password(audio_hash, encrypted_pw)
                print(f"Generated Thematic Password (new): {password}")
            else:
                print("Failed to generate password.")
                password = None

        # 5) Summarize each feature array
        summarized_features = {}
        for k, v in features.items():
            if isinstance(v, np.ndarray) and v.size > 0:
                summarized_features[k] = summarize_array(v)
            else:
                summarized_features[k] = None

        # 6) Build a record with only the needed info
        audio_entry = {
            "features": summarized_features,  # Summaries only
            "hash": audio_hash,
            "password": password  # If you want the model to learn to produce both
        }

        audio_data_list.append(audio_entry)

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

if __name__ == "__main__":
    if not os.path.exists(AUDIO_FOLDER_PATH):
        print(f"The folder {AUDIO_FOLDER_PATH} does not exist.")
        exit()

    initialize_db()
    password_gen = AIPasswordGenerator()

    # Loop once over each .mp3 file
    for file_name in os.listdir(AUDIO_FOLDER_PATH):
        if not file_name.endswith(".mp3"):
            continue

        file_path = os.path.join(AUDIO_FOLDER_PATH, file_name)
        print(f"\nProcessing file: {file_name}")

        try:
            y, sr = librosa.load(file_path, sr=None)
            process_audio_file(file_name, y, sr, password_gen)
        except Exception as e:
            print(f"Failed to process {file_name}: {e}")

        print("-" * 50)

    print("Processing completed.")

    # Write the final dataset to JSON
    if audio_data_list:
        with open(OUTPUT_JSON_FILE, "w") as f:
            json.dump(audio_data_list, f, indent=4)
        print(f"\nSaved {len(audio_data_list)} entries to '{OUTPUT_JSON_FILE}'.")
    else:
        print("No features extracted; nothing to save.")
