from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to generate a password based on audio features
def generate_password_from_audio_features(features):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a password generation assistant."},
                {
                    "role": "user",
                    "content": f"Generate a secure password based on these audio features: {features}"
                }
            ]
        )
        
        # Accessing the generated password directly
        generated_password = completion.choices[0].message.content.strip()
        print("Generated Password:", generated_password)
        return generated_password

    except Exception as e:
        print("Error generating password:", e)

# Example usage with made-up audio features
audio_features = """
- High bass frequency
- Echo effect
- Moderate tempo
"""
generate_password_from_audio_features(audio_features)