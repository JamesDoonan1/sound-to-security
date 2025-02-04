import unittest
from models.voice_recognition import verify_voice

class TestVoiceAuthentication(unittest.TestCase):

    def test_valid_voice(self):
        """Test if a valid voice matches the saved voiceprint."""
        result = verify_voice("vocal_input.wav")
        self.assertTrue(result)

    def test_invalid_voice(self):
        """Test if an invalid voice fails authentication."""
        result = verify_voice("different_voice.wav")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
