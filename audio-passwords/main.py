import os
import librosa
import numpy as np
import tkinter as tk
from tkinter import filedialog
from hash_password_generator import extract_features, create_hash
from ai_password_generator import AIPasswordGenerator
from symmetric_key_generation import derive_key_from_hash
from encrypt_decrypt_password import encrypt_password, decrypt_password
from database_control import initialize_db, store_encrypted_password, get_encrypted_password

# Initialize database
initialize_db()
password_gen = AIPasswordGenerator()

def process_audio_file(file_path):
    """Processes an audio file, generates a password, and stores it in the database."""
    try:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing file: {file_name}")

        # Ensure the file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found -> {file_path}")
            return

        # Try loading with librosa
        try:
            y, sr = librosa.load(file_path, sr=None)
        except Exception as e:
            print(f"Librosa failed to load file: {e}")
            return
        
        # Extract features
        features = extract_features(y, sr)
        if not features:
            print(f"Failed to extract features for {file_name}.")
            return

        print(f"Extracted features for {file_name} successfully.")

        # Generate hash
        audio_hash = create_hash(features)
        print(f"Generated Hash: {audio_hash}")

        # Derive key
        key = derive_key_from_hash(audio_hash)

        # Check if there's an existing password in DB
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

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")


def choose_audio_file():
    """Opens a file dialog to select an audio file for processing."""
    file_path = filedialog.askopenfilename(
        initialdir="/home/cormacgeraghty/Desktop",  # Force it to open in Desktop
        filetypes=[("All Files", "*.*")]
    )
    print(f"Selected file: {file_path}")  # Debugging step
    if file_path:
        process_audio_file(file_path)

# GUI for file selection
app = tk.Tk()
app.title("Choose Audio File for Processing")
app.geometry("400x200")

tk.Label(app, text="Select an audio file to generate a password", font=("Helvetica", 12)).pack(pady=20)
tk.Button(app, text="Choose File", command=choose_audio_file).pack(pady=10)

app.mainloop()
