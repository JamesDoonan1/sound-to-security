import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from audio_passwords.audio_feature_extraction import extract_features

# Load API key from environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)

class AIPasswordGenerator:
    def _format_features_for_prompt(self, features):
        """
        Format audio features into a thematic prompt for the AI without referencing the hash.
        Interprets the audio features in a musical/sonic context and guides
        how to reflect these characteristics in the password.
        """
        mean_mfcc = np.mean(features["MFCCs"])
        mean_spectral_centroid = np.mean(features["Spectral Centroid"])
        tempo = float(features["Tempo"][0]) if len(features["Tempo"]) > 0 else 120.0
        beats_count = len(features["Beats"])

        description = "The audio characteristics:\n"
        if mean_spectral_centroid > 2000:
            description += "- Bright, high-frequency tones (use symbols like ^, *)\n"
        else:
            description += "- Mellow, low-frequency tones (use symbols like ~, _)\n"

        if mean_mfcc > 0:
            description += "- Rich harmonic profile (mix uppercase and lowercase letters)\n"
        else:
            description += "- Darker harmonic profile (lean on lowercase letters)\n"

        if tempo > 120:
            description += f"- Energetic tempo ({tempo:.2f} BPM) → include more numbers\n"
        else:
            description += f"- Relaxed tempo ({tempo:.2f} BPM) → fewer numbers\n"

        if beats_count > 100:
            description += "- Many beats → use more special characters (#, @, &, etc.)\n"
        else:
            description += "- Few beats → fewer special characters\n"

        return description

    def generate_password(self, features):
        """
        Generate a secure password based on the thematic interpretation of audio features.
        """
        try:
            formatted_features = self._format_features_for_prompt(features)
            # print("Formatted Features for Prompt:", formatted_features)  # Debugging output

            prompt = f"""
            Generate a secure password that reflects these audio characteristics:

            {formatted_features}

            Requirements:
            - Length exactly 12 characters.
            - Include uppercase and lowercase letters.
            - Include numbers.
            - Include special characters (e.g. ^, *, ~, _, #, @, &).
            - Reflect brightness or mellowness in symbol choice.
            - Reflect harmonic richness or darkness in letter case choice.
            - Reflect tempo in number usage.
            - Reflect beats in special character usage.
            - No obvious patterns.
            - Must be cryptographically strong.
            - **Use musical words related to brightness, harmony, rhythm, and energy (e.g., "Bright", "Harmonic", "Beat", "Melody", "Dark", "Bass", etc.).**
            - **If brightness is high, use words like "Bright", "Treble", "Sharp".**
            - **If brightness is low, use words like "Dark", "Bass", "Deep".**
            - **If the tempo is fast, reflect energy with words like "Rush", "Quick", "Pulse".**
            - **If the tempo is slow, reflect smoothness with words like "Flow", "Calm", "Ease".**

            Return only the password with exactly 12 characters and no extra text.
"""


            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a password generation assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating password: {e}")
            return None
