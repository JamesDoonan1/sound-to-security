import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)

class AIPasswordGenerator:
    def _format_features_for_prompt(self, features):
        """
        Format audio features into a thematic prompt for the AI without referencing the hash.
        This function interprets the audio features in a musical/sonic context and gives the AI guidance
        on how to reflect these characteristics in the password.
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
        Generate a secure password based solely on the thematic interpretation of audio features.
        """
        try:
            formatted_features = self._format_features_for_prompt(features)

            prompt = f"""
            Generate a secure password that reflects these audio characteristics:
            
            {formatted_features}
            
            Requirements:
            - Length between 16 and 32 characters
            - Include uppercase and lowercase letters
            - Include numbers
            - Include special characters (e.g. ^, *, ~, _, #, @, &)
            - Reflect brightness or mellowness in symbol choice
            - Reflect harmonic richness or darkness in letter case choice
            - Reflect tempo in number usage
            - Reflect beats in special character usage
            - No obvious patterns
            - Must be cryptographically strong
            
            Return only the password with no additional text.
            """

            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a password generation assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Keep temperature at 0 for more deterministic output
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating password: {e}")
            return None

if __name__ == "__main__":
    # Example usage with mock features.
    # In practice, you would get these from your audio_feature_extraction code.
    sample_features = {
        "MFCCs": np.random.randn(1000),
        "Spectral Centroid": np.random.randn(2000) + 1500,  # somewhat bright
        "Spectral Contrast": np.random.randn(2000),
        "Tempo": np.array([130]),  # energetic
        "Beats": np.array(range(200)),  # many beats
        "Harmonic Components": np.random.randn(1200),
        "Percussive Components": np.random.randn(1200),
        "Zero-Crossing Rate": np.random.randn(200),
        "Chroma Features (CENS)": np.random.randn(1200),
    }

    password_gen = AIPasswordGenerator()
    password = password_gen.generate_password(sample_features)
    print("Generated Password:", password)
