from openai import OpenAI
import os
from dotenv import load_dotenv
import time,json
import time
import json

# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def test_password_with_gpt(password, passphrase, voice_features, max_attempts=5):
    """
    Enhanced GPT password testing with better structure and logging.
    """
    start_time = time.time()
    
    # Format voice features for prompt
    features_str = (
        f"MFCC (vocal tone): {voice_features['mfcc']:.2f}\n"
        f"Spectral Centroid (voice brightness): {voice_features['spectral_centroid']:.2f}\n"
        f"Speech Tempo: {voice_features['tempo']:.2f} BPM"
    )
    
    # Construct a more focused prompt
    prompt = f"""You are analyzing a voice-generated password system. 
Given these inputs:
1. Spoken Passphrase: "{passphrase}"
2. Voice Characteristics:
{features_str}

Generate exactly 5 possible passwords that could have been created from this voice input.
Rules:
- Each password should be 12 characters
- Include uppercase, lowercase, numbers, and special characters
- Base patterns on the passphrase and voice characteristics
- Format: just list the 5 passwords, one per line
"""

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )

        # Extract and clean up the guesses
        raw_guesses = response.choices[0].message.content.strip().split('\n')
        guesses = [guess.strip() for guess in raw_guesses if guess.strip()][:5]
        
        # Ensure exactly 5 guesses
        while len(guesses) < 5:
            guesses.append(f"GuessAttempt{len(guesses)+1}")
            
        elapsed_time = time.time() - start_time
        
        # Check if password was guessed
        password_cracked = password in guesses
        
        result = {
            "cracked": password_cracked,
            "time": f"{elapsed_time:.2f}s",
            "attempts": guesses,
            "message": "Password cracked!" if password_cracked else "Failed to crack password"
        }

        print(f" GPT Test Results: {json.dumps(result, indent=2)}")
        return result

    except Exception as e:
        print(f" GPT Testing Error: {str(e)}")
        return {
            "cracked": False,
            "time": f"{time.time() - start_time:.2f}s",
            "attempts": [f"Error{i+1}" for i in range(5)],
            "message": f"Error during testing: {str(e)}"
        }