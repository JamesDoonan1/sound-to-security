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
        response = client.messages.create(
            model="claude-2",
            max_tokens=200,
            temperature=0.7,
            system="You are an AI that evaluates password security. Provide either password guesses OR a reason why AI does not generate them.",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract text properly
        if isinstance(response.content, list):
            raw_response = " ".join([block.text for block in response.content]).strip()
        else:
            raw_response = str(response.content).strip()

        logging.info(f"Claude AI Response: {raw_response}")
        print("Claude AI Response:", raw_response)  # Debugging Output

        # If AI provides an ethical refusal message
        if "refuse" in raw_response.lower() or "ethical" in raw_response.lower():
            return {
                "cracked": False,
                "message": "AI refused to generate password variations.",
                "explanation": raw_response
            }

        # Otherwise, extract password guesses
        guesses = raw_response.split("\n")
        attempts = [guess.strip() for guess in guesses if len(guess.strip()) > 3]

        return {
            "cracked": False,
            "message": "AI generated similar passwords.",
            "attempts": attempts
        } if attempts else {
            "cracked": False,
            "message": "Claude did not generate usable passwords.",
            "explanation": raw_response
        }

    except Exception as e:
        logging.error(f"AI Cracking Error: {str(e)}")
        return {"cracked": False, "message": f"Claude AI error: {str(e)}"}
