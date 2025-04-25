import os
import librosa
import base64
from audio_passwords.hash_password_generator import extract_features, create_hash
from audio_passwords.ai_password_generator import AIPasswordGenerator
from audio_passwords.symmetric_key_generation import derive_key, new_salt
from audio_passwords.encrypt_decrypt_password import encrypt_password
from audio_passwords.database_control import get_encrypted_password_by_hash, store_encrypted_password

def create_password_from_audio(file_path, username):
    """
    Processes an audio file, generates a password, and stores it in the database
    with the associated username.
    
    Args:
        file_path: Path to the audio file
        username: Username to associate with this password
        
    Returns:
        str: A message indicating the result of the operation
    """
    try:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing file for password creation: {file_name} for user: {username}")
        
        if not os.path.exists(file_path):
            print(f"Error: File not found -> {file_path}")
            return "Error: File not found"
            
        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        features = extract_features(y, sr)
        
        if not features:
            print(f"Failed to extract features for {file_name}.")
            return "Error: Feature extraction failed"
            
        # Generate full hash from audio features
        audio_hash = create_hash(features)
        print(f"Generated Hash: {audio_hash}")
        
        # Check if a password already exists for this hash
        stored_username, b64_salt, encrypted_pw = get_encrypted_password_by_hash(audio_hash)
        
        if encrypted_pw and stored_username == username:
            # If the password exists for this user, retrieve it
            salt_bytes = base64.b64decode(b64_salt)
            key = derive_key(audio_hash, salt_bytes)
            try:
                stored_password = decrypt_password(encrypted_pw, key)
                print(f"Password already exists for user {username} with this audio file.")
                print(f"Stored AI-Generated Password: {stored_password}")
                return "Password already exists for this audio file."
            except Exception:
                # If decryption fails, treat it as if no password exists
                pass
        
        # Generate a fresh salt and derive key
        salt_bytes = new_salt()
        key = derive_key(audio_hash, salt_bytes)
        
        # Generate a new password
        password_gen = AIPasswordGenerator()
        password = password_gen.generate_password(features)
        
        if password:
            # Encrypt and store the new password
            encrypted_pw = encrypt_password(password, key)
            store_encrypted_password(
                username=username,
                audio_hash=audio_hash,
                salt=base64.b64encode(salt_bytes).decode("utf-8"),
                encrypted_password=encrypted_pw
            )
            print(f"Generated AI Password for user {username}: {password}")
            return "Password created successfully."
        else:
            print("Failed to generate password.")
            return "Error: Failed to generate password."
            
    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
        return f"Error: An issue occurred during processing: {str(e)}"