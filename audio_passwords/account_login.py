import os
import librosa
import base64
from audio_passwords.hash_password_generator import extract_features, create_hash
from audio_passwords.symmetric_key_generation import derive_key
from audio_passwords.encrypt_decrypt_password import decrypt_password
from audio_passwords.database_control import get_encrypted_password_by_hash

def authenticate_with_audio(file_path, username):
    """
    Verifies if an audio file matches a stored password for the given username.
    
    Args:
        file_path: Path to the audio file
        username: Username to authenticate
    
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    try:
        file_name = os.path.basename(file_path)
        print(f"\nAttempting login with file: {file_name} for user: {username}")
        
        if not os.path.exists(file_path):
            print(f"Error: File not found -> {file_path}")
            return False
            
        # Load audio and extract features
        y, sr = librosa.load(file_path, sr=None)
        features = extract_features(y, sr)
        
        if not features:
            print("Failed to extract features for login.")
            return False
            
        # Generate hash from audio features
        audio_hash = create_hash(features)
        print(f"Generated Hash: {audio_hash}")
        
        # Get stored data using the hash
        stored_username, b64_salt, encrypted_pw = get_encrypted_password_by_hash(audio_hash)
        
        # Verify both the hash and username match
        if encrypted_pw and stored_username == username:
            # Decode the base64 salt
            salt_bytes = base64.b64decode(b64_salt)
            
            # Derive the key using the hash and stored salt
            key = derive_key(audio_hash, salt_bytes)
            
            # Decrypt the password
            try:
                stored_password = decrypt_password(encrypted_pw, key)
                print(f"Retrieved stored password for user {stored_username}")
                print("Login Successful!")
                return True
            except Exception as e:
                print(f"Decryption failed: {e}")
                return False
        else:
            print("No matching account found or username doesn't match.")
            return False
            
    except Exception as e:
        print(f"Error during login: {e}")
        return False