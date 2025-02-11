import openai
import os
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def test_password_with_gpt(password, max_attempts=3):
    """
    Uses GPT-4 Turbo to attempt cracking the given password.
    Returns whether GPT-4 successfully guessed the password.
    """
    prompt = (
        "You are an advanced AI trained in security and password analysis. "
        "You must attempt to guess the following password based on common structures, "
        "patterns, and weaknesses. Do NOT use brute force but rather predict the password "
        "intelligently using pattern recognition and AI inference.\n\n"
        f"Target Password: {password}\n"
        "Generate a list of up to 5 potential passwords that a hacker might guess."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.8,
            api_key=openai_api_key,
        )

        guesses = response["choices"][0]["message"]["content"].strip().split("\n")
        print(f"🔍 GPT-4 Generated Password Guesses: {guesses}")

        # Check if GPT guessed correctly
        if password in guesses:
            return True, guesses
        return False, guesses

    except Exception as e:
        print(f"❌ Error with GPT-4 API: {e}")
        return False, []

