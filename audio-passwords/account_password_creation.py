import os
import librosa
from hash_password_generator import extract_features, create_hash
from ai_password_generator import AIPasswordGenerator
from symmetric_key_generation import derive_key_from_hash
from encrypt_decrypt_password import encrypt_password
from database_control import initialize_db, store_encrypted_password, get_encrypted_password

# Initialize database
initialize_db()
password_gen = AIPasswordGenerator()

def create_password_from_audio(file_path):
    """Processes an audio file, generates a password, and stores it in the database."""
    try:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing file for password creation: {file_name}")

        if not os.path.exists(file_path):
            print(f"Error: File not found -> {file_path}")
            return

        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        features = extract_features(y, sr)

        if not features:
            print(f"Failed to extract features for {file_name}.")
            return

        audio_hash = create_hash(features)
        key = derive_key_from_hash(audio_hash)

        # Check if password already exists
        encrypted_pw = get_encrypted_password(audio_hash)
        if encrypted_pw:
            password = encrypted_pw
            print(f"Password already exists for this audio.")
        else:
            password = password_gen.generate_password(features)
            if password:
                encrypted_pw = encrypt_password(password, key)
                store_encrypted_password(audio_hash, encrypted_pw)
                print(f"Generated new password: {password}")
            else:
                print("Failed to generate password.")
                password = None

        return password

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
