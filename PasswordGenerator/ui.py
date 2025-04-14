import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys
import librosa
import numpy as np

from audio_feature_extraction import extract_features
from hash_password_generator import create_hash
from symmetric_key_generation import derive_key_from_hash
from encrypt_decrypt_password import encrypt_password, decrypt_password
from database_control import initialize_db, store_encrypted_password, get_encrypted_password
from ai_password_generator import AIPasswordGenerator

# --- Set up sys.path for correct folder resolution ---
# Current file: root/sound-to-security/PasswordGenerator/ui.py
current_dir = os.path.dirname(__file__)  
# The project folder ("sound-to-security") is one level up.
project_folder = os.path.abspath(os.path.join(current_dir, ".."))
if project_folder not in sys.path:
    sys.path.append(project_folder)

# Now import candidate generator from AI_Training
try:
    from AI_Training.test_fine_tuned_model import generate_candidate_password
except ImportError:
    print("Failed to import generate_candidate_password from AI_Training/test_fine_tuned_model.py")
    generate_candidate_password = None  # Candidate generator must be provided

def summarize_array(arr: np.ndarray) -> dict:
    """Returns a summary (mean, std, min, max) for a NumPy array."""
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max())
    }

def load_fine_tuned_model_id():
    """
    Loads the fine-tuned model ID from model_info_fold0.txt, which is located
    in the root directory. The root is the parent of the project folder.
    """
    # The root folder is one level above the project folder.
    root_folder = os.path.abspath(os.path.join(project_folder, ".."))
    model_info_path = os.path.join(root_folder, "model_info_fold0.txt")
    if not os.path.exists(model_info_path):
        print("Fine-tuned model ID file not found; using default model ID.")
        return "ft:gpt-4o-2024-08-06:personal::BM4R6u51"  # fallback value
    with open(model_info_path, "r") as f:
        model_id = f.read().strip()
    print(f"Loaded Fine-Tuned Model ID: {model_id}")
    return model_id

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Melody-Based Account Manager")
        self.geometry("600x500")
        self.configure(bg="#282c34")
        initialize_db()  # Initialize the database
        print("Database initialized.")
        self.create_main_menu()

    def create_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        print("Displaying Main Menu.")
        
        frame = tk.Frame(self, bg="#282c34")
        frame.pack(expand=True, fill="both")
        
        print("Main Menu: Welcome")
        tk.Label(frame,
                 text="Welcome",
                 font=("Helvetica", 18, "bold"),
                 fg="#61dafb",
                 bg="#282c34").pack(pady=20)
        
        tk.Button(frame,
                  text="Login",
                  font=("Helvetica", 14),
                  command=self.show_login,
                  bg="#61dafb", fg="#282c34").pack(pady=10)
        tk.Button(frame,
                  text="Create Account",
                  font=("Helvetica", 14),
                  command=self.show_create_account,
                  bg="#61dafb", fg="#282c34").pack(pady=10)
        tk.Button(frame,
                  text="Test Password Security",
                  font=("Helvetica", 14),
                  command=self.show_test_security,
                  bg="#61dafb", fg="#282c34").pack(pady=10)

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        print("Displaying Login Screen.")
        
        frame = tk.Frame(self, bg="#282c34")
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame,
                 text="Login",
                 font=("Helvetica", 18, "bold"),
                 fg="#61dafb", bg="#282c34").pack(pady=20)
        
        tk.Label(frame,
                 text="Username:",
                 font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=5)
        self.username_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.username_entry.pack(pady=5)
        
        tk.Button(frame,
                  text="Select Audio and Login",
                  font=("Helvetica", 14),
                  command=self.login_with_audio,
                  bg="#61dafb", fg="#282c34").pack(pady=20)
        tk.Button(frame,
                  text="Back",
                  font=("Helvetica", 12),
                  command=self.create_main_menu,
                  bg="gray", fg="white").pack(pady=10)
    
    def login_with_audio(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter your username.")
            return

        file_path = filedialog.askopenfilename(
            title="Select Your Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            print(f"\n[Login] User '{username}' selected audio file: {file_path}")
            y, sr = librosa.load(file_path, sr=None)
            y = np.squeeze(y)
            print("[Login] Audio loaded successfully.")
            
            features = extract_features(y, sr)
            if not features:
                messagebox.showerror("Error", "Failed to extract features from the audio file.")
                print("[Login] Feature extraction failed.")
                return
            print("[Login] Extracted features successfully.")
            
            audio_hash = create_hash(features)
            print(f"[Login] Generated Hash: {audio_hash}")
            key = derive_key_from_hash(audio_hash)
            print("[Login] Derived encryption key from hash.")
            
            stored_enc_pw = get_encrypted_password(username, audio_hash)
            if stored_enc_pw:
                decrypted_password = decrypt_password(stored_enc_pw, key)
                print(f"[Login] Retrieved stored password (hidden from UI).")
                messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            else:
                print("[Login] No matching record found for provided username and audio.")
                messagebox.showerror("Error", "No account found for the provided username and audio.\nPlease create an account first.")
        except Exception as e:
            print(f"[Login] Error: {str(e)}")
            messagebox.showerror("Error", f"Login failed: {str(e)}")

    def show_create_account(self):
        for widget in self.winfo_children():
            widget.destroy()
        print("Displaying Create Account Screen.")
        
        frame = tk.Frame(self, bg="#282c34")
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame,
                 text="Create Account",
                 font=("Helvetica", 18, "bold"),
                 fg="#61dafb", bg="#282c34").pack(pady=20)
        
        tk.Label(frame,
                 text="Choose a Username:",
                 font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=5)
        self.new_username_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.new_username_entry.pack(pady=5)
        
        tk.Button(frame,
                  text="Select Audio and Create Account",
                  font=("Helvetica", 14),
                  command=self.create_account_with_audio,
                  bg="#61dafb", fg="#282c34").pack(pady=20)
        tk.Button(frame,
                  text="Back",
                  font=("Helvetica", 12),
                  command=self.create_main_menu,
                  bg="gray", fg="white").pack(pady=10)
    
    def create_account_with_audio(self):
        username = self.new_username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Your Audio File for Account Creation",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            print(f"\n[Account Creation] Creating account for '{username}' using audio file: {file_path}")
            y, sr = librosa.load(file_path, sr=None)
            y = np.squeeze(y)
            print("[Account Creation] Audio loaded successfully.")
            
            features = extract_features(y, sr)
            if not features:
                messagebox.showerror("Error", "Failed to extract features from the audio file.")
                print("[Account Creation] Feature extraction failed.")
                return
            print("[Account Creation] Extracted features successfully.")
            
            audio_hash = create_hash(features)
            print(f"[Account Creation] Generated Hash: {audio_hash}")
            key = derive_key_from_hash(audio_hash)
            print("[Account Creation] Derived encryption key from hash.")
            
            stored_enc_pw = get_encrypted_password(username, audio_hash)
            if stored_enc_pw:
                print("[Account Creation] Account already exists for this username and audio.")
                messagebox.showerror("Error", "An account already exists for the provided username and audio.\nPlease login.")
                return
            
            password_gen = AIPasswordGenerator()
            password = password_gen.generate_password(features)
            if not password:
                messagebox.showerror("Error", "Failed to generate a secure password. Try again.")
                print("[Account Creation] AI-based password generation failed.")
                return
            
            enc_password = encrypt_password(password, key)
            store_encrypted_password(username, audio_hash, enc_password)
            print(f"[Account Creation] Generated new password: {password}")
            print(f"[Account Creation] Account created for '{username}'.")
            messagebox.showinfo("Account Created", f"Account created for {username}.")
            self.create_main_menu()
        except Exception as e:
            print(f"[Account Creation] Error: {str(e)}")
            messagebox.showerror("Error", f"Account creation failed: {str(e)}")
    
    def show_test_security(self):
        for widget in self.winfo_children():
            widget.destroy()
        print("Displaying Test Password Security Screen.")
        
        frame = tk.Frame(self, bg="#282c34")
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame,
                 text="Test Password Security",
                 font=("Helvetica", 18, "bold"),
                 fg="#61dafb", bg="#282c34").pack(pady=20)
        tk.Label(frame,
                 text="Enter Username:",
                 font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=5)
        self.test_username_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.test_username_entry.pack(pady=5)
        
        tk.Button(frame,
                  text="Select Audio & Run Brute Force Test",
                  font=("Helvetica", 14),
                  command=self.test_password_security,
                  bg="#61dafb", fg="#282c34").pack(pady=20)
        tk.Button(frame,
                  text="Back",
                  font=("Helvetica", 12),
                  command=self.create_main_menu,
                  bg="gray", fg="white").pack(pady=10)
    
    def test_password_security(self):
        """
        Uses the fine-tuned AI model (via the candidate generator) to generate 10 candidate passwords
        from the provided audio file, then compares each candidate to the stored password.
        Prints the generated hash, stored password, each candidate, and the final match count.
        """
        username = self.test_username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter your username for testing.")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Your Audio File for Testing",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            print(f"\n[Test] Username: '{username}' selected audio file: {file_path}")
            y, sr = librosa.load(file_path, sr=None)
            y = np.squeeze(y)
            print("[Test] Audio loaded successfully.")
            
            features = extract_features(y, sr)
            if not features:
                messagebox.showerror("Error", "Failed to extract features from the audio file.")
                print("[Test] Feature extraction failed.")
                return
            print("[Test] Extracted features successfully.")
            
            audio_hash = create_hash(features)
            print(f"[Test] Generated Hash: {audio_hash}")
            key = derive_key_from_hash(audio_hash)
            print("[Test] Derived encryption key from hash.")
            
            stored_enc_pw = get_encrypted_password(username, audio_hash)
            if not stored_enc_pw:
                print("[Test] No matching account record found for testing.")
                messagebox.showerror("Error", "No account found for the provided username and audio.\nPlease create an account first.")
                return
            
            stored_password = decrypt_password(stored_enc_pw, key)
            print(f"[Test] Stored password for '{username}': {stored_password}")
            
            model_id = load_fine_tuned_model_id()
            password_gen = AIPasswordGenerator()
            match_count = 0
            print("[Test] Generating 10 candidate passwords using the fine-tuned model:")
            for i in range(1, 11):
                candidate = generate_candidate_password(features, model_id)
                print(f"Candidate {i}: {candidate}")
                if candidate == stored_password:
                    print(f"*** Candidate {i} matches the stored password! ***")
                    match_count += 1
            
            print(f"[Test] Out of 10 attempts, {match_count} candidate(s) matched the stored password.")
            messagebox.showinfo("Security Test Completed",
                                f"Brute Force Test Complete:\n{match_count} out of 10 candidates matched the stored password.")
        except Exception as e:
            print(f"[Test] Error: {str(e)}")
            messagebox.showerror("Error", f"Security test failed: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
