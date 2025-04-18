import sounddevice as sd
import soundfile as sf
import numpy as np
import librosa
from resemblyzer import VoiceEncoder, preprocess_wav

encoder = VoiceEncoder()

def record_audio(duration=5, sample_rate=22050):
    print(f" Recording for {duration} seconds at {sample_rate} Hz...")
    try:
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        print(f" Recording complete. Captured audio shape: {audio.shape}")
        
        # Save audio file
        filename = "vocal_input.wav"
        sf.write(filename, audio, sample_rate)
        print(f" Audio saved to {filename}")

        # Generate voice embedding
        wav = preprocess_wav(filename)
        embedding = encoder.embed_utterance(wav)

        # Save the voiceprint
        np.save("voice_embedding.npy", embedding)
        print(" Voiceprint saved for authentication.")

        return np.squeeze(audio), sample_rate
    except Exception as e:
        print(f" Error during audio recording: {e}")
        return None, None

def verify_voice(audio_path="vocal_input.wav"):
    """Compares new voice recording against the saved voiceprint."""
    try:
        saved_embedding = np.load("voice_embedding.npy")

        # Load test voice sample
        wav = preprocess_wav(audio_path)
        test_embedding = encoder.embed_utterance(wav)

        # Compute similarity
        similarity = np.dot(saved_embedding, test_embedding)

        if similarity > 0.85:  # Threshold for voice verification
            print(" Voice verified! Proceeding with password generation...")
            return True
        else:
            print(" Voice not recognized! Access denied.")
            return False
    except FileNotFoundError:
        print(" No saved voiceprint found. Please record your voice first.")
        return False
