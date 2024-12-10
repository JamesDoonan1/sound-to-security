import tkinter as tk
from vocal_passwords.voice_processing import record_audio
from vocal_passwords.feature_extraction import extract_audio_features
from models.claude_password_generator import generate_password_with_claude

def on_generate():
    print("\nStep 1: Starting audio capture...")
    audio, sr = record_audio()
    if audio is not None:
        print("\nStep 2: Audio captured successfully. Proceeding to feature extraction...")
        features = extract_audio_features(audio, sr)
        print(f"Extracted features: {features}")
        
        print("\nStep 3: Generating password using Claude...")
        password = generate_password_with_claude(features)
        
        if "Error" not in password:
            print("\nStep 4: Password generation complete!")
            result_label.config(text=f"Generated Password:\n{password}")
        else:
            print("\nError: Failed to generate password.")
            result_label.config(text="Error in generating password!")
    else:
        print("\nError: Audio capture failed.")
        result_label.config(text="Error in capturing audio!")

# Create main app window
app = tk.Tk()
app.title("Secure Melody-Based Password Generator")
app.geometry("500x300")
app.configure(bg="#282c34")  # Set background color

# Header
header_label = tk.Label(
    app,
    text="Melody-Based Password Generator",
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

# Result Label
result_label = tk.Label(
    app,
    text="Click 'Generate Password' and sing or hum for 5 seconds.",
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
