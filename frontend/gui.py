import time  
import tkinter as tk
import requests
from tkinter import messagebox
from vocal_passwords.voice_processing import record_audio
from vocal_passwords.feature_extraction import extract_audio_features
from models.claude_password_generator import generate_password_with_claude

# Global variable to store the generated password
generated_password = None  

def on_generate():
    """Handles the process of generating a password from voice input."""
    global generated_password  

    print("Step 1: Starting audio capture...")
    audio, sr = record_audio()
    
    if audio is not None:
        print("Step 2: Audio captured successfully. Proceeding to feature extraction...")
        features = extract_audio_features(audio, sr)
        print(f"Extracted features: {features}")

        print("Step 3: Generating password using Claude...")
        generated_password = generate_password_with_claude(features)

        if "Error" not in generated_password:
            print("Step 4: Password generation complete!")
            result_label.config(text=f"Generated Password:\n{generated_password}")
            test_button.config(state=tk.NORMAL)  # Enable the "Test Password" button
        else:
            print("Error: Failed to generate password.")
            result_label.config(text="Error in generating password!")
    else:
        print("Error: Audio capture failed.")
        result_label.config(text="Error in capturing audio!")

def on_test_password():
    """Handles testing the generated password for security with real-time AI updates."""
    global generated_password

    if not generated_password:
        messagebox.showerror("Error", "No password available to test.")
        return

    print("Step 5: Testing the generated password...")
    result_label.config(text="Testing password strength... Please wait.")

    try:
        url = "http://127.0.0.1:5000/api/test-password"
        response = requests.post(url, json={"password": generated_password})
        response.raise_for_status()
        result = response.json()

        # Create a pop-up window to show AI guesses dynamically
        ai_window = tk.Toplevel(app)
        ai_window.title("AI Cracking Process")
        ai_window.geometry("500x400")
        ai_window.configure(bg="#1e1e1e")

        # Add a label for progress
        progress_label = tk.Label(
            ai_window,
            text="AI is trying to guess your password...",
            font=("Helvetica", 14, "bold"),
            fg="#61dafb",
            bg="#1e1e1e"
        )
        progress_label.pack(pady=10)

        # Frame for AI response
        frame = tk.Frame(ai_window, bg="#282c34", bd=2, relief="ridge")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable AI Response Box
        ai_attempts_box = tk.Text(
            frame,
            font=("Helvetica", 12),
            height=10,
            width=55,
            wrap="word",
            bg="#1e1e1e",
            fg="white",
            bd=0
        )
        ai_attempts_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Add scrollbar
        scrollbar = tk.Scrollbar(frame, command=ai_attempts_box.yview)
        scrollbar.pack(side="right", fill="y")
        ai_attempts_box.config(yscrollcommand=scrollbar.set)

        # Get AI guesses from the response safely
        ai_attack_results = result.get("ai_attack", {})
        ai_attempts = ai_attack_results.get("attempts", [])
        explanation = ai_attack_results.get("explanation", "")

        if ai_attempts:
            ai_attempts_box.insert(tk.END, "🔍 AI Generated These Password Variations:\n\n", "bold")
            for attempt in ai_attempts:
                ai_attempts_box.insert(tk.END, f"🔹 {attempt}\n")
        elif explanation:
            ai_attempts_box.insert(tk.END, "⚠️ AI Refusal Message:\n\n", "bold")
            ai_attempts_box.insert(tk.END, explanation)

        ai_attempts_box.config(state="disabled")  # Make text read-only

        # Display final results
        test_results = f"""
        🛡️ Brute Force:
          🔸 Cracked: {result['brute_force']['cracked']}
          🔸 Message: {result['brute_force'].get('message', '')}
          🔸 Time Taken: {result['brute_force'].get('time_taken', 'N/A')} seconds

        📖 Dictionary Attack:
          🔸 Cracked: {result['dictionary_attack']['cracked']}
          🔸 Message: {result['dictionary_attack'].get('message', '')}

        🤖 AI Attack:
          🔸 Cracked: {ai_attack_results.get('cracked', False)}
          🔸 Message: {ai_attack_results.get('message', '')}
          🔸 Guess: {ai_attack_results.get('guess', 'N/A')}
        """

        result_label.config(text=test_results)

    except requests.RequestException as e:
        print(f"Error during password testing: {e}")
        result_label.config(text="Error in testing password!")

# Create main app window
app = tk.Tk()
app.title("Secure Melody-Based Password Generator")
app.geometry("500x400")
app.configure(bg="#282c34")  # Set background color

# Header
header_label = tk.Label(
    app,
    text="Vocal-Based Password Generator",
    font=("Helvetica", 18, "bold"),
    fg="#61dafb",
    bg="#282c34"
)
header_label.pack(pady=20)

# Generate Button
generate_button = tk.Button(
    app,
    text="Generate Password",
    font=("Helvetica", 14),
    bg="#61dafb",
    fg="#282c34",
    activebackground="#21a1f1",
    activeforeground="white",
    command=on_generate
)
generate_button.pack(pady=10)

# Test Button (Initially Disabled)
test_button = tk.Button(
    app,
    text="Test This Password",
    font=("Helvetica", 14),
    bg="#61dafb",
    fg="#282c34",
    activebackground="#21a1f1",
    activeforeground="white",
    command=on_test_password,
    state=tk.DISABLED  # Disabled until a password is generated
)
test_button.pack(pady=10)

# Result Label
result_label = tk.Label(
    app,
    text="Click 'Generate Password' to begin.",
    font=("Helvetica", 12),
    fg="white",
    bg="#282c34",
    wraplength=400,
    justify="center"
)
result_label.pack(pady=20)

# Footer
footer_label = tk.Label(
    app,
    text="Developed by James Doonan",
    font=("Helvetica", 10),
    fg="gray",
    bg="#282c34"
)
footer_label.pack(side="bottom", pady=10)

# Start the main event loop
app.mainloop()
