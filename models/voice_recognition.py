import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

encoder = VoiceEncoder()

def save_voiceprint(audio_path="vocal_input.wav"):
    """Generates and saves a voiceprint for authentication."""
    try:
        wav = preprocess_wav(audio_path)
        embedding = encoder.embed_utterance(wav)
        np.save("voice_embedding.npy", embedding)
        print(" Voiceprint saved successfully.")
    except Exception as e:
        print(f" Error saving voiceprint: {e}")

def verify_voice(audio_path="vocal_input.wav"):
    """Compares the given voice to the saved voiceprint."""
    try:
        saved_embedding = np.load("voice_embedding.npy")
        wav = preprocess_wav(audio_path)
        test_embedding = encoder.embed_utterance(wav)
        similarity = np.dot(saved_embedding, test_embedding)

        if similarity > 0.85:  # Similarity threshold
            print(" Voice verified!")
            return True
        else:
            print(" Voice not recognized.")
            return False
    except FileNotFoundError:
        print(" No saved voiceprint found. Please register your voice first.")
        return False
