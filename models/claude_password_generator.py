import anthropic
import os
import time
import csv
from dotenv import load_dotenv


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/data"))
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/logs"))  
PASSWORD_LOG_FILE = os.path.join(LOGS_DIR, "password_log.csv")

# Load environment variables
load_dotenv()
anthropic_api_key = os.getenv("CLAUDE_API_KEY")


def log_password(password, status):
    """Logs generated passwords and validation status to a CSV file."""
    os.makedirs(LOGS_DIR, exist_ok=True)  #  Ensure `logs/` exists

    with open(PASSWORD_LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not os.path.isfile(PASSWORD_LOG_FILE):
            writer.writerow(["Generated Password", "Valid"])

        writer.writerow([password, status])

def generate_password_with_claude(features, passphrase="", max_retries=5):
    """Generate a secure password using Claude AI based on extracted features and a passphrase."""
    print("Step 4: Sending features to Claude for password generation...")

    prompt = (
        f"The following are features extracted from a vocal recording: {features}.\n"
        f"The user has also provided a passphrase: \"{passphrase}\".\n"
        "**Generate a strong password based on these inputs.**\n"
        "The password must:\n"
        "- Be exactly **12 characters long**\n"
        "- Include **uppercase, lowercase, numbers, and symbols**\n"
        "- **Avoid dictionary words**\n\n"
        "**Return ONLY the password with NO explanation.**"
    )

    client = anthropic.Anthropic(api_key=anthropic_api_key)

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-2",
                max_tokens=20,
                temperature=0.7,
                system="You are an AI that generates strong passwords. Return ONLY the password.",
                messages=[{"role": "user", "content": prompt}]
            )

            if isinstance(response.content, list):
                password = "".join([block.text for block in response.content]).strip()
            else:
                password = str(response.content).strip()

            #  Validate and log password
            if validate_password(password):
                print(f" Generated Valid Password: {password}")
                log_password(password, "Valid")
                return password

            print(f" Invalid password format received: {password}. Retrying...")
            log_password(password, "Invalid")

        except anthropic.APIError as e:
            print(f" Claude API Error: {e}")

            if "overloaded_error" in str(e):
                print(f" Claude is overloaded. Retrying {attempt + 1}/{max_retries} in 5 seconds...")
                time.sleep(5)
            else:
                return "Error: Could not generate password."

    return "Error: Claude AI is currently unavailable. Try again later."

def validate_password(password):
    """Ensures the password meets all security criteria."""
    return (
        len(password) == 12
        and any(c.islower() for c in password)
        and any(c.isupper() for c in password)
        and any(c.isdigit() for c in password)
        and any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password)
    )
