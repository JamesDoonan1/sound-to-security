import anthropic
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API key securely
anthropic_api_key = os.getenv("CLAUDE_API_KEY")

def generate_password_with_claude(features, passphrase="", max_retries=3):
    """Generate a password using Claude AI based on extracted features and a passphrase."""
    print("Step 4: Sending features to Claude for password generation...")

    prompt = (
        f"The following are features extracted from a vocal recording: {features}.\n"
        f"The user has also provided a passphrase: \"{passphrase}\".\n"
        "Generate a **secure, unique password** based on these inputs. The password must:\n"
        "- Be at least **12 characters long**\n"
        "- Include **uppercase, lowercase, numbers, and symbols**\n"
        "- **Avoid common dictionary words**\n\n"
        "**Return only the password with no explanation or additional text.**"
    )

    client = anthropic.Anthropic(api_key=anthropic_api_key)

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-2",
                max_tokens=20,
                temperature=0.7,
                system="You are a security AI that generates strong passwords.",
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract text from Claude's response properly
            if isinstance(response.content, list):  
                password = " ".join([block.text for block in response.content]).strip()  # Convert list of TextBlocks to string
            else:
                password = str(response.content).strip()

            print(f"✅ Generated Password: {password}")

            if "Unfortunately" in password or len(password) < 8:
                return "Error: AI failed to generate a valid password."

            return password

        except anthropic.APIError as e:
            print(f"❌ Claude API Error: {e}")

            # Handle overload error specifically
            if "overloaded_error" in str(e):
                print(f"⚠️ Claude is overloaded. Retrying {attempt + 1}/{max_retries} in 5 seconds...")
                time.sleep(5)  # Wait before retrying
            else:
                return "Error: Could not generate password."

    return "Error: Claude AI is currently unavailable. Try again later."
