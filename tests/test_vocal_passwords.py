import unittest
from vocal_passwords.feature_extraction import extract_audio_features, extract_rhythm_features
from vocal_passwords.voice_processing import record_audio

class TestVocalPasswords(unittest.TestCase):
    def test_extract_audio_features(self):
        """Test feature extraction with dummy audio."""
        import numpy as np
        audio = np.random.rand(22050 * 5)  # Simulated 5-second audio
        sr = 22050
        features = extract_audio_features(audio, sr)
        self.assertTrue(isinstance(features, str))

    def test_record_audio(self):
        """Test audio recording (integration test)."""
        audio, sr = record_audio(duration=1)  # 1-second test
        self.assertIsNotNone(audio)
        self.assertEqual(sr, 22050)

if __name__ == "__main__":
    unittest.main()
