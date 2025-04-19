import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys
import math
import librosa
import numpy as np
import base64

from audio_feature_extraction import extract_features
from hash_password_generator import create_hash
from symmetric_key_generation import derive_key, new_salt
from encrypt_decrypt_password import encrypt_password, decrypt_password
from database_control import initialize_db, store_encrypted_password, get_encrypted_password_by_hash
from ai_password_generator import AIPasswordGenerator

# --- Set up sys.path for correct folder resolution ---
current_dir = os.path.dirname(__file__)
project_folder = os.path.abspath(os.path.join(current_dir, ".."))
if project_folder not in sys.path:
    sys.path.append(project_folder)

# Import candidate generator from AI_Training.
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
    in the root directory (the parent of the project folder).
    """
    root_folder = os.path.abspath(os.path.join(project_folder, ".."))
    model_info_path = os.path.join(root_folder, "model_info_fold0.txt")
    if not os.path.exists(model_info_path):
        print("Fine-tuned model ID file not found; using default model ID.")
        return "ft:gpt-4o-2024-08-06:personal::BM4R6u51"  # fallback value
    with open(model_info_path, "r") as f:
        model_id = f.read().strip()
    print(f"Loaded Fine-Tuned Model ID: {model_id}")
    return model_id

def edit_distance(s1, s2):
    """
    Computes the Levenshtein edit distance between two strings.
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1,     # deletion
                           dp[i][j-1] + 1,     # insertion
                           dp[i-1][j-1] + cost)  # substitution
    return dp[m][n]

def calculate_entropy(s):
    """
    Calculates the Shannon entropy of a string.
    """
    if not s:
        return 0
    freq = {}
    for char in s:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0
    for count in freq.values():
        p = count / len(s)
        entropy -= p * math.log2(p)
    return entropy

def log_security_test_result(test_result, log_filename="security_test_results.json"):
    """
    Appends the test result (a dictionary) to a JSON file.
    """
    try:
        with open(log_filename, "r") as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        results = []
    results.append(test_result)
    with open(log_filename, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Test result saved to {log_filename}")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Melody-Based Account Manager")
        self.geometry("600x550")
        self.configure(bg="#282c34")
        # No database initialization is needed for the test mode
        print("UI initialized.")
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
            # Salted lookup: fetch salt & encrypted password
            stored_username, b64_salt, stored_enc_pw = get_encrypted_password_by_hash(audio_hash)
            if stored_enc_pw and stored_username == username:
                salt_bytes = base64.b64decode(b64_salt)
                key = derive_key(audio_hash, salt_bytes)
                decrypted_password = decrypt_password(stored_enc_pw, key)
                print(f"[Login] Retrieved stored password for user {stored_username}.")
                messagebox.showinfo("Login Successful", f"Welcome, {self.username_entry.get().strip()}!")
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
            # Generate per‐account salt & derive key
            salt_bytes = new_salt()
            key = derive_key(audio_hash, salt_bytes)
            print("[Account Creation] Derived encryption key from salt and hash.")

            # Check existing record via salted lookup
            stored_username, b64_salt, stored_enc_pw = get_encrypted_password_by_hash(audio_hash)
            if stored_enc_pw and stored_username == username:
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
            store_encrypted_password(
                username=username,
                audio_hash=audio_hash,
                salt=base64.b64encode(salt_bytes).decode("utf-8"),
                encrypted_password=enc_password
            )
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
                 text="Number of Candidates:",
                 font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=5)
        self.candidate_count_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.candidate_count_entry.insert(0, "10")
        self.candidate_count_entry.pack(pady=5)
        
        tk.Button(frame,
                  text="Select Audio & Run Test",
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
        Generates a base secure password using the same pipeline as account creation,
        then uses the fine-tuned candidate generator to create candidate passwords.
        It computes the edit distances for each candidate relative to the base password,
        calculates the Shannon entropy of the base password, and then saves the test results to a JSON file.
        """
        try:
            candidate_count = int(self.candidate_count_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Number of candidates must be an integer.")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Your Audio File for Testing",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            print(f"\n[Test] Selected audio file: {file_path}")
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
            
            # Generate the base secure password on the fly using the standard generator.
            password_gen = AIPasswordGenerator()
            base_password = password_gen.generate_password(features)
            print(f"[Test] Base secure password: {base_password}")
            
            model_id = load_fine_tuned_model_id()
            candidates = []
            match_count = 0
            edit_distances = []
            print(f"[Test] Generating {candidate_count} candidate passwords using the fine-tuned model:")
            for i in range(1, candidate_count + 1):
                candidate = generate_candidate_password(features, model_id)
                candidates.append(candidate)
                distance = edit_distance(candidate, base_password)
                edit_distances.append(distance)
                print(f"Candidate {i}: {candidate} | Edit Distance: {distance}")
                if candidate == base_password:
                    print(f"*** Candidate {i} exactly matches the secure password! ***")
                    match_count += 1
            
            entropy = calculate_entropy(base_password)
            print(f"[Test] Computed Shannon entropy of the secure password: {entropy:.2f} bits")
            print(f"[Test] Out of {candidate_count} attempts, {match_count} candidate(s) matched the secure password.")
            messagebox.showinfo("Security Test Completed",
                                f"Brute Force Test Complete:\n{match_count} out of {candidate_count} candidates matched.\nEntropy: {entropy:.2f} bits")
            
            # Prepare the JSON record (no account dependency here)
            test_result = {
                "audio_hash": audio_hash,
                "base_password": base_password,
                "candidate_count": candidate_count,
                "candidates": candidates,
                "match_count": match_count,
                "edit_distances": edit_distances,
                "entropy": entropy
            }
            log_security_test_result(test_result)
        except Exception as e:
            print(f"[Test] Error: {str(e)}")
            messagebox.showerror("Error", f"Security test failed: {str(e)}")

if __name__ == "__main__":
    initialize_db()
    app = App()
    app.mainloop()
