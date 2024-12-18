import librosa
import numpy as np
import os
import hashlib
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

# Import the new OpenAI client class
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Instantiate the OpenAI client
client = OpenAI(api_key=api_key)

class AudioFeatureProcessor:
    def extract_features(self, y: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Extracts features from an audio signal using Librosa."""
        return {
            "MFCCs": librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).flatten(),
            "Spectral Centroid": librosa.feature.spectral_centroid(y=y, sr=sr).flatten(),
            "Spectral Contrast": librosa.feature.spectral_contrast(y=y, sr=sr).flatten(),
            "Tempo": np.array([librosa.beat.beat_track(y=y, sr=sr)[0]]).flatten(),
            "Beats": librosa.beat.beat_track(y=y, sr=sr)[1].flatten(),
            "Harmonic Components": librosa.effects.hpss(y)[0].flatten(),
            "Percussive Components": librosa.effects.hpss(y)[1].flatten(),
            "Zero-Crossing Rate": librosa.feature.zero_crossing_rate(y).flatten(),
            "Chroma Features (CENS)": librosa.feature.chroma_cens(y=y, sr=sr).flatten(),
        }

    def create_hash(self, features: Dict[str, np.ndarray]) -> str:
        """Creates a unique hash based on the extracted features."""
        concatenated_features = np.concatenate([value for value in features.values()])
        feature_bytes = concatenated_features.tobytes()
        return hashlib.md5(feature_bytes).hexdigest()

class AudioPasswordGenerator:
    def _format_features_for_prompt(self, features: Dict[str, np.ndarray], audio_hash: str) -> str:
        """Format audio features into a readable string for the AI prompt."""
        feature_summary = [f"Audio Hash: {audio_hash}"]

        for feature_name, feature_array in features.items():
            if len(feature_array) > 0:
                stats = {
                    'mean': np.mean(feature_array),
                    'max': np.max(feature_array),
                    'min': np.min(feature_array),
                    'std': np.std(feature_array)
                }
                feature_summary.append(f"\n{feature_name}:")
                for stat_name, value in stats.items():
                    feature_summary.append(f"- {stat_name}: {value:.4f}")

        return "\n".join(feature_summary)

    def generate_password(self, features: Dict[str, np.ndarray], audio_hash: str) -> str:
        """Generate a secure password based on audio features using OpenAI."""
        try:
            formatted_features = self._format_features_for_prompt(features, audio_hash)

            prompt = f"""
            Generate a secure password using these audio characteristics:
            
            {formatted_features}
            
            Requirements:
            - Length between 16 and 32 characters
            - Include uppercase and lowercase letters
            - Include numbers
            - Include special characters
            - No obvious patterns
            - Must be cryptographically strong
            
            Return only the password with no additional text.
            """

            # Use the new client to create chat completions
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a password generation assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Access the generated password
            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating password: {e}")
            return None

def process_audio_file(file_path: str) -> Tuple[str, str]:
    """Process a single audio file and return its hash and generated password."""
    processor = AudioFeatureProcessor()
    password_gen = AudioPasswordGenerator()

    try:
        # Load and process audio
        y, sr = librosa.load(file_path, sr=None)
        print(f"Loaded: {len(y)} samples, Sample Rate: {sr}")

        # Extract features and create hash
        features = processor.extract_features(y, sr)
        audio_hash = processor.create_hash(features)

        # Print feature information
        print("\nExtracted Features:")
        for key, value in features.items():
            print(f"{key}: {value.shape if isinstance(value, np.ndarray) else len(value)}")

        # Generate password
        password = password_gen.generate_password(features, audio_hash)

        return audio_hash, password

    except Exception as e:
        print(f"Failed to process file: {e}")
        return None, None

def process_audio_files(folder_path: str) -> None:
    """Process all audio files in the specified folder."""
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    results = []

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".mp3"):
            continue

        file_path = os.path.join(folder_path, file_name)
        print(f"\nProcessing file: {file_name}")

        audio_hash, password = process_audio_file(file_path)

        if audio_hash and password:
            print(f"\nGenerated Hash: {audio_hash}")
            print(f"Generated Password: {password}")
            results.append({
                "file": file_name,
                "hash": audio_hash,
                "password": password
            })

        print("-" * 50)

    # Save results to a file
    if results:
        with open("audio_passwords.txt", "w") as f:
            for result in results:
                f.write(f"File: {result['file']}\n")
                f.write(f"Hash: {result['hash']}\n")
                f.write(f"Password: {result['password']}\n")
                f.write("-" * 50 + "\n")
        print("\nResults saved to audio_passwords.txt")

    print("Processing completed.")

if __name__ == "__main__":
    # Set your audio folder path
    AUDIO_FOLDER_PATH = "/media/sf_VM_Shared_Folder/Audio Files"

    try:
        process_audio_files(AUDIO_FOLDER_PATH)
    except Exception as e:
        print(f"An error occurred: {e}")
