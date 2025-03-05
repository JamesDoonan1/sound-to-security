import tkinter as tk
from tkinter import filedialog, messagebox
from account_password_creation import create_password_from_audio
from account_login import authenticate_with_audio

def choose_audio_file(for_login=False):
    """Opens a file dialog to select an audio file for processing."""
    file_path = filedialog.askopenfilename(
        initialdir="/home/cormacgeraghty/Desktop",  # Force it to open in Desktop
        filetypes=[("All Files", "*.*")]
    )


    if file_path:
        if for_login:
            success = authenticate_with_audio(file_path)
            if success:
                messagebox.showinfo("Login", "Login Successful!")
            else:
                messagebox.showerror("Login", "Login Failed: No matching password found.")
        else:
            message = create_password_from_audio(file_path)
            messagebox.showinfo("Password Creation", message)

# GUI Setup
app = tk.Tk()
app.title("Audio-Based Authentication")
app.geometry("400x250")

tk.Label(app, text="Audio-Based Authentication System", font=("Helvetica", 14, "bold")).pack(pady=20)
tk.Button(app, text="Select Audio for Password Creation", command=lambda: choose_audio_file(False)).pack(pady=10)
tk.Button(app, text="Select Audio for Login", command=lambda: choose_audio_file(True)).pack(pady=10)

app.mainloop()
