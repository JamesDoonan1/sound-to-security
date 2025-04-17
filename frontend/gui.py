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

# Paths for stored data
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)  
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

    try:
        # Append to the file (keeps history of all passwords)
        with open(HASHED_PASSWORD_FILE, "a", encoding="utf-8") as f:  
            f.write(hashed_password + "\n")
        
        print(f" Hashed password saved successfully at {HASHED_PASSWORD_FILE}")

    except Exception as e:
        print(f" Error saving hashed password: {e}")

    # Store hashed password in `test_results`
    global test_results
    test_results["hashed_password"] = hashed_password

    print(f" Hashed AI Password: {hashed_password}")
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

        print("Step 3: Recognising spoken passphrase...")
        passphrase = recognize_speech("vocal_input.wav")

        if not passphrase:
            messagebox.showerror("Error", "Could not detect a passphrase. Try again.")
            return

        print(f"Recognised Passphrase: {passphrase}")
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
            
            hashed_password = save_hashed_password(generated_password)
            test_results["hashed_password"] = hashed_password  #  Store in test results

                        #  Update UI
            result_label.config(text=f" AI Password: {generated_password}\n\n Password generated successfully! Click 'Run Security Tests' to evaluate.")

            #  Enable the test button after password generation
            test_button.config(state=tk.NORMAL)
            compare_button.config(state=tk.DISABLED)  # Keep compare button disabled until tests are run


        else:
            print(" Error: Failed to generate password.")
            result_label.config(text=" Error generating password!")

    else:
        print(" Error: Audio capture failed.")
        result_label.config(text=" Error in capturing audio!")


# Add a flag to prevent double execution of security tests

security_tests_in_progress = False

def run_security_tests():
    """Runs all security tests after password generation."""
    global generated_password, test_results, security_tests_in_progress

    # If already processing, ignore the second call
    if security_tests_in_progress:
        print(" Security tests already in progress, ignoring duplicate call")
        return
        
    # Set flag to indicate tests are running
    security_tests_in_progress = True

    if not generated_password:
        messagebox.showerror("Error", "No password available to test. Generate a password first.")
        security_tests_in_progress = False  # Reset flag before returning
        return

    if "Traditional_Passwords" not in test_results:
         test_results["Traditional_Passwords"] = []

    print(" Running security tests...")
    result_label.config(text="🔍 Running security tests... This may take a few moments.")
    
    # Update UI to indicate tests are running
    test_button.config(state=tk.DISABLED)

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
    
    time.sleep(1)
    
    #  Hashcat MD5 Test
    try:
        # Hash the password with MD5 for Hashcat testing
        password_hash = hashlib.md5(generated_password.encode()).hexdigest()
        
        # Call the Hashcat API endpoint
        response = requests.post(
            "http://127.0.0.1:5000/api/test-password-hashcat", 
            json={
                "password_hash": password_hash,
                "hash_type": "0",  # MD5
                "attack_mode": "3"  # Brute-force
            }
        )
        
        response.raise_for_status()
        hashcat_result = response.json()
        
        test_results["Hashcat_MD5"] = {
            "cracked": hashcat_result.get("cracked", False),
            "result": hashcat_result.get("result", "N/A"),
            "hash": password_hash
        }
        
        print(f" Hashcat MD5 Test Result: {hashcat_result}")
        
    except requests.RequestException as e:
        print(f" Hashcat Testing Error: {e}")
        test_results["Hashcat_MD5"] = {
            "cracked": "Error", 
            "result": f"Error: {str(e)}", 
            "hash": hashlib.md5(generated_password.encode()).hexdigest()
        }

    time.sleep(1)

    #  Hashcat SHA-256 Test
    try:
        # Also test with SHA-256
        password_hash = hashlib.sha256(generated_password.encode()).hexdigest()
        
        response = requests.post(
            "http://127.0.0.1:5000/api/test-password-hashcat", 
            json={
                "password_hash": password_hash,
                "hash_type": "1400",  # SHA-256
                "attack_mode": "3"  # Brute-force
            }
        )
        
        response.raise_for_status()
        hashcat_result = response.json()
        
        test_results["Hashcat_SHA256"] = {
            "cracked": hashcat_result.get("cracked", False),
            "result": hashcat_result.get("result", "N/A"),
            "hash": password_hash
        }
        
        print(f" Hashcat SHA-256 Test Result: {hashcat_result}")
        
    except requests.RequestException as e:
        print(f" Hashcat SHA-256 Testing Error: {e}")
        test_results["Hashcat_SHA256"] = {
            "cracked": "Error", 
            "result": f"Error: {str(e)}", 
            "hash": hashlib.sha256(generated_password.encode()).hexdigest()
        }

    #  Log results
    log_test_results()

    #  Update UI after tests complete
    result_label.config(text=f" AI Password: {generated_password}\n Security tests completed. Click 'Compare AI Results' to view details.")
    test_button.config(state=tk.NORMAL)  # Re-enable the test button
    compare_button.config(state=tk.NORMAL)  # Enable the compare button after tests complete
    
    # Reset the flag when tests are complete
    security_tests_in_progress = False

def log_test_results():
    """Logs AI password, passphrase, security test results, and traditional passwords to CSV file."""
    global test_results, generated_password

    #  Ensure hashed password exists in `test_results`
    if "hashed_password" not in test_results or not test_results["hashed_password"]:
        print(" WARNING: Hashed password missing from test_results! Setting to N/A.")
        test_results["hashed_password"] = "N/A"

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
        print(f" Final passphrase being logged: {test_results['passphrase']}")

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
            "Traditional_Passwords": lambda: traditional_passwords_str,
            "Hashed Password": lambda: test_results.get("hashed_password", "N/A"),
            "Hashcat_MD5_Cracked": lambda: test_results.get("Hashcat_MD5", {}).get("cracked", "N/A"),
            "Hashcat_MD5_Result": lambda: test_results.get("Hashcat_MD5", {}).get("result", "N/A"),
            "Hashcat_MD5_Hash": lambda: test_results.get("Hashcat_MD5", {}).get("hash", "N/A"),
            "Hashcat_SHA256_Cracked": lambda: test_results.get("Hashcat_SHA256", {}).get("cracked", "N/A"),
            "Hashcat_SHA256_Result": lambda: test_results.get("Hashcat_SHA256", {}).get("result", "N/A"),
            "Hashcat_SHA256_Hash": lambda: test_results.get("Hashcat_SHA256", {}).get("hash", "N/A")
             
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
                
                if not user_entered_password:
                    print("Password entry canceled")
                    result_label.config(text=" Password entry canceled.")
                    return
                
                # Correct file path for hashed password
                HASHED_PASSWORD_FILE = os.path.join(DATA_DIR, "hashed_password.txt")

                # Check existence clearly
                if not os.path.exists(HASHED_PASSWORD_FILE):
                    print(f" Error: Hashed password file missing at {HASHED_PASSWORD_FILE}")
                    result_label.config(text=" Missing hashed password file.")
                    return
                
                try:
                    # Load the stored hashed password(s)
                    with open(HASHED_PASSWORD_FILE, "r") as f:
                        # Read all hashed passwords from the file (there may be multiple)
                        stored_hashed_passwords = [line.strip() for line in f.readlines() if line.strip()]
                    
                    if not stored_hashed_passwords:
                        print(" Error: No stored hashed passwords found in file")
                        result_label.config(text=" No stored passwords found. Please generate a password first.")
                        return
                    
                    # Get the most recent hashed password (last one in the file)
                    most_recent_hash = stored_hashed_passwords[-1]
                    
                    # Hash the user-entered password before comparison
                    user_hashed_password = hashlib.sha256(user_entered_password.encode()).hexdigest()

                    if user_hashed_password == most_recent_hash:
                        print(" Access Granted! ")
                        result_label.config(text=" Access Granted! ")
                    else:
                        print(" Incorrect AI-generated password. Access Denied.")
                        result_label.config(text=" Incorrect AI-generated password.")
                except Exception as e:
                    print(f" Error during password verification: {e}")
                    result_label.config(text=f" Error: {str(e)}")
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
    """Opens a new window to display AI vs Traditional Password Comparison."""
    log_file = os.path.join(LOGS_DIR, "password_result_log.csv")

    if not os.path.exists(log_file):
        messagebox.showerror("Error", "No test results available. Run security tests first.")
        return

    try:
        # Add error handling for CSV file format issues
        try:
            df = pd.read_csv(log_file)
        except pd.errors.ParserError as e:
            messagebox.showerror("Error", "CSV file format has changed. Creating a backup for historical data.")
            
            # Rename the old file for backup
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            backup_file = os.path.join(LOGS_DIR, f"password_result_log_backup_{timestamp}.csv")
            os.rename(log_file, backup_file)
            
            messagebox.showinfo("Info", f"Old data backed up to {backup_file}\nPlease run a new test to generate updated results.")
            return

        if df.empty:
            messagebox.showerror("Error", "No data found in the log file.")
            return

        # Get the latest test result (last row)
        latest_result = df.iloc[-1]

        # Extract only the requested fields with error handling
        try:
            ai_password = latest_result["AI_Password"]
            passphrase = latest_result["Passphrase"]
            cl_attempts = latest_result["Claude_Attempts"]
            gpt_cracked = latest_result["GPT_Cracked"]
            gpt_attempts = latest_result["GPT_Attempts"]
        except KeyError as e:
            messagebox.showerror("Error", f"Missing field in results: {e}")
            return

        # Create a new Tkinter window to display results
        compare_window = tk.Toplevel(app)
        compare_window.title("AI Password Security Results")
        compare_window.geometry("600x400")
        compare_window.configure(bg="#282c34")

        # Add a header
        tk.Label(compare_window, text=" AI Password Security Results", 
                font=("Helvetica", 16, "bold"), fg="#61dafb", bg="#282c34").pack(pady=10)
        
        # Display the selected fields
        tk.Label(compare_window, text=f" AI Password: {ai_password}", 
                font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=5)
        
        tk.Label(compare_window, text=f" Passphrase: {passphrase}", 
                font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=5)
        
        # Claude attempts section with scrolling text area for longer outputs
        tk.Label(compare_window, text=" Claude's Attempts:", 
                font=("Helvetica", 12, "bold"), fg="white", bg="#282c34").pack(pady=5)
                
        cl_attempts_frame = tk.Frame(compare_window, bg="#282c34")
        cl_attempts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        cl_attempts_text = tk.Text(cl_attempts_frame, height=5, width=60, 
                                  wrap=tk.WORD, font=("Helvetica", 10),
                                  bg="#1e2127", fg="white")
        cl_attempts_text.insert(tk.END, cl_attempts)
        cl_attempts_text.config(state=tk.DISABLED)  # Make read-only
        
        cl_scrollbar = tk.Scrollbar(cl_attempts_frame, command=cl_attempts_text.yview)
        cl_attempts_text.configure(yscrollcommand=cl_scrollbar.set)
        
        cl_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        cl_attempts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # GPT section
        tk.Label(compare_window, text=f" GPT-4 Cracked: {gpt_cracked}", 
                font=("Helvetica", 12), fg="white", bg="#282c34").pack(pady=5)
        
        # GPT attempts with scrolling text
        tk.Label(compare_window, text=" GPT's Attempts:", 
                font=("Helvetica", 12, "bold"), fg="white", bg="#282c34").pack(pady=5)
                
        gpt_attempts_frame = tk.Frame(compare_window, bg="#282c34")
        gpt_attempts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        gpt_attempts_text = tk.Text(gpt_attempts_frame, height=5, width=60, 
                                  wrap=tk.WORD, font=("Helvetica", 10),
                                  bg="#1e2127", fg="white")
        gpt_attempts_text.insert(tk.END, gpt_attempts)
        gpt_attempts_text.config(state=tk.DISABLED)  # Make read-only
        
        gpt_scrollbar = tk.Scrollbar(gpt_attempts_frame, command=gpt_attempts_text.yview)
        gpt_attempts_text.configure(yscrollcommand=gpt_scrollbar.set)
        
        gpt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        gpt_attempts_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Link to CSV file
        tk.Label(compare_window, text="For complete results, see CSV file:", 
                font=("Helvetica", 10), fg="#61dafb", bg="#282c34").pack(pady=5)
        tk.Label(compare_window, text=log_file, 
                font=("Helvetica", 9), fg="white", bg="#282c34").pack()
        
        # Close button
        tk.Button(compare_window, text="Close", 
                font=("Helvetica", 12), bg="#61dafb", fg="#282c34",
                command=compare_window.destroy).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load test results: {e}")
###  UI BUTTON HANDLING
def disable_buttons():
    """Disables test button during automated testing."""
    test_button.config(state=tk.DISABLED)
    compare_button.config(state=tk.DISABLED)

#  GUI SETUP
app = tk.Tk()
app.title("Secure AI Password Generator")
app.geometry("600x500")
app.configure(bg="#282c34")


# Initialize global state flags
password_generation_in_progress = False
security_tests_in_progress = False

# Custom style for buttons
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14), padding=10)
style.map("TButton", background=[("active", "#61dafb")])

header_label = tk.Label(app, text="Vocal-Based Password Generator", font=("Helvetica", 18, "bold"), fg="#61dafb", bg="#282c34")
header_label.pack(pady=20)

# Add a flag to prevent double execution
password_generation_in_progress = False

def safe_on_generate():

    """Wrapper for on_generate to prevent double execution"""

    global password_generation_in_progress
    # If already processing, ignore the second call
    if password_generation_in_progress:
        print(" Generation already in progress, ignoring duplicate call")
        return     

    try:

        # Set flag to indicate processing is happening
        password_generation_in_progress = True

        # Disable button during generation to prevent multiple clicks
        generate_button.config(state=tk.DISABLED)
        # Call the actual function
        on_generate()

    finally:

        # Reset flag when done (even if there was an error)
        password_generation_in_progress = False
        # Re-enable button
        generate_button.config(state=tk.NORMAL)

generate_button = ttk.Button(app, text="Generate Password", style="TButton", command=safe_on_generate)
generate_button.pack(pady=10)

test_button = ttk.Button(app, text="Run Security Tests", style="TButton", state=tk.DISABLED, command=run_security_tests)
test_button.pack(pady=5)

compare_button = ttk.Button(app, text="Compare AI Results", style="TButton", state=tk.DISABLED, command=compare_ai_results)
compare_button.pack(pady=5)

login_button = ttk.Button(app, text="Login", style="TButton", command=on_login)
login_button.pack(pady=10)

result_label = tk.Label(app, text="Click 'Generate Password' to begin.", font=("Helvetica", 12), fg="white", bg="#282c34")
result_label.pack(pady=20)

app.mainloop()