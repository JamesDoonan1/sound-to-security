import requests
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from vocal_passwords.voice_processing import record_audio
from vocal_passwords.feature_extraction import extract_audio_features
from vocal_passwords.voice_auth import recognize_speech, save_passphrase, save_voiceprint, load_voiceprint, verify_passphrase, verify_voice, load_passphrase
from models.claude_password_generator import generate_password_with_claude

# Paths for stored data
VOICEPRINT_FILE = "stored_voiceprint.npy"
PASSWORD_FILE = "generated_password.txt"

# Global variable to store the generated password
generated_password = None  

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
        save_passphrase(passphrase)  # ✅ Correct, now we store the passphrase

        print("Step 5: Generating AI password with Claude...")
        generated_password = generate_password_with_claude(features, passphrase)  # ✅ Passphrase is now used in AI prompt

        if generated_password and "Error" not in generated_password:
            print(f"✅ Generated Password: {generated_password}")
            save_password(generated_password)  # ✅ Now we store the AI-generated password correctly
            result_label.config(text=f"🔐 Generated Password:\n{generated_password}")

            # ✅ Ensure buttons become active!
            test_button.config(state=tk.NORMAL)
            login_button.config(state=tk.NORMAL)
            test_button.update_idletasks()
            login_button.update_idletasks() 
        else:
            print("❌ Error: Failed to generate password.")
            result_label.config(text="❌ Error in generating password!")
    else:
        print("❌ Error: Audio capture failed.")
        result_label.config(text="❌ Error in capturing audio!")

def on_test_password():
    """Handles testing the generated password for security with real-time AI updates."""
    global generated_password

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    print("Step 6: Testing the generated password...")
    result_label.config(text="Testing password strength... Please wait.")

    try:
        url = "http://127.0.0.1:5000/api/test-password"
        response = requests.post(url, json={"password": generated_password})
        response.raise_for_status()
        result = response.json()

        # Extract results safely
        ai_attack = result.get("ai_attack", {})
        brute_force = result.get("brute_force", {})
        dictionary_attack = result.get("dictionary_attack", {})

        # ✅ Format the results for the GUI
        formatted_result = f"""
🔍 **PASSWORD STRENGTH TEST RESULTS**

🛡 **AI-Based Attack:**  
   ✅ Cracked: {ai_attack.get("cracked", False)}  
   ℹ Explanation: {ai_attack.get("explanation", "No explanation provided.")}

⚡ **Brute Force Attack:**  
   ✅ Cracked: {brute_force.get("cracked", False)}  
   ⏳ Message: {brute_force.get("message", "N/A")}

📖 **Dictionary Attack:**  
   ✅ Cracked: {dictionary_attack.get("cracked", False)}  
   📜 Message: {dictionary_attack.get("message", "N/A")}
"""

        # ✅ Display results in the GUI instead of a pop-up
        result_label.config(text=formatted_result, justify="left")

    except requests.RequestException as e:
        print(f"Error during password testing: {e}")
        result_label.config(text="❌ Error in testing password!")
        messagebox.showerror("Error", "Failed to test the password. Ensure the backend server is running.")


def on_login():
    """Handles voice-based login authentication with passphrase and AI password verification."""
    print("🔐 Step 1: Recording login voice...")
    audio, sr = record_audio()

    if audio is not None:
        print("🔍 Step 2: Extracting login voice features...")
        features = extract_audio_features(audio, sr)

        print("🛠 Step 3: Verifying voiceprint...")
        if verify_voice(features):
            print("✅ Voice matched! Checking passphrase...")
            recognized_passphrase = recognize_speech("vocal_input.wav")  # Convert to text
            stored_passphrase = load_passphrase()  # ✅ Corrected, now loading passphrase properly

            if verify_passphrase(recognized_passphrase):
                print("✅ Passphrase matched! Now verifying AI-generated password...")

                # Prompt user to enter AI-generated password
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
        result_label.config(text="Error in capturing audio!")

# Create main app window
app = tk.Tk()
app.title("Secure Melody-Based Password Generator")
app.geometry("500x400")
app.configure(bg="#282c34")  # Set background color

# UI Elements
header_label = tk.Label(app, text="Vocal-Based Password Generator", font=("Helvetica", 18, "bold"), fg="#61dafb", bg="#282c34")
header_label.pack(pady=20)

generate_button = tk.Button(app, text="Generate Password", font=("Helvetica", 14), bg="#61dafb", fg="#282c34",
                            activebackground="#21a1f1", activeforeground="white", command=on_generate)
generate_button.pack(pady=10)

test_button = tk.Button(app, text="Test Password Strength", font=("Helvetica", 14), bg="#ff9800", fg="white",
                        activebackground="#f57c00", activeforeground="white", command=on_test_password, state=tk.DISABLED)
test_button.pack(pady=10)

login_button = tk.Button(app, text="Login with Voice", font=("Helvetica", 14), bg="#4CAF50", fg="white",
                         activebackground="#388E3C", activeforeground="white", command=on_login, state=tk.DISABLED)
login_button.pack(pady=10)

result_label = tk.Label(app, text="Click 'Generate Password' to begin.", font=("Helvetica", 12), fg="white", bg="#282c34", wraplength=400, justify="center")
result_label.pack(pady=20)

footer_label = tk.Label(app, text="Developed by James Doonan", font=("Helvetica", 10), fg="gray", bg="#282c34")
footer_label.pack(side="bottom", pady=10)

# Start the main event loop
app.mainloop()
