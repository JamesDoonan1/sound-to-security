import librosa
from vocal_passwords.feature_extraction import extract_audio_features
from models.claude_password_generator import generate_password_with_claude

def process_audio_and_generate_password(audio_path):
    """
    Process an audio file and generate a secure password.
    """
    # Load the audio file
    audio, sr = librosa.load(audio_path, sr=22050)

    # Extract features
    features = extract_audio_features(audio, sr)

    # Generate a password using Claude
    password = generate_password_with_claude(features)
    return password
