import os
import csv
import time
import tkinter as tk
import requests
import hashlib
import pandas as pd
from tkinter import messagebox, simpledialog
from tkinter import ttk
from vocal_passwords.voice_processing import record_audio
from vocal_passwords.feature_extraction import extract_audio_features
from vocal_passwords.voice_auth import recognize_speech, save_passphrase, save_voiceprint, verify_passphrase, verify_voice, load_passphrase

from audio_passwords.main import choose_audio_file

# Paths for stored data
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)  # moves up to 'sound-to-security'
DATA_DIR = os.path.join(ROOT_DIR, "backend", "data")
LOGS_DIR = os.path.join(ROOT_DIR, "backend", "logs")

PASSWORD_FILE = os.path.join(DATA_DIR, "generated_password.txt")
HASHED_PASSWORD_FILE = os.path.join(DATA_DIR, "hashed_password.txt")
PASSPHRASE_FILE = os.path.join(DATA_DIR, "stored_passphrase.txt")
VOICEPRINT_FILE = os.path.join(DATA_DIR, "stored_voiceprint.npy")

PASSWORD_RESULT_LOG = os.path.join(LOGS_DIR, "password_result_log.csv")
PASSWORD_DATA_FILE = os.path.join(LOGS_DIR, "password_data.csv")

# Global variables
generated_password = None  
test_results = {}  # Stores test results for comparison
current_username = "default_user"  # Default username

class AudioAccountDialog(tk.Toplevel):
    """Custom dialog for audio file password creation/login."""
    
    def __init__(self, parent, for_login=False):
        super().__init__(parent)
        self.parent = parent
        self.for_login = for_login
        self.result = None
        self.username = ""
        
        # Configure dialog window
        title = "Audio File Login" if for_login else "Create Audio Password"
        self.title(title)
        self.geometry("450x250")
        self.configure(bg="#282c34")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        # Build UI
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_text = "Audio Login" if self.for_login else "Create Audio Password"
        header = tk.Label(
            self, 
            text=header_text,
            font=("Helvetica", 16, "bold"),
            fg="#61dafb",
            bg="#282c34"
        )
        header.pack(pady=15)
        
        # Username frame
        username_frame = tk.Frame(self, bg="#282c34")
        username_frame.pack(pady=10, fill="x", padx=30)
        
        username_label = tk.Label(
            username_frame,
            text="Username:",
            font=("Helvetica", 12),
            fg="white",
            bg="#282c34",
            anchor="w"
        )
        username_label.pack(fill="x")
        
        self.username_entry = tk.Entry(
            username_frame,
            font=("Helvetica", 12),
            bg="#1e2127",
            fg="white",
            insertbackground="white"
        )
        self.username_entry.pack(fill="x", pady=5)
        self.username_entry.insert(0, "default_user")
        self.username_entry.focus_set()
        
        # Buttons frame
        btn_frame = tk.Frame(self, bg="#282c34")
        btn_frame.pack(pady=20, fill="x", padx=30)
        
        action_text = "Select Audio & Login" if self.for_login else "Select Audio & Create Password"
        
        select_btn = tk.Button(
            btn_frame,
            text=action_text,
            font=("Helvetica", 12),
            bg="#61dafb",
            fg="#282c34",
            activebackground="#21a1f1",
            activeforeground="white",
            command=self.on_submit
        )
        select_btn.pack(side="left", padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Helvetica", 12),
            bg="gray",
            fg="white",
            activebackground="#666",
            activeforeground="white",
            command=self.on_cancel
        )
        cancel_btn.pack(side="right", padx=10)
    
    def on_submit(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showerror("Error", "Username is required", parent=self)
            return
        
        # Close the dialog
        self.grab_release()
        self.destroy()
        
        # Proceed with file selection
        self.process_audio_file()
    
    def on_cancel(self):
        self.grab_release()
        self.destroy()
    
    def process_audio_file(self):
        from audio_passwords.main import choose_audio_file
        choose_audio_file(username=self.username, for_login=self.for_login)

def show_audio_dialog(parent, for_login=False):
    """Shows the custom dialog for audio password creation/login."""
    dialog = AudioAccountDialog(parent, for_login=for_login)
    parent.wait_window(dialog)

###  PASSWORD HANDLING FUNCTIONS
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
        print(" Error: Cannot hash a NoneType password.")
        return None

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Correct file path
    HASHED_PASSWORD_FILE = os.path.join(DATA_DIR, "hashed_password.txt")

    with open(HASHED_PASSWORD_FILE, "w") as f:  
        f.write(hashed_password + "\n")  

    return hashed_password

###  PASSWORD GENERATION HANDLER
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
            
            #  Extract AI and Traditional passwords from response
            generated_password = data.get("ai_password", "N/A")
            traditional_passwords = data.get("traditional_passwords", [])

            print(f" Generated AI Password: {generated_password}")
            print(f" Traditional Passwords: {', '.join(traditional_passwords)}")
            #  Ensure Traditional Passwords are stored in test_results
            test_results["Traditional_Passwords"] = traditional_passwords if traditional_passwords else ["N/A"]

            #  Hash and store AI-generated password
            hashed_password = save_hashed_password(generated_password)
            print(f" Hashed AI Password: {hashed_password}")

            #  Update UI
            result_label.config(text=f" AI Password: {generated_password}\n Traditional Passwords: {', '.join(traditional_passwords)}\n\n Running security tests...")

            # Ensure button exists before disabling
            compare_button.config(state=tk.DISABLED)

            # Enable test button so user can run it manually
            test_button.config(state=tk.NORMAL)


        else:
            print(" Error: Failed to generate password.")
            result_label.config(text=" Error generating password!")

    else:
        print(" Error: Audio capture failed.")
        result_label.config(text=" Error in capturing audio!")

###  AUTOMATED SECURITY TESTS
def run_security_tests():
    """Automatically runs all security tests after password generation."""
    global generated_password, test_results

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    if "Traditional_Passwords" not in test_results:
         test_results["Traditional_Passwords"] = []

    print("🔍 Running security tests...")

    #  Claude AI Password Guessing Test
    try:
        response = requests.post("http://127.0.0.1:5000/api/test-password", json={"password": generated_password, "test_type": "claude"})
        response.raise_for_status()
        response_data = response.json()
        test_results["Claude"] = {
            "cracked": response_data.get("cracked", "N/A"),
            "time": response_data.get("time", "N/A"),
            "response": response_data.get("message", "No response from Claude."),
            "attempts": ", ".join(response_data.get("attempts", []))  #  Log Claude's password guesses
        }
    except requests.RequestException:
        test_results["Claude"] = {"cracked": "Error", "time": "N/A", "response": "Error retrieving response.", "attempts": "N/A"}

    time.sleep(1)

    #  GPT-4 Password Guessing Test 
    try:
        response = requests.post("http://127.0.0.1:5000/api/test-password", json={"password": generated_password, "test_type": "gpt"})
        response.raise_for_status()
        response_data = response.json()

        #  Explicitly store and format attempted passwords
        gpt_attempts = response_data.get("attempts", [])
        if not gpt_attempts or not isinstance(gpt_attempts, list):
            gpt_attempts = ["No attempts generated"]

        test_results["GPT"] = {
            "cracked": response_data.get("cracked", "N/A"),
            "time": response_data.get("time", "N/A"),
            "attempts": gpt_attempts  #  Ensure it is always a list
        }

    except requests.RequestException as e:
        print(f" GPT Testing Error: {e}")
        test_results["GPT"] = {"cracked": "Error", "time": "N/A", "attempts": ["Error retrieving attempts."]}

    time.sleep(1)

    #  Brute-Force Test
    try:
        response = requests.post("http://127.0.0.1:5000/api/test-password", json={"password": generated_password, "test_type": "brute"})
        response.raise_for_status()
        test_results["Brute Force"] = response.json()
    except requests.RequestException:
        test_results["Brute Force"] = {"cracked": "Error", "time": "N/A"}

    #  Log results
    log_test_results()

    #  Enable "Compare AI Results" button after tests complete
    compare_button.config(state=tk.NORMAL)

###  LOGGING FUNCTION
def log_test_results():
    """Logs AI password, passphrase, security test results, and traditional passwords to CSV file."""
    global test_results, generated_password

    #  Ensure the logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)

    if test_results.get("passphrase") in ["UNKNOWN_PHRASE", "ERROR", None, "N/A"]:
        test_results["passphrase"] = load_passphrase()

    #  Ensure GPT test results are stored properly
    test_results["GPT"] = test_results.get("GPT", {})

    #  Retrieve and format Traditional Passwords correctly
    traditional_passwords_list = test_results.get("Traditional_Passwords", [])

    # If missing, extract from 'comparison'
    if not traditional_passwords_list:
        traditional_passwords_list = [
            item["Password"] for item in test_results.get("comparison", []) if item["Type"] == "Traditional"
        ]

    # Convert to string format
    traditional_passwords_str = "; ".join(traditional_passwords_list) if traditional_passwords_list else "N/A"

    #  Ensure Claude's response is not overwritten
    if "Claude" not in test_results:
        test_results["Claude"] = {}

    gpt_attempts_list = test_results["GPT"].get("attempts", [])
    if not gpt_attempts_list or not isinstance(gpt_attempts_list, list):
        gpt_attempts_list = ["No attempts generated"]
    gpt_attempts_str = ", ".join(gpt_attempts_list)

    try:
        print(f"DEBUG: Final passphrase being logged: {test_results['passphrase']}")

        #  Define column headers and their corresponding data mappings
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

        file_exists = os.path.isfile(PASSWORD_RESULT_LOG)

        with open(PASSWORD_RESULT_LOG, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)

            if not file_exists:
                writer.writerow(columns.keys())

            writer.writerow([func() for func in columns.values()])

        print(f" Security test results saved to {PASSWORD_RESULT_LOG}")

    except Exception as e:
        print(f" Error logging test results: {e}")

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
        print(f" Failed to log error: {str(e)}")

def on_login():
    """Handles voice-based login authentication."""
    print(" Step 1: Recording login voice...")
    audio, sr = record_audio()
    
    if audio is not None:
        print(" Step 2: Extracting login voice features...")
        features = extract_audio_features(audio, sr)
        
        print(" Step 3: Verifying voiceprint...")
        if verify_voice(features):
            print(" Voice matched! Checking passphrase...")
            recognized_passphrase = recognize_speech("vocal_input.wav")

            if verify_passphrase(recognized_passphrase):
                print(" Passphrase matched! Now verifying AI-generated password...")
                user_entered_password = simpledialog.askstring("Password Required", "Enter the AI-generated password:")
                
                #  Correct file path for hashed password
                HASHED_PASSWORD_FILE = os.path.join(DATA_DIR, "hashed_password.txt")

                # Check existence clearly
                if not os.path.exists(HASHED_PASSWORD_FILE):
                    print(f" Error: Hashed password file missing at {HASHED_PASSWORD_FILE}")
                    result_label.config(text=" Missing hashed password file.")
                    return
                
                #  Load the stored hashed password
                with open(HASHED_PASSWORD_FILE, "r") as f:
                    stored_hashed_password = f.read().strip()
                #  Hash the user-entered password before comparison
                user_hashed_password = hashlib.sha256(user_entered_password.encode()).hexdigest()

                if user_hashed_password == stored_hashed_password:
                    print(" Access Granted! ")
                    result_label.config(text=" Access Granted! ")
                else:
                    print(" Incorrect AI-generated password. Access Denied.")
                    result_label.config(text=" Incorrect AI-generated password.")
            else:
                print(" Incorrect passphrase. Access Denied.")
                result_label.config(text=" Incorrect passphrase.")
        else:
            print(" Access Denied! Voice does not match.")
            result_label.config(text=" Access Denied! Voice does not match.")
    else:
        print(" Error: Audio capture failed.")
        result_label.config(text=" Error in capturing audio!")

def compare_ai_results():
    """Opens a new window to display AI vs Traditional Password Comparison (Dark Mode)."""
    log_file = os.path.join(LOGS_DIR, "password_result_log.csv")

    if not os.path.exists(log_file):
        messagebox.showerror("Error", "No test results available. Run security tests first.")
        return

    try:
        # Add error handling for CSV file format issues
        try:
            df = pd.read_csv(log_file)
        except pd.errors.ParserError as e:
            messagebox.showerror("Error", "CSV file format has changed or is corrupt.")
            return

        if df.empty:
            messagebox.showerror("Error", "No data found in the log file.")
            return

        # Get the latest test result (last row)
        latest_result = df.iloc[-1]

        # Extract required fields
        ai_password = latest_result.get("AI_Password", "N/A")
        passphrase = latest_result.get("Passphrase", "N/A")
        cl_cracked = latest_result.get("Claude_Cracked", "N/A")
        cl_attempts = latest_result.get("Claude_Attempts", "N/A")
        gpt_cracked = latest_result.get("GPT_Cracked", "N/A")
        gpt_attempts = latest_result.get("GPT_Attempts", "N/A")
        brute_cracked = latest_result.get("Brute_Cracked", "N/A")
        traditional_passwords = latest_result.get("Traditional_Passwords", "N/A")

        # Create dark mode window
        compare_window = tk.Toplevel(app)
        compare_window.title("AI Password Security Results")
        compare_window.geometry("600x500")
        compare_window.configure(bg="#282c34")

        # Header
        tk.Label(compare_window, text=" AI Password Security Results",
                 font=("Helvetica", 16, "bold"), fg="#61dafb", bg="#282c34").pack(pady=10)

        # AI password and passphrase
        for label_text in [
            f" AI Password: {ai_password}",
            f" Passphrase: {passphrase}",
            f" Claude Cracked: {cl_cracked}",
            f" GPT-4 Cracked: {gpt_cracked}",
            f" Brute-Force Cracked: {brute_cracked}",
            f" Traditional Passwords: {traditional_passwords}"
        ]:
            tk.Label(compare_window, text=label_text,
                     font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=2)

        # Claude Attempts section
        tk.Label(compare_window, text=" Claude's Attempts:",
                 font=("Helvetica", 12, "bold"), fg="white", bg="#282c34").pack(pady=5)

        cl_frame = tk.Frame(compare_window, bg="#282c34")
        cl_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        cl_text = tk.Text(cl_frame, height=5, width=60, wrap=tk.WORD,
                          font=("Helvetica", 10), bg="#1e2127", fg="white")
        cl_text.insert(tk.END, cl_attempts)
        cl_text.config(state=tk.DISABLED)
        cl_scrollbar = tk.Scrollbar(cl_frame, command=cl_text.yview)
        cl_text.configure(yscrollcommand=cl_scrollbar.set)
        cl_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        cl_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # GPT Attempts section
        tk.Label(compare_window, text=" GPT-4's Attempts:",
                 font=("Helvetica", 12, "bold"), fg="white", bg="#282c34").pack(pady=5)

        gpt_frame = tk.Frame(compare_window, bg="#282c34")
        gpt_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        gpt_text = tk.Text(gpt_frame, height=5, width=60, wrap=tk.WORD,
                           font=("Helvetica", 10), bg="#1e2127", fg="white")
        gpt_text.insert(tk.END, gpt_attempts)
        gpt_text.config(state=tk.DISABLED)
        gpt_scrollbar = tk.Scrollbar(gpt_frame, command=gpt_text.yview)
        gpt_text.configure(yscrollcommand=gpt_scrollbar.set)
        gpt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        gpt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Close button
        tk.Button(compare_window, text="Close",
                  font=("Helvetica", 12), bg="#61dafb", fg="#282c34",
                  command=compare_window.destroy).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load test results: {e}")

###  UI BUTTON HANDLING
def disable_buttons():
    """Disables test button during automated testing."""
    compare_button.config(state=tk.DISABLED)

#  GUI SETUP
app = tk.Tk()
app.title("Secure AI Password Generator")
app.geometry("600x500")
app.configure(bg="#282c34")

# Custom style for buttons
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14), padding=10)
style.map("TButton", background=[("active", "#61dafb")])

header_label = tk.Label(app, text="Vocal-Based Password Generator", font=("Helvetica", 18, "bold"), fg="#61dafb", bg="#282c34")
header_label.pack(pady=20)

generate_button = ttk.Button(app, text="Generate Password", style="TButton", command=on_generate)
generate_button.pack(pady=10)

# MODIFIED: Use the custom dialog
generate_file_button = ttk.Button(app, text="Generate Audio File Password", style="TButton", command=lambda: show_audio_dialog(app, for_login=False))
generate_file_button.pack(pady=10)

test_button = ttk.Button(app, text="Run Security Tests", style="TButton", state=tk.DISABLED, command=run_security_tests)
test_button.pack(pady=5)

compare_button = ttk.Button(app, text="Compare AI Results", style="TButton", state=tk.DISABLED, command=compare_ai_results)
compare_button.pack(pady=5)

login_button = ttk.Button(app, text="Voice Login", style="TButton", command=on_login)
login_button.pack(pady=10)

# MODIFIED: Use the custom dialog
file_login_button = ttk.Button(app, text="Audio File Login", style="TButton", command=lambda: show_audio_dialog(app, for_login=True))
file_login_button.pack(pady=10)

result_label = tk.Label(app, text="Click 'Generate Password' to begin.", font=("Helvetica", 12), fg="white", bg="#282c34")
result_label.pack(pady=20)

app.mainloop()