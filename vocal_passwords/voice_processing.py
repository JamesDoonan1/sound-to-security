import sounddevice as sd
import soundfile as sf
import numpy as np

def record_audio(duration=5, sample_rate=22050):
    print(f"Recording audio for {duration} seconds at {sample_rate} Hz...")
    try:
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()  # Wait until recording is finished
        print(f"Recording complete. Captured audio shape: {audio.shape}")
        
        # Save the audio to a file
        filename = "vocal_input.wav"
        sf.write(filename, audio, sample_rate)
        print(f"Audio saved to {filename}")
        
        # Check for empty audio
        if np.all(audio == 0):
            print("Warning: Recorded audio is silent.")
        return np.squeeze(audio), sample_rate
    except Exception as e:
        print(f"Error during audio recording: {e}")
        return None, None