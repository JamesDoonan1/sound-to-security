import tkinter as tk
from tkinter import filedialog, messagebox
from audio_passwords.account_password_creation import create_password_from_audio
from audio_passwords.account_login import authenticate_with_audio

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
