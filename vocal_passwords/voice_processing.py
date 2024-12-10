import sounddevice as sd
import numpy as np

def record_audio(duration=5, sample_rate=22050):
    """Record audio from the microphone."""
    print(f"Recording audio for {duration} seconds at {sample_rate} Hz...")
    try:
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()  # Wait until recording finishes
        print(f"Recording complete. Captured audio shape: {audio.shape}")
        return np.squeeze(audio), sample_rate
    except Exception as e:
        print(f"Error during audio recording: {e}")
        return None, None
