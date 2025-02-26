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
OUTPUT_JSON_FILE = "/home/cormacgeraghty/Desktop/Project Code/audio_data.json"

print(f"JSON file being used: {os.path.abspath(OUTPUT_JSON_FILE)}")


# Load existing JSON data to count processed files
if os.path.exists(OUTPUT_JSON_FILE):
    try:
        with open(OUTPUT_JSON_FILE, "r") as f:
            raw_json = f.read().strip()  # Read raw JSON data and remove any whitespace
            
            # Debugging: Show the file's actual content
            # print(f"Raw JSON content: {raw_json}") 
            
            if raw_json:  # If the file is not empty
                audio_data_list = json.loads(raw_json)
            else:
                audio_data_list = []  # Start fresh if the file is empty
            
        processed_count = len(audio_data_list)
        print(f"Found existing JSON with {processed_count} processed files.")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"JSON file is empty or corrupted: {e}. Starting fresh.")
        audio_data_list = []
        processed_count = 0
else:
    print("No JSON file found. Starting fresh.")
    audio_data_list = []
    processed_count = 0

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

def process_audio_file(file_name, y, sr, password_gen, file_count):
    """
    Extracts features, generates hash & password, stores summarized features + hash + password in JSON.
    """
    try:
        print(f"\n[{file_count}] Processing file: {file_name}")

        # 1) Extract full features
        features = extract_features(y, sr)
        if not features:
            print(f"Failed to extract features for {file_name}.")
            return

        print(f"Extracted features for {file_name} successfully.")

        # 2) Generate hash
        audio_hash = create_hash(features)
        print(f"Generated Hash: {audio_hash}")

        # 3) Derive key
        key = derive_key_from_hash(audio_hash)

        # 4) Check if there's an existing password in DB
        encrypted_pw = get_encrypted_password(audio_hash)
        if encrypted_pw:
            password = decrypt_password(encrypted_pw, key)
            print(f"Retrieved stored password: {password}")
        else:
            password = password_gen.generate_password(features)
            if password:
                encrypted_pw = encrypt_password(password, key)
                store_encrypted_password(audio_hash, encrypted_pw)
                print(f"Generated new password: {password}")
            else:
                print("Failed to generate password.")
                password = None

        # 5) Summarize each feature array
        summarized_features = {
            k: summarize_array(v) if isinstance(v, np.ndarray) and v.size > 0 else None
            for k, v in features.items()
        }

        # 6) Build a record with only the needed info
        audio_entry = {
            "features": summarized_features, 
            "hash": audio_hash,
            "password": password 
        }

        audio_data_list.append(audio_entry)

        # Debugging: Print before writing
        print(f"Current data list before saving: {json.dumps(audio_data_list, indent=4)}")

        # Save JSON immediately after each file
        with open(OUTPUT_JSON_FILE, "w") as f:
            json.dump(audio_data_list, f, indent=4)
            f.flush()  # Ensure data is written immediately
            os.fsync(f.fileno())  # Force the OS to write the file

        print(f"Updated JSON after processing {file_name}.")
        print(json.dumps(audio_entry, indent=4))

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

if __name__ == "__main__":
    if not os.path.exists(AUDIO_FOLDER_PATH):
        print(f"The folder {AUDIO_FOLDER_PATH} does not exist.")
        exit()

    initialize_db()
    password_gen = AIPasswordGenerator()

    file_list = sorted(os.listdir(AUDIO_FOLDER_PATH))  # Ensure consistent order
    file_count = 0  # Track processed file count

    print("\nStarting audio file processing...\n")

    for file_name in file_list:
        if not file_name.endswith(".mp3"):
            continue

        # Skip already processed files
        if file_count < processed_count:
            print(f"Skipping {file_name} (already processed).")
            file_count += 1
            continue

        file_path = os.path.join(AUDIO_FOLDER_PATH, file_name)
        print("=" * 60)  # Separator for readability

        try:
            y, sr = librosa.load(file_path, sr=None)
            process_audio_file(file_name, y, sr, password_gen, file_count + 1)  # Adjusted count
        except Exception as e:
            print(f"Failed to process {file_name}: {e}")

        file_count += 1  # Only increment after processing

    print("=" * 60)
    print(f"\nProcessing completed. Total new files processed: {file_count - processed_count}")
