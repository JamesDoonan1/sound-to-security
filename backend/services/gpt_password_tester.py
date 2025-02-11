from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_password_with_gpt(password, passphrase, voice_features, max_attempts=3):
    """
    Uses GPT-4 to analyze the password based on the spoken passphrase, prompt,
    and extracted voice features to simulate an AI hacker guessing the password.
    """
    prompt = (
        "You are an AI security researcher trying to guess a password based on the given clues.\n"
        "You have access to:\n"
        f"- The user's spoken passphrase: \"{passphrase}\"\n"
        " - The AI prompt that created the password: "
        "\"Generate a secure 12-character password based on the spoken passphrase and extracted voice features.\"\n"
        f"- Extracted voice features:\n"
        f"  - MFCC Mean: {voice_features['mfcc']}\n"
        f"  - Spectral Centroid: {voice_features['spectral_centroid']}\n"
        f"  - Tempo: {voice_features['tempo']}\n\n"
        "Your task:\n"
        "1. Analyze the spoken passphrase for common password structures.\n"
        "2. Generate up to 5 likely password variations based on secure password trends.\n"
        "3. Try to mimic an AI-generated password using uppercase, lowercase, numbers, and special characters.\n"
        "4. Return ONLY the list of password guesses (NO explanations).\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7
        )
        
        # Extract response
        gpt_guesses = response.choices[0].message.content.strip().split("\n")

        print(f"🔍 GPT Generated Password Guesses: {gpt_guesses}")

        if password in gpt_guesses:
            return {
                "cracked": True,
                "attempts": gpt_guesses,
                "message": "GPT successfully guessed the password."
            }
        return {
            "cracked": False,
            "attempts": gpt_guesses,
            "message": "GPT failed to guess the password."
        }
        
    except Exception as e:
        print(f"❌ GPT API Error: {e}")
        return {
            "cracked": False,
            "attempts": [],
            "message": f"GPT error: {e}"
        }

