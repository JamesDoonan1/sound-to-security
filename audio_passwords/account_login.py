import os
import librosa
from audio_passwords.hash_password_generator import extract_features, create_hash
from audio_passwords.symmetric_key_generation import derive_key_from_hash
from audio_passwords.encrypt_decrypt_password import decrypt_password
from audio_passwords.database_control import get_encrypted_password

def authenticate_with_audio(file_path):
    """Verifies if an audio file matches a stored password (No manual password entry)."""
    try:
        file_name = os.path.basename(file_path)
        print(f"\nAttempting login with file: {file_name}")

        if not os.path.exists(file_path):
            print(f"Error: File not found -> {file_path}")
            return False

        # Load audio and extract features
        y, sr = librosa.load(file_path, sr=None)
        features = extract_features(y, sr)

        if not features:
            print("Failed to extract features for login.")
            return False

        # Generate hash and derive key
        audio_hash = create_hash(features)
        key = derive_key_from_hash(audio_hash)

        # Retrieve stored password
        encrypted_pw = get_encrypted_password(audio_hash)
        if encrypted_pw:
            stored_password = decrypt_password(encrypted_pw, key)
            print(f"Retrieved stored password: {stored_password}")  # Debugging Output

            print("Login Successful!")  # Automatic login without manual password entry
            return True
        else:
            print("No password found for this audio. Login failed.")
            return False

    except Exception as e:
        print(f"Error during login: {e}")
        return False
