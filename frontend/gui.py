import os
import csv
import time
import tkinter as tk
import requests
import hashlib
import subprocess
from tkinter import messagebox, simpledialog
from vocal_passwords.voice_processing import record_audio
from vocal_passwords.feature_extraction import extract_audio_features
from vocal_passwords.voice_auth import recognize_speech, save_passphrase, save_voiceprint, verify_passphrase, verify_voice
from models.claude_password_generator import generate_password_with_claude

# Paths for stored data
VOICEPRINT_FILE = "stored_voiceprint.npy"
PASSWORD_FILE = "generated_password.txt"

# Global variables
generated_password = None  
test_results = {}  # Stores test results for comparison

### ✅ PASSWORD HANDLING FUNCTIONS
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

def save_hashed_password(password):
    """Hashes and stores the password securely."""
    if not password:
        print("❌ Error: Cannot hash a NoneType password.")
        return None

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    with open("hashed_password.txt", "w") as f:
        f.write(hashed_password + "\n")  

    return hashed_password

### ✅ PASSWORD GENERATION HANDLER
def on_generate():
    """Handles the process of generating a password from voice input and comparing AI vs. Traditional passwords."""
    global generated_password  

    print("Step 1: Starting audio capture...")
    audio, sr = record_audio()
    
    if audio is not None:
        print("Step 2: Extracting voice features...")
        features = extract_audio_features(audio, sr)

        print("Step 3: Recognizing spoken passphrase...")
        passphrase = recognize_speech("vocal_input.wav")

        if not passphrase:
            messagebox.showerror("Error", "Could not detect a passphrase. Try again.")
            return

        print(f"Recognized Passphrase: {passphrase}")

        # ✅ Save passphrase to test_results
        test_results["passphrase"] = passphrase

        print("Step 4: Saving voiceprint & passphrase...")
        save_voiceprint(features)  
        save_passphrase(passphrase)

        print("Step 5: Generating AI password with Claude...")
        response = requests.post("http://127.0.0.1:5000/api/generate-password", files={"audio": open("vocal_input.wav", "rb")})
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract AI and Traditional passwords
            generated_password = data.get("ai_password", "N/A")
            traditional_password = next((res["Password"] for res in data.get("comparison", []) if res["Type"] == "Traditional"), "N/A")

            print(f"✅ Generated Password: {generated_password}")

            # Hash and store the generated password
            hashed_password = save_hashed_password(generated_password)
            print(f"✅ Hashed Password: {hashed_password}")

            # Update UI
            result_label.config(text=f"🔐 AI Password: {generated_password}\n🔐 Traditional Password: {traditional_password}\n\n🔍 Running security tests...")

            # Ensure button exist before disabling them
            compare_button.config(state=tk.DISABLED)

            # Run tests automatically
            run_security_tests()


        else:
            print("❌ Error: Failed to generate password.")
            result_label.config(text="❌ Error generating password!")

    else:
        print("❌ Error: Audio capture failed.")
        result_label.config(text="❌ Error in capturing audio!")

### ✅ AUTOMATED SECURITY TESTS
def run_security_tests():
    """Automatically runs all security tests after password generation."""
    global generated_password, test_results

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    test_results = {}

    print("🔍 Running security tests...")

    # ✅ Claude AI Password Guessing Test
    try:
        response = requests.post("http://127.0.0.1:5000/api/test-password", json={"password": generated_password, "test_type": "claude"})
        response.raise_for_status()
        response_data = response.json()
        test_results["Claude"] = {
            "cracked": response_data.get("cracked", "N/A"),
            "time": response_data.get("time", "N/A"),
            "response": response_data.get("message", "No response from Claude."),
            "attempts": ", ".join(response_data.get("attempts", []))  # ✅ Log Claude's password guesses
        }
    except requests.RequestException:
        test_results["Claude"] = {"cracked": "Error", "time": "N/A", "response": "Error retrieving response.", "attempts": "N/A"}

    time.sleep(1)

    # ✅ GPT-4 Password Guessing Test
    try:
        response = requests.post("http://127.0.0.1:5000/api/test-password", json={"password": generated_password, "test_type": "gpt"})
        response.raise_for_status()
        response_data = response.json()
        test_results["GPT"] = {
            "cracked": response_data.get("cracked", "N/A"),
            "time": response_data.get("time", "N/A"),
            "attempts": response_data.get("attempted_passwords", [])  # ✅ Capture attempted passwords
        }
    except requests.RequestException:
        test_results["GPT"] = {"cracked": "Error", "time": "N/A", "attempts": "Error retrieving attempts."}

    time.sleep(1)

    # ✅ Brute-Force Test
    try:
        response = requests.post("http://127.0.0.1:5000/api/test-password", json={"password": generated_password, "test_type": "brute"})
        response.raise_for_status()
        test_results["Brute Force"] = response.json()
    except requests.RequestException:
        test_results["Brute Force"] = {"cracked": "Error", "time": "N/A"}

    # ✅ Log results
    log_test_results()

    # ✅ Enable "Compare AI Results" button after tests complete
    compare_button.config(state=tk.NORMAL)

### ✅ LOGGING FUNCTION


def log_test_results():
    """Logs AI password, passphrase, and security test results to CSV file with better formatting."""
    log_file = "backend/temp/password_result_log.csv"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    file_exists = os.path.isfile(log_file)

    with open(log_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)  # ✅ Prevents CSV formatting issues

        # ✅ Clear and structured column headers
        if not file_exists:
            writer.writerow([
                "AI_Password", "Passphrase",
                "Claude_Cracked", "Claude_Time", "Claude_Response",
                "Claude_Password_Attempts",
                "GPT_Cracked", "GPT_Time", "GPT_Attempted_Passwords",
                "Brute_Cracked", "Brute_Time"
            ])

        # ✅ Ensure clean data (replace None with "N/A")
        ai_password = generated_password if generated_password else "N/A"
        passphrase = test_results.get("passphrase", "N/A")  # ✅ Make sure passphrase is stored

        claude_cracked = test_results["Claude"].get("cracked", "N/A")
        claude_time = test_results["Claude"].get("time", "N/A")
        claude_response = test_results["Claude"].get("response", "N/A")
        claude_attempts = test_results["Claude"].get("attempts", [])

        gpt_cracked = test_results["GPT"].get("cracked", "N/A")
        gpt_time = test_results["GPT"].get("time", "N/A")
        gpt_attempts = test_results["GPT"].get("attempts", [])

        brute_cracked = test_results["Brute Force"].get("cracked", "N/A")
        brute_time = test_results["Brute Force"].get("time", "N/A")

        # ✅ Fix: Ensure Claude’s attempts are logged correctly
        if isinstance(claude_attempts, list) and claude_attempts:
            claude_attempts_str = "\n".join(claude_attempts)  # ✅ Multi-line only if it's a list
        else:
            claude_attempts_str = "N/A"

        # ✅ Fix: Ensure GPT’s attempted passwords are formatted correctly
        if isinstance(gpt_attempts, list) and gpt_attempts:
            gpt_attempts_str = "\n".join(gpt_attempts)  # ✅ Multi-line for better readability
        else:
            gpt_attempts_str = "N/A"

        # ✅ Write the structured data row
        writer.writerow([
            ai_password, passphrase,
            claude_cracked, claude_time, claude_response,
            claude_attempts_str,  # ✅ Properly formatted password attempts
            gpt_cracked, gpt_time, gpt_attempts_str,
            brute_cracked, brute_time
        ])

    print(f"✅ Security test results saved to {log_file}")

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

### ✅ UI BUTTON HANDLING
def disable_buttons():
    """Disables test button during automated testing."""
    compare_button.config(state=tk.DISABLED)

# ✅ GUI SETUP
app = tk.Tk()
app.title("Secure AI Password Generator")
app.geometry("600x500")
app.configure(bg="#282c34")

header_label = tk.Label(app, text="Vocal-Based Password Generator", font=("Helvetica", 18, "bold"), fg="#61dafb", bg="#282c34")
header_label.pack(pady=20)

generate_button = tk.Button(app, text="Generate Password", font=("Helvetica", 14), bg="#61dafb", command=on_generate)
generate_button.pack(pady=10)

compare_button = tk.Button(app, text="Compare AI Results", font=("Helvetica", 14), bg="#20B2AA", state=tk.DISABLED)
compare_button.pack(pady=5)

login_button = tk.Button(app, text="Login", font=("Helvetica", 14), bg="lightblue", command=on_login)
login_button.pack(pady=10)


result_label = tk.Label(app, text="Click 'Generate Password' to begin.", font=("Helvetica", 12), fg="white", bg="#282c34")
result_label.pack(pady=20)

app.mainloop()
