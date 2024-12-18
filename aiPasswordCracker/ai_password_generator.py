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
    def _format_features_for_prompt(self, features, audio_hash):
        """
        Format audio features into a readable, thematic string for the AI prompt.
        Add logic to reflect characteristics of the audio in symbolic form.
        """
        
        # Example: Use the mean of some features to decide which symbols to use
        mean_mfcc = np.mean(features["MFCCs"])
        mean_spectral_centroid = np.mean(features["Spectral Centroid"])
        tempo = float(features["Tempo"][0]) if len(features["Tempo"]) > 0 else 120.0  # default tempo if missing
        beats_count = len(features["Beats"])

        description = f"Audio Hash: {audio_hash}\n"
        description += "Audio Characterization:\n"

        # High spectral centroid = bright / high-frequency → use ^ or * symbols
        if mean_spectral_centroid > 2000:
            description += "- Bright, high-frequency tones (use ^, *)\n"
        else:
            description += "- Mellow, low-frequency tones (use ~, _)\n"

        # High MFCC mean might imply richer harmonic content → use uppercase letters
        if mean_mfcc > 0:
            description += "- Rich harmonic profile (use uppercase letters)\n"
        else:
            description += "- Darker harmonic profile (use lowercase letters)\n"

        # Tempo reflection: faster tempo → more digits or special characters
        if tempo > 120:
            description += f"- Energetic (tempo: {tempo:.2f} BPM) → Add numbers\n"
        else:
            description += f"- Relaxed (tempo: {tempo:.2f} BPM) → Add fewer numbers\n"

        # Beats count influences complexity
        if beats_count > 100:
            description += "- Many beats → More special characters\n"
        else:
            description += "- Few beats → Fewer special characters\n"
        
        return description

    def generate_password(self, features, audio_hash):
        """
        Generate a secure password using these audio characteristics.
        """
        try:
            formatted_features = self._format_features_for_prompt(features, audio_hash)
            prompt = f"""
            Generate a secure password using these audio characteristics:
            
            {formatted_features}

            Requirements:
            - Length between 16 and 32 characters
            - Include uppercase and lowercase letters
            - Include numbers
            - Include special characters (some from: ^, *, ~, _, #, @, &)
            - Reflect the 'bright' or 'mellow' nature of the audio
            - Reflect the 'rich' or 'dark' harmonic profile
            - If energetic, include more numbers
            - If many beats, include more special characters
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
                temperature=0,  # reduce randomness for consistency
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating password: {e}")
            return None

if __name__ == "__main__":
    # Example usage (just a demonstration):
    # Assuming we already have 'features' and 'audio_hash' from audio_feature_extraction.py
    # This is just a mock-up array for demonstration purposes.
    sample_features = {
        "MFCCs": np.random.randn(1000),
        "Spectral Centroid": np.random.randn(2000) + 2000,  # somewhat high
        "Spectral Contrast": np.random.randn(2000),
        "Tempo": np.array([150]),  # higher tempo
        "Beats": np.array([1,2,3,4] * 200),  # many beats
        "Harmonic Components": np.random.randn(1200),
        "Percussive Components": np.random.randn(1200),
        "Zero-Crossing Rate": np.random.randn(200),
        "Chroma Features (CENS)": np.random.randn(1200),
    }

    sample_hash = "be57b3b83719a851fffac1968b22cc73"
    gen = AIPasswordGenerator()
    password = gen.generate_password(sample_features, sample_hash)
    print("Generated Password:", password)
