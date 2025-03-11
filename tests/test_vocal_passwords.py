import unittest
import sys
import os
import numpy as np

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we should be able to import from vocal_passwords
from vocal_passwords.feature_extraction import extract_audio_features
from vocal_passwords.voice_processing import record_audio

class TestVocalPasswords(unittest.TestCase):
    def test_extract_audio_features(self):
        """Test feature extraction with dummy audio."""
        # Create simulated 5-second audio
        audio = np.random.rand(22050 * 5)
        sr = 22050
        features = extract_audio_features(audio, sr)
        
        # Update test to match the actual return type - a numpy array with 3 values
        self.assertTrue(isinstance(features, np.ndarray))
        self.assertEqual(features.shape, (3,))
        self.assertTrue(all(isinstance(val, np.float32) for val in features))

    @unittest.skip("This test requires audio hardware and will be skipped in CI environments")
    def test_record_audio(self):
        """Test audio recording (integration test) - Skip this for now."""
        audio, sr = record_audio(duration=1)  # 1-second test
        self.assertIsNotNone(audio)
        self.assertEqual(sr, 22050)

if __name__ == "__main__":
    unittest.main()