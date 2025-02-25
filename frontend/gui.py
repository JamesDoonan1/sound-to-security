import os
import csv
import time
import tkinter as tk
import requests
import hashlib
import pandas as pd
from tkinter import messagebox, simpledialog
from vocal_passwords.voice_processing import record_audio
from vocal_passwords.feature_extraction import extract_audio_features
from vocal_passwords.voice_auth import recognize_speech, save_passphrase, save_voiceprint,verify_passphrase, verify_voice, load_passphrase

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
    """Handles AI password generation and comparison with traditional passwords."""
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
        test_results["passphrase"] = passphrase

        print("Step 4: Saving voiceprint & passphrase...")
        save_voiceprint(features)  
        save_passphrase(passphrase)
        verify_passphrase(passphrase)

        print("Step 5: Generating AI password with Claude...")
        response = requests.post("http://127.0.0.1:5000/api/generate-password", files={"audio": open("vocal_input.wav", "rb")})
        
        if response.status_code == 200:
            data = response.json()
            
            # ✅ Extract AI and Traditional passwords from response
            generated_password = data.get("ai_password", "N/A")
            traditional_passwords = data.get("traditional_passwords", [])

            print(f"✅ Generated AI Password: {generated_password}")
            print(f"✅ Traditional Passwords: {', '.join(traditional_passwords)}")
            # ✅ Ensure Traditional Passwords are stored in test_results
            test_results["Traditional_Passwords"] = traditional_passwords if traditional_passwords else ["N/A"]

            # ✅ Debugging - Print Traditional Passwords to ensure they exist
            print(f"🟢 DEBUG: Traditional Passwords stored in test_results: {test_results['Traditional_Passwords']}")

            print(f"🟢 DEBUG: Full API Response: {data}")  # ✅ Add this inside on_generate()

            # ✅ Hash and store AI-generated password
            hashed_password = save_hashed_password(generated_password)
            print(f"✅ Hashed AI Password: {hashed_password}")

            # ✅ Update UI
            result_label.config(text=f"🔐 AI Password: {generated_password}\n🔐 Traditional Passwords: {', '.join(traditional_passwords)}\n\n🔍 Running security tests...")

            # ✅ Ensure button exists before disabling
            compare_button.config(state=tk.DISABLED)

            # ✅ Run security tests automatically
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

    if "Traditional_Passwords" not in test_results:
         test_results["Traditional_Passwords"] = []


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

        # ✅ Debugging API Response
        print(f"🟢 DEBUG: GPT Full API Response: {response_data}")

        # ✅ Explicitly store and format attempted passwords
        gpt_attempts = response_data.get("attempts", [])
        if not gpt_attempts or not isinstance(gpt_attempts, list):
            gpt_attempts = ["No attempts generated"]

        test_results["GPT"] = {
            "cracked": response_data.get("cracked", "N/A"),
            "time": response_data.get("time", "N/A"),
            "attempts": gpt_attempts  # ✅ Ensure it is always a list
        }

        # ✅ Additional Debugging Before Logging
        print(f"🟢 DEBUG: GPT Stored Attempts in test_results: {test_results['GPT']['attempts']}")

    except requests.RequestException as e:
        print(f"❌ GPT Testing Error: {e}")
        test_results["GPT"] = {"cracked": "Error", "time": "N/A", "attempts": ["Error retrieving attempts."]}

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
    """Logs AI password, passphrase, security test results, and traditional passwords to CSV file."""
    log_file = "backend/temp/password_result_log.csv"

    if test_results.get("passphrase") in ["UNKNOWN_PHRASE", "ERROR", None, "N/A"]:
        test_results["passphrase"] = load_passphrase()

    # ✅ Ensure GPT test results are stored properly
    test_results["GPT"] = test_results.get("GPT", {})

    # ✅ Retrieve and format Traditional Passwords correctly
    traditional_passwords_list = test_results.get("Traditional_Passwords", [])

    # If missing, extract from 'comparison'
    if not traditional_passwords_list:
        traditional_passwords_list = [
            item["Password"] for item in test_results.get("comparison", []) if item["Type"] == "Traditional"
        ]

    # ✅ Ensure we extract traditional passwords if they exist in 'comparison'
    if not traditional_passwords_list:
        traditional_passwords_list = [
            item["Password"] for item in test_results.get("comparison", []) if item["Type"] == "Traditional"
        ]

    # Convert to string format
    if isinstance(traditional_passwords_list, list) and traditional_passwords_list:
        traditional_passwords_str = "; ".join(traditional_passwords_list)
    else:
        traditional_passwords_str = "N/A"

    # Debugging output
    print(f"🟢 DEBUG: Extracted Traditional Passwords → {traditional_passwords_list}")
    print(f"🟢 DEBUG: Traditional Passwords to be logged → {traditional_passwords_str}")
    
    # ✅ Ensure Claude's response is not overwritten
    if "Claude" not in test_results:
        test_results["Claude"] = {}

    gpt_attempts_list = test_results["GPT"].get("attempts", [])
    if not gpt_attempts_list or not isinstance(gpt_attempts_list, list):
        gpt_attempts_list = ["No attempts generated"]
    gpt_attempts_str = ", ".join(gpt_attempts_list)

    try:
        # ✅ Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        print(f"DEBUG: Final passphrase being logged: {test_results['passphrase']}")
        # Debugging before writing to CSV

        # ✅ Define column headers and their corresponding data mappings
        columns = {
            "Timestamp": lambda: time.strftime("%Y-%m-%d %H:%M:%S"),
            "AI_Password": lambda: generated_password or "N/A",
            "Passphrase": lambda: test_results.get("passphrase", "N/A"),
            "Claude_Cracked": lambda: test_results.get("Claude", {}).get("cracked", "N/A"),
            "Claude_Time": lambda: test_results.get("Claude", {}).get("time", "N/A"),
            "Claude_Response": lambda: test_results.get("Claude", {}).get("response", "N/A"),
            "Claude_Attempts": lambda: format_attempts(test_results.get("Claude", {}).get("attempts", [])),
            "GPT_Cracked": lambda: str(test_results["GPT"].get("cracked", "N/A")),
            "GPT_Time": lambda: str(test_results["GPT"].get("time", "N/A")),
            "GPT_Attempts": lambda: gpt_attempts_str,
            "Brute_Cracked": lambda: test_results.get("Brute Force", {}).get("cracked", "N/A"),
            "Brute_Time": lambda: test_results.get("Brute Force", {}).get("time", "N/A"),
            "Traditional_Passwords": lambda: traditional_passwords_str 

        }

        file_exists = os.path.isfile(log_file)

        with open(log_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)

            if not file_exists:
                writer.writerow(columns.keys())

            writer.writerow([func() for func in columns.values()])

        print(f"✅ Security test results saved to {log_file}")

    except Exception as e:
        print(f"❌ Error logging test results: {e}")

def flatten_columns(columns, prefix=""):
    """Flattens nested column structure into a list of header names."""
    headers = []
    for key, value in columns.items():
        if isinstance(value, dict):
            headers.extend(flatten_columns(value, f"{key}_"))
        else:
            headers.append(f"{prefix}{key}")
    return headers

def format_attempts(attempts):
    """Formats password attempts into a clean string representation."""
    if not attempts:
        return "N/A"
    
    if isinstance(attempts, str):
        return attempts.replace("\n", "; ")
    
    if isinstance(attempts, list):
        return "; ".join(str(attempt) for attempt in attempts)
    
    return str(attempts)

def generate_row_data(columns):
    """Generates a single row of data based on the column structure."""
    row_data = []
    
    def process_value(value):
        if isinstance(value, dict):
            return [process_value(v) for v in value.values()]
        return [value()]
    
    for value in columns.values():
        row_data.extend(process_value(value))
    
    return row_data

def write_to_csv(log_file, headers, row_data):
    """Writes the data to CSV file with proper encoding and error handling."""
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)  # Quote all fields for consistency
        
        # Write headers if file is new
        if not file_exists:
            writer.writerow(headers)
        
        # Write data row
        writer.writerow(row_data)

def log_error(error):
    """Logs errors to a separate error log file."""
    error_log = "backend/temp/error_log.txt"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(error_log, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Error in logging test results: {str(error)}\n")
    except Exception as e:
        print(f"❌ Failed to log error: {str(e)}")



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
            stored_passphrase = load_passphrase()

            if verify_passphrase(recognized_passphrase):
                print("✅ Passphrase matched! Now verifying AI-generated password...")
                user_entered_password = simpledialog.askstring("Password Required", "Enter the AI-generated password:")
                
                # ✅ Load the stored hashed password
                with open("hashed_password.txt", "r") as f:
                    stored_hashed_password = f.read().strip()

                # ✅ Hash the user-entered password before comparison
                user_hashed_password = hashlib.sha256(user_entered_password.encode()).hexdigest()

                if user_hashed_password == stored_hashed_password:
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


def compare_ai_results():
    """Opens a new window to display AI vs Traditional Password Comparison."""
    log_file = "backend/temp/password_result_log.csv"

    if not os.path.exists(log_file):
        messagebox.showerror("Error", "No test results available. Run security tests first.")
        return

    try:
        # Load CSV file into a DataFrame
        df = pd.read_csv(log_file)

        if df.empty:
            messagebox.showerror("Error", "No data found in the log file.")
            return

        # Get the latest test result (last row)
        latest_result = df.iloc[-1]

        # ✅ Extract key data
        ai_password = latest_result["AI_Password"]
        passphrase = latest_result["Passphrase"]
        cl_cracked = latest_result["Claude_Cracked"]
        cl_attempts = latest_result["Claude_Attempts"]
        gpt_cracked = latest_result["GPT_Cracked"]
        gpt_attempts = latest_result["GPT_Attempts"]
        brute_cracked = latest_result["Brute_Cracked"]
        traditional_passwords = latest_result["Traditional_Passwords"]

        # ✅ Create a new Tkinter window to display results
        compare_window = tk.Toplevel(app)
        compare_window.title("AI Password Security Comparison")
        compare_window.geometry("600x500")

        tk.Label(compare_window, text="🔍 AI Password Security Results", font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(compare_window, text=f"🔐 AI Password: {ai_password}", font=("Helvetica", 12)).pack()
        tk.Label(compare_window, text=f"🗣️ Passphrase: {passphrase}", font=("Helvetica", 12)).pack()
        tk.Label(compare_window, text=f"🤖 Claude Cracked: {cl_cracked}", font=("Helvetica", 12)).pack()
        tk.Label(compare_window, text=f"🔓 Claude's Attempts: {cl_attempts}", font=("Helvetica", 12)).pack()
        tk.Label(compare_window, text=f"🤖 GPT-4 Cracked: {gpt_cracked}", font=("Helvetica", 12)).pack()
        tk.Label(compare_window, text=f"🔓 GPT-4's Attempts: {gpt_attempts}", font=("Helvetica", 12)).pack()
        tk.Label(compare_window, text=f"🔨 Brute-Force Cracked: {brute_cracked}", font=("Helvetica", 12)).pack()
        tk.Label(compare_window, text=f"🔑 Traditional Passwords: {traditional_passwords}", font=("Helvetica", 12, "bold")).pack()

        tk.Button(compare_window, text="Close", command=compare_window.destroy).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load test results: {e}")

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

compare_button = tk.Button(app, text="Compare AI Results", font=("Helvetica", 14), bg="#20B2AA", state=tk.DISABLED, command=compare_ai_results)
compare_button.pack(pady=5)

login_button = tk.Button(app, text="Login", font=("Helvetica", 14), bg="lightblue", command=on_login)
login_button.pack(pady=10)


result_label = tk.Label(app, text="Click 'Generate Password' to begin.", font=("Helvetica", 12), fg="white", bg="#282c34")
result_label.pack(pady=20)

app.mainloop()
