import os
import librosa
from audio_passwords.hash_password_generator import extract_features, create_hash
from audio_passwords.ai_password_generator import AIPasswordGenerator
from audio_passwords.symmetric_key_generation import derive_key_from_hash
from audio_passwords.database_control import initialize_db, store_encrypted_password, get_encrypted_password
from audio_passwords.encrypt_decrypt_password import encrypt_password, decrypt_password

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
            return "Error: File not found"

        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        features = extract_features(y, sr)

        if not features:
            print(f"Failed to extract features for {file_name}.")
            return "Error: Feature extraction failed"

        # Generate hash
        audio_hash = create_hash(features)
        print(f"Generated Hash: {audio_hash}")  # Output hash to terminal

        # Derive key
        key = derive_key_from_hash(audio_hash)

        # Check if password already exists
        encrypted_pw = get_encrypted_password(audio_hash)
        if encrypted_pw:
            print("Password already exists for this audio file.")
            stored_password = decrypt_password(encrypted_pw, key)
            print(f"Stored AI-Generated Password: {stored_password}")  # Output AI password to terminal
            return "Password already exists for this audio file."
        else:
            password = password_gen.generate_password(features)
            if password:
                encrypted_pw = encrypt_password(password, key)
                store_encrypted_password(audio_hash, encrypted_pw)
                print(f"Generated AI Password: {password}")  # Output AI password to terminal
                return "Password created successfully."
            else:
                print("Failed to generate password.")
                return "Error: Failed to generate password."

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
        return "Error: An issue occurred during processing."
