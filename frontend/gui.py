import requests
import os
import tkinter as tk
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

        # ✅ Debugging: Confirm files are saved correctly
        if os.path.exists("stored_passphrase.txt"):
            print("✅ Passphrase saved successfully.")
        else:
            print("❌ ERROR: Passphrase not saved!")

        if os.path.exists("stored_voiceprint.npy"):
            print("✅ Voiceprint saved successfully.")
        else:
            print("❌ ERROR: Voiceprint not saved!")
        

        print("Step 5: Generating AI password with Claude...")
        generated_password = generate_password_with_claude(features)

        if generated_password and "Error" not in generated_password:
            print(f"✅ Generated Password: {generated_password}")
            save_password(generated_password)  
            result_label.config(text=f"🔐 Generated Password:\n{generated_password}")

            # ✅ Enable test buttons!
            gpt_test_button.config(state=tk.NORMAL)
            claude_test_button.config(state=tk.NORMAL)
            brute_test_button.config(state=tk.NORMAL)
            compare_button.config(state=tk.NORMAL)

        else:
            print("❌ Error: Failed to generate password.")
            result_label.config(text="❌ Error in generating password!")
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

compare_button = tk.Button(app, text="Compare AI Results", font=("Helvetica", 14), bg="#20B2AA", command=compare_ai_results, state=tk.DISABLED)
compare_button.pack(pady=5)

result_label = tk.Label(app, text="Click 'Generate Password' to begin.", font=("Helvetica", 12), fg="white", bg="#282c34")
result_label.pack(pady=20)

login_button = tk.Button(app, text="Login", font=("Helvetica", 14), bg="lightblue", command=on_login)
login_button.pack(pady=10) 

app.mainloop()
