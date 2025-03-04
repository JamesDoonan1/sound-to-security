import os
import librosa
from hash_password_generator import extract_features, create_hash
from symmetric_key_generation import derive_key_from_hash
from encrypt_decrypt_password import decrypt_password
from database_control import get_encrypted_password

def authenticate_with_audio(file_path, entered_password):
    """Verifies if an audio file matches a stored password."""
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
            print(f"Stored password: {stored_password}")

            if entered_password == stored_password:
                print("Login Successful!")
                return True
            else:
                print("Incorrect Password.")
                return False
        else:
            print("No password found for this audio.")
            return False

    except Exception as e:
        print(f"Error during login: {e}")
        return False
