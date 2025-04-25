import tkinter as tk
from tkinter import filedialog, messagebox
from audio_passwords.account_password_creation import create_password_from_audio
from audio_passwords.account_login import authenticate_with_audio
from audio_passwords.database_control import initialize_db 

initialize_db()

def choose_audio_file(username="default_user", for_login=False):
    """
    Opens a file dialog to select an audio file for processing.
    
    Args:
        username: The username to associate with this file (for account creation) or 
                 to authenticate (for login)
        for_login: If True, authenticate the user; if False, create a new password
    """
    file_path = filedialog.askopenfilename(
        initialdir="/home/cormacgeraghty/Desktop",
        filetypes=[("Audio Files", "*.mp3 *.wav *.flac"), ("All Files", "*.*")]
    )
    
    if file_path:
        if for_login:
            success = authenticate_with_audio(file_path, username)
            if success:
                messagebox.showinfo("Login", f"Login Successful for {username}!")
            else:
                messagebox.showerror("Login", "Login Failed: No matching password found.")
        else:
            message = create_password_from_audio(file_path, username)
            messagebox.showinfo("Password Creation", message)