import anthropic
import os
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
anthropic_api_key = os.getenv("CLAUDE_API_KEY")

def generate_password_with_claude(features, passphrase="", max_retries=5):
    """Generate a secure password using Claude AI based on extracted features and a passphrase."""
    print("Step 4: Sending features to Claude for password generation...")

    prompt = (
        f"The following are features extracted from a vocal recording: {features}.\n"
        f"The user has also provided a passphrase: \"{passphrase}\".\n"
        "**Generate a strong password based on these inputs.**\n"
        "The password must:\n"
        "- Be exactly **12 characters long** (not shorter, not longer)\n"
        "- Include **at least one uppercase letter**\n"
        "- Include **at least one lowercase letter**\n"
        "- Include **at least one number**\n"
        "- Include **at least one special symbol** (!@#$%^&*()_+-=[]{}|;:,.<>?/)\n"
        "- **Do NOT include dictionary words or phrases**\n\n"
        "**Return ONLY the password with NO explanation or extra text.**"
    )

    client = anthropic.Anthropic(api_key=anthropic_api_key)

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-2",
                max_tokens=20,
                temperature=0.7,
                system="You are an AI that generates strong, secure passwords. Return ONLY a valid password.",
                messages=[{"role": "user", "content": prompt}]
            )

            # ✅ Extract password correctly
            if isinstance(response.content, list):
                password = "".join([block.text for block in response.content]).strip()
            else:
                password = str(response.content).strip()

            # ✅ Validate password format
            if validate_password(password):
                print(f"✅ Generated Valid Password: {password}")
                return password

            print(f"⚠️ Invalid password format received: {password}. Retrying...")

        except anthropic.APIError as e:
            print(f"❌ Claude API Error: {e}")

            if "overloaded_error" in str(e):
                print(f"⚠️ Claude is overloaded. Retrying {attempt + 1}/{max_retries} in 5 seconds...")
                time.sleep(5)
            else:
                return "Error: Could not generate password."

    return "Error: Claude AI is currently unavailable. Try again later."

def validate_password(password):
    """Ensures the password meets all security criteria."""
    return (
        len(password) == 12
        and any(c.islower() for c in password)  # At least one lowercase
        and any(c.isupper() for c in password)  # At least one uppercase
        and any(c.isdigit() for c in password)  # At least one number
        and any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password)  # At least one symbol
    )
