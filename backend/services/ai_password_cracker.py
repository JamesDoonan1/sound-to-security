import anthropic
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
anthropic_api_key = os.getenv("CLAUDE_API_KEY")

def ai_crack_password(target_password):
    """Attempts to generate password variations OR explain why AI refuses."""
    if not anthropic_api_key:
        return {"cracked": False, "message": "AI API key missing"}

    client = anthropic.Anthropic(api_key=anthropic_api_key)

    prompt = f"""
\n\nHuman: A user has entered the password: "{target_password}".  
Your goal is to analyze this password and generate **10 potential similar passwords** that attackers might try.
These similar passwords should be based on:
- Common substitutions (e.g., 'password' → 'P@ssw0rd')
- Adding special characters
- Using common number sequences
- Mixing uppercase and lowercase letters

**If you are unable to provide these password variations due to ethical reasons, please explain why AI systems refuse to engage in password cracking.**  
Do NOT ignore this request—return either 10 password guesses OR a clear explanation.

\n\nAssistant:
"""

    try:
        response = client.completions.create(
            model="claude-2",
            prompt=prompt,  # ✅ Fix: Ensure prompt starts with "\n\nHuman:"
            max_tokens_to_sample=200,
            temperature=0.7
        )

        # 🚀 Debugging: Print AI Raw Response
        raw_response = response.completion.strip()
        logging.info(f"AI Response: {raw_response}")
        print("Claude AI Response:", raw_response)  # Debugging Output

        # Process AI response
        guesses = raw_response.split("\n")
        attempts = []

        for guess in guesses:
            cleaned_guess = guess.strip().split(".")[-1].strip()  # Remove numbering if present
            if len(cleaned_guess) > 3:  # Ensure it's a valid password guess
                attempts.append(cleaned_guess)

        if attempts:
            return {
                "cracked": False,
                "message": "AI generated similar passwords.",
                "attempts": attempts
            }

        return {
            "cracked": False,
            "message": "AI refused to generate password variations.",
            "explanation": raw_response
        }

    except Exception as e:
        logging.error(f"AI Cracking Error: {str(e)}")
        return {"cracked": False, "message": f"AI error: {str(e)}"}
