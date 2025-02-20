import requests
import os
import tkinter as tk
import requests
import hashlib
import subprocess
from tkinter import messagebox, simpledialog
from vocal_passwords.voice_processing import record_audio
from vocal_passwords.feature_extraction import extract_audio_features
from vocal_passwords.voice_auth import recognize_speech, save_passphrase, save_voiceprint, load_voiceprint, verify_passphrase, verify_voice
from models.claude_password_generator import generate_password_with_claude

# Paths for stored data
VOICEPRINT_FILE = "stored_voiceprint.npy"
PASSWORD_FILE = "generated_password.txt"

# Global variables to store the generated password and test results
generated_password = None  
test_results = {}  # Stores test results for comparison

def save_password(password):
    """Save the AI-generated password for login verification."""
    with open(PASSWORD_FILE, "w") as f:
        f.write(password)

def load_password():
    """Retrieve the stored AI-generated password."""
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as f:
            return f.read().strip()
    return None

def hash_password(password):
    """Hashes a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def save_hashed_password(password):
    """Hashes the password using SHA-256 and saves it correctly."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # ✅ Overwrite file with only the hash
    with open("hashed_password.txt", "w") as f:
        f.write(hashed_password + "\n")  # ✅ Ensure single hash with newline

    return hashed_password



def on_generate():
    """Handles the process of generating a password from voice input."""
    global generated_password  

    print("Step 1: Starting audio capture...")
    audio, sr = record_audio()
    
    if audio is not None:
        print("Step 2: Audio captured successfully. Proceeding to feature extraction...")
        features = extract_audio_features(audio, sr)
        print(f"Extracted features: {features}")

        print("Step 3: Recognizing spoken passphrase...")
        passphrase = recognize_speech("vocal_input.wav")

        if not passphrase:
            messagebox.showerror("Error", "Could not detect a passphrase. Try again.")
            return

        print(f"Recognized Passphrase: {passphrase}")

        print("Step 4: Saving voiceprint & passphrase...")
        save_voiceprint(features)  
        save_passphrase(passphrase)

        print("Step 5: Generating AI password with Claude...")
        generated_password = generate_password_with_claude(features)

        if generated_password and "Error" not in generated_password:
            print(f"✅ Generated Password: {generated_password}")

            hashed_password = save_hashed_password(generated_password)
            print(f"✅ Hashed Password: {hashed_password}")


            # Save the hashed password to a file in correct format
            with open("hashed_password.txt", "w") as f:
                f.write(f"{hashed_password}\n")

            save_password(generated_password)  
            result_label.config(text=f"🔐 Generated Password:\n{generated_password}")

            # ✅ Enable test buttons!
            gpt_test_button.config(state=tk.NORMAL)
            claude_test_button.config(state=tk.NORMAL)
            brute_test_button.config(state=tk.NORMAL)
            compare_button.config(state=tk.NORMAL)
            hashcat_test_button.config(state=tk.NORMAL)

    else:
        print("❌ Error: Audio capture failed.")
        result_label.config(text="❌ Error in capturing audio!")

def test_with_gpt():
    """Tests the AI-generated password with GPT-4 Turbo cracking attempt."""
    global generated_password, test_results

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    print("🔍 Testing password security with GPT-4 Turbo...")
    result_label.config(text="Testing password with GPT... Please wait.")

    try:
        url = "http://127.0.0.1:5000/api/test-password"
        response = requests.post(url, json={"password": generated_password, "test_type": "gpt"})
        response.raise_for_status()
        test_results["GPT"] = response.json()

        print("✅ GPT Response:", test_results["GPT"])  # Debugging output
        result_label.config(text="✅ GPT test completed. Click 'Compare AI Results' to view.")
    except requests.RequestException as e:
        print(f"❌ Error during GPT password testing: {e}")
        result_label.config(text="❌ Error in testing password with GPT!")

def test_with_claude():
    """Tests the password with Claude to see if it can break its own password."""
    global generated_password, test_results

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    print("🔍 Testing password security with Claude...")
    result_label.config(text="Testing password with Claude... Please wait.")

    try:
        url = "http://127.0.0.1:5000/api/test-password"
        response = requests.post(url, json={"password": generated_password, "test_type": "claude"})
        response.raise_for_status()
        test_results["Claude"] = response.json()

        print("✅ Claude Response:", test_results["Claude"])  # Debugging output
        result_label.config(text="✅ Claude test completed. Click 'Compare AI Results' to view.")
    except requests.RequestException as e:
        print(f"❌ Error during Claude password testing: {e}")
        result_label.config(text="❌ Error in testing password with Claude!")

def test_with_brute_force():
    """Runs brute-force and dictionary attack simulations."""
    global generated_password, test_results

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    print("🔍 Running brute-force and dictionary attacks...")
    result_label.config(text="Running brute-force & dictionary attacks... Please wait.")

    try:
        url = "http://127.0.0.1:5000/api/test-password"
        response = requests.post(url, json={"password": generated_password, "test_type": "brute"})
        response.raise_for_status()
        test_results["Brute Force"] = response.json()

        result_label.config(text="✅ Brute-force & dictionary test completed. Click 'Compare AI Results' to view.")
    except requests.RequestException as e:
        print(f"❌ Error during brute-force password testing: {e}")
        result_label.config(text="❌ Error in testing password with brute-force!")

def compare_ai_results():
    """Displays AI cracking test results in a structured format."""
    global test_results

    if not test_results:
        messagebox.showerror("Error", "No AI test results available. Run tests first.")
        return

    compare_window = tk.Toplevel(app)
    compare_window.title("AI Cracking Comparison")
    compare_window.geometry("600x500")
    compare_window.configure(bg="#1e1e1e")

    tk.Label(compare_window, text="🔍 AI Password Testing Results", font=("Helvetica", 16, "bold"), fg="white", bg="#1e1e1e").pack(pady=10)

    for test_type, result in test_results.items():
        tk.Label(compare_window, text=f"🛠 {test_type} Test:", font=("Helvetica", 14, "bold"), fg="#61dafb", bg="#1e1e1e").pack(pady=5)
        tk.Label(compare_window, text=f"✅ Cracked: {result.get('cracked', 'Unknown')}", font=("Helvetica", 12), fg="white", bg="#1e1e1e").pack()

        explanation = result.get("explanation", "N/A")
        if explanation and explanation != "N/A":
            tk.Label(compare_window, text=f"📄 Explanation: {explanation}", font=("Helvetica", 12), fg="#FFA500", bg="#1e1e1e").pack()

        attempts = result.get("attempts", "N/A")
        tk.Label(compare_window, text=f"📋 Attempts: {attempts}", font=("Helvetica", 12), fg="white", bg="#1e1e1e").pack()
        tk.Label(compare_window, text="---------------------------------", fg="gray", bg="#1e1e1e").pack()

def on_login():
    """Handles voice-based login authentication."""
    print("🔐 Step 1: Recording login voice...")
    audio, sr = record_audio()
    
    if audio is not None:
        print("🔍 Step 2: Extracting login voice features...")
        features = extract_audio_features(audio, sr)
        
        print("🛠 Step 3: Verifying voiceprint...")
        if verify_voice(features):
            print("✅ Voice matched! Checking passphrase...")
            recognized_passphrase = recognize_speech("vocal_input.wav")  
            stored_passphrase = load_password()

            if verify_passphrase(recognized_passphrase):
                print("✅ Passphrase matched! Now verifying AI-generated password...")
                user_entered_password = simpledialog.askstring("Password Required", "Enter the AI-generated password:")
                stored_password = load_password()

                if user_entered_password == stored_password:
                    print("✅ Access Granted! 🎉")
                    result_label.config(text="✅ Access Granted! 🎉")
                else:
                    print("❌ Incorrect AI-generated password. Access Denied.")
                    result_label.config(text="❌ Incorrect AI-generated password.")
            else:
                print("❌ Incorrect passphrase. Access Denied.")
                result_label.config(text="❌ Incorrect passphrase.")
        else:
            print("❌ Access Denied! Voice does not match.")
            result_label.config(text="❌ Access Denied! Voice does not match.")
    else:
        print("❌ Error: Audio capture failed.")
        result_label.config(text="❌ Error in capturing audio!")


def test_with_hashcat():
    """Runs Hashcat to attempt cracking the hashed password."""
    global generated_password, test_results

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    print("🔍 Running Hashcat attack...")
    result_label.config(text="Running Hashcat attack... Please wait.")

    try:
        # ✅ Full path to Hashcat (update this path if necessary)
        hashcat_path = r"C:\Users\James Doonan\Downloads\hashcat-6.2.6\hashcat-6.2.6\hashcat.exe"

        # ✅ Validate hashed_password.txt exists
        if not os.path.exists("hashed_password.txt"):
            print("❌ Error: hashed_password.txt not found!")
            result_label.config(text="❌ hashed_password.txt not found!")
            return

        # ✅ Validate rockyou.txt exists
        wordlist_path = "rockyou.txt"
        if not os.path.exists(wordlist_path):
            print("❌ Error: rockyou.txt not found! Download and place it in the same folder.")
            result_label.config(text="❌ rockyou.txt not found! Download and place it in the same folder.")
            return

        # ✅ Exact Hashcat Command (Matches Your Working CLI Command)
        command = [
            hashcat_path,  # ✅ Hashcat Executable Path
            "-D", "1",  # ✅ Force CPU execution
            "-m", "1400",  # ✅ SHA-256 Hash Mode
            "-a", "0",  # ✅ Dictionary Attack Mode
            "hashed_password.txt",  # ✅ Input Hash File
            wordlist_path,  # ✅ Wordlist File
            "--force"  # ✅ Force Run (since OpenCL is disabled)
        ]

        # ✅ Run Hashcat and Capture Output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        hashcat_output = ""
        for line in process.stdout:
            print("🔥 Hashcat Output:", line.strip())  # Print real-time output
            hashcat_output += line.strip() + "\n"

        process.wait()

        # ✅ Process Hashcat Results
        if "Recovered" in hashcat_output or "Cracked" in hashcat_output:
            cracked = True
            result_text = "✅ Hashcat cracked the password!"
        elif "No hashes loaded" in hashcat_output:
            cracked = False
            result_text = "❌ Hashcat did not recognize the hash format!"
        elif "Token length exception" in hashcat_output:
            cracked = False
            result_text = "❌ Hash format incorrect! Ensure it's a single SHA-256 hash."
        else:
            cracked = False
            result_text = "❌ No password cracked!"

        test_results["Hashcat"] = {"cracked": cracked, "result": result_text, "output": hashcat_output}
        result_label.config(text=result_text)

    except Exception as e:
        print(f"❌ Error during Hashcat password testing: {e}")
        result_label.config(text="❌ Error in testing password with Hashcat!")


# Create main app window
app = tk.Tk()
app.title("Secure AI Password Generator")
app.geometry("600x500")
app.configure(bg="#282c34")

header_label = tk.Label(app, text="Vocal-Based Password Generator", font=("Helvetica", 18, "bold"), fg="#61dafb", bg="#282c34")
header_label.pack(pady=20)

generate_button = tk.Button(app, text="Generate Password", font=("Helvetica", 14), bg="#61dafb", command=on_generate)
generate_button.pack(pady=10)

gpt_test_button = tk.Button(app, text="Test with GPT", font=("Helvetica", 14), bg="#FFA500", command=test_with_gpt, state=tk.DISABLED)
gpt_test_button.pack(pady=5)

claude_test_button = tk.Button(app, text="Test with Claude", font=("Helvetica", 14), bg="#FFD700", command=test_with_claude, state=tk.DISABLED)
claude_test_button.pack(pady=5)

brute_test_button = tk.Button(app, text="Test Brute Force & Dictionary", font=("Helvetica", 14), bg="#DC143C", command=test_with_brute_force, state=tk.DISABLED)
brute_test_button.pack(pady=5)

hashcat_test_button = tk.Button(app, text="Test with Hashcat", font=("Helvetica", 14), bg="#FF5733", command=test_with_hashcat, state=tk.DISABLED)
hashcat_test_button.pack(pady=5)


compare_button = tk.Button(app, text="Compare AI Results", font=("Helvetica", 14), bg="#20B2AA", command=compare_ai_results, state=tk.DISABLED)
compare_button.pack(pady=5)

result_label = tk.Label(app, text="Click 'Generate Password' to begin.", font=("Helvetica", 12), fg="white", bg="#282c34")
result_label.pack(pady=20)

login_button = tk.Button(app, text="Login", font=("Helvetica", 14), bg="lightblue", command=on_login)
login_button.pack(pady=10) 

app.mainloop()
