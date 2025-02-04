import anthropic
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
anthropic_api_key = os.getenv("CLAUDE_API_KEY")

def ai_crack_password(target_password):
    """Uses AI to predict potential passwords and check if they match the target."""
    if not anthropic_api_key:
        return {"cracked": False, "message": "AI API key missing"}

    client = anthropic.Anthropic(api_key=anthropic_api_key)

    prompt = f"""
You are an AI password cracker. Your task is to generate possible passwords based on common patterns.

A user has entered a password: "{target_password}".  
Generate **exactly 10 possible passwords** that could be similar based on:
- Common substitutions (e.g., 'password' → 'P@ssw0rd')
- Adding special characters
- Using common number sequences
- Mixing uppercase and lowercase letters

Return ONLY a list of possible passwords in a numbered format, with NO extra explanation or text.
"""

    try:
        response = client.completions.create(
            model="claude-2",
            messages=[
                {"role": "system", "content": "You are an AI assistant specialized in password cracking."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )

        # Print and Log AI Response for Debugging
        raw_response = response.completion.strip()
        logging.info(f"AI Response: {raw_response}")
        print("Claude AI Raw Response:", raw_response)  # Debug print

        # Process AI response into a list of guesses
        guesses = raw_response.split("\n")
        attempts = []

        for guess in guesses:
            cleaned_guess = guess.strip().split(".")[-1].strip()  # Remove numbering if present
            if len(cleaned_guess) > 3:  # Ensure it is a valid guess
                attempts.append(cleaned_guess)

        print("AI Generated Attempts:", attempts)  # Debug print

        if target_password in attempts:
            return {
                "cracked": True,
                "message": "AI successfully guessed the password!",
                "guess": target_password,
                "attempts": attempts
            }

        return {
            "cracked": False,
            "message": "AI could not guess the password",
            "attempts": attempts
        }
    except Exception as e:
        logging.error(f"AI Cracking Error: {str(e)}")
        return {"cracked": False, "message": f"AI error: {str(e)}"}
