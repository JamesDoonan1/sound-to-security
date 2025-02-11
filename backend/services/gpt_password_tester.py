from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_password_with_gpt(password, max_attempts=3):
    """
    Uses GPT-4 to attempt analyzing the given password.
    Returns whether GPT-4 successfully identified potential variations.
    """
    prompt = (
        "You are an AI trained in cybersecurity. Your goal is to analyze the given password "
        "and generate up to 5 possible variations a hacker might try based on common substitutions, "
        "patterns, and common words.\n\n"
        f"Password to analyze: {password}\n"
        "Provide only the list of password guesses."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Note: "gpt-4-turbo" isn't a valid model name
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7
        )
        
        # Parse the response - in the new API, we access the content differently
        gpt_response = response.choices[0].message.content.strip().split("\n")
        
        print(f"🔍 GPT Generated Password Guesses: {gpt_response}")
        
        if password in gpt_response:
            return {
                "cracked": True,
                "attempts": gpt_response,
                "message": "GPT successfully guessed the password."
            }
        return {
            "cracked": False,
            "attempts": gpt_response,
            "message": "GPT failed to guess the password."
        }
        
    except Exception as e:
        print(f"❌ GPT API Error: {e}")
        return {
            "cracked": False,
            "attempts": [],
            "message": f"GPT error: {e}"
        }

# Example usage
if __name__ == "__main__":
    test_password = "Password123!"
    result = test_password_with_gpt(test_password)
    print(f"\nTesting password security with GPT-4...\n✅ GPT Response: {result}")