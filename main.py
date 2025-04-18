import tkinter as tk
from frontend.gui import on_generate

def main():
    """Main entry point for the application."""
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
        command=on_generate  # Call the function from gui.py
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


if __name__ == "__main__":
    main()
