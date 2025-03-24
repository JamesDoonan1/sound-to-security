import unittest
import numpy as np
import os
import sys
from unittest.mock import patch, mock_open,MagicMock

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestVoiceAuth(unittest.TestCase):
    """Test voice authentication functionality"""
    
    @patch('numpy.save')
    def test_save_voiceprint(self, mock_save):
        """Test saving voiceprint features"""
        from vocal_passwords.voice_auth import save_voiceprint
        
        # Test data
        voice_features = np.array([123.45, 4567.89, 85.5], dtype=np.float32)
        
        # Call the function
        save_voiceprint(voice_features)
        
        # Check that numpy.save was called with the right arguments
        mock_save.assert_called_once()
        args = mock_save.call_args[0]
        self.assertEqual(args[0], "stored_voiceprint.npy")
        np.testing.assert_array_equal(args[1], voice_features)
    
    @patch('numpy.load')
    @patch('os.path.exists')
    def test_load_voiceprint_exists(self, mock_exists, mock_load):
        """Test loading voiceprint when file exists"""
        from vocal_passwords.voice_auth import load_voiceprint
        
        # Setup mocks
        mock_exists.return_value = True
        test_voiceprint = np.array([123.45, 4567.89, 85.5], dtype=np.float32)
        mock_load.return_value = test_voiceprint
        
        # Call the function
        result = load_voiceprint()
        
        # Check results
        np.testing.assert_array_equal(result, test_voiceprint)
        mock_exists.assert_called_once_with("stored_voiceprint.npy")
        mock_load.assert_called_once_with("stored_voiceprint.npy")
    
    @patch('os.path.exists')
    def test_load_voiceprint_not_exists(self, mock_exists):
        """Test loading voiceprint when file doesn't exist"""
        from vocal_passwords.voice_auth import load_voiceprint
        
        # Setup mock
        mock_exists.return_value = False
        
        # Call the function
        result = load_voiceprint()
        
        # Check result
        self.assertIsNone(result)
        mock_exists.assert_called_once_with("stored_voiceprint.npy")
    
    @patch('vocal_passwords.voice_auth.load_voiceprint')
    def test_verify_voice_match(self, mock_load_voiceprint):
        """Test voice verification when voices match"""
        from vocal_passwords.voice_auth import verify_voice
        
        # Setup mocks
        stored_voiceprint = np.array([123.45, 4567.89, 85.5], dtype=np.float32)
        mock_load_voiceprint.return_value = stored_voiceprint
        
        # Test data - close enough to the stored voiceprint
        new_features = np.array([123.5, 4567.9, 85.6], dtype=np.float32)
        
        # Call the function with a low threshold to ensure match
        result = verify_voice(new_features, threshold=10)
        
        # Check result
        self.assertTrue(result)
        mock_load_voiceprint.assert_called_once()
    
    @patch('vocal_passwords.voice_auth.load_voiceprint')
    def test_verify_voice_no_match(self, mock_load_voiceprint):
        """Test voice verification when voices don't match"""
        from vocal_passwords.voice_auth import verify_voice
        
        # Setup mocks
        stored_voiceprint = np.array([123.45, 4567.89, 85.5], dtype=np.float32)
        mock_load_voiceprint.return_value = stored_voiceprint
        
        # Test data - very different from stored voiceprint
        new_features = np.array([500.0, 8000.0, 150.0], dtype=np.float32)
        
        # Call the function with a low threshold
        result = verify_voice(new_features, threshold=10)
        
        # Check result
        self.assertFalse(result)
        mock_load_voiceprint.assert_called_once()
    
    @patch('vocal_passwords.voice_auth.load_voiceprint')
    def test_verify_voice_no_stored_print(self, mock_load_voiceprint):
        """Test voice verification when no stored voiceprint exists"""
        from vocal_passwords.voice_auth import verify_voice
        
        # Setup mocks
        mock_load_voiceprint.return_value = None
        
        # Test data
        new_features = np.array([123.45, 4567.89, 85.5], dtype=np.float32)
        
        # Call the function
        result = verify_voice(new_features)
        
        # Check result
        self.assertFalse(result)
        mock_load_voiceprint.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_passphrase(self, mock_file):
        """Test saving passphrase to file"""
        from vocal_passwords.voice_auth import save_passphrase
        
        # Test data
        passphrase = "my secure passphrase"
        
        # Call the function
        save_passphrase(passphrase)
        
        # Check file operations
        mock_file.assert_called_once()
        mock_file().write.assert_called_once_with(passphrase)
    
    @patch('builtins.open', new_callable=mock_open, read_data="my secure passphrase")
    @patch('os.path.exists')
    def test_load_passphrase_exists(self, mock_exists, mock_file):
        """Test loading passphrase when file exists"""
        from vocal_passwords.voice_auth import load_passphrase
        
        # Setup mocks
        mock_exists.return_value = True
        
        # Call the function
        result = load_passphrase()
        
        # Check result
        self.assertEqual(result, "my secure passphrase")
        mock_exists.assert_called_once()
        mock_file.assert_called_once()
    
    @patch('os.path.exists')
    def test_load_passphrase_not_exists(self, mock_exists):
        """Test loading passphrase when file doesn't exist"""
        from vocal_passwords.voice_auth import load_passphrase
        
        # Setup mock
        mock_exists.return_value = False
        
        # Call the function
        result = load_passphrase()
        
        # Check result
        self.assertEqual(result, "NO_PASSPHRASE")
        mock_exists.assert_called_once()
    
    @patch('vocal_passwords.voice_auth.load_passphrase')
    def test_verify_passphrase_match(self, mock_load_passphrase):
        """Test passphrase verification when phrases match"""
        from vocal_passwords.voice_auth import verify_passphrase
        
        # Setup mocks
        mock_load_passphrase.return_value = "my secure passphrase"
        
        # Call the function
        result = verify_passphrase("my secure passphrase")
        
        # Check result
        self.assertTrue(result)
        mock_load_passphrase.assert_called_once()
    
    @patch('vocal_passwords.voice_auth.load_passphrase')
    def test_verify_passphrase_different_case(self, mock_load_passphrase):
        """Test passphrase verification with different case (should match)"""
        from vocal_passwords.voice_auth import verify_passphrase
        
        # Setup mocks
        mock_load_passphrase.return_value = "My Secure Passphrase"
        
        # Call the function with different case
        result = verify_passphrase("my secure passphrase")
        
        # Check result - should still match due to case insensitivity
        self.assertTrue(result)
        mock_load_passphrase.assert_called_once()
    
    @patch('vocal_passwords.voice_auth.load_passphrase')
    def test_verify_passphrase_no_match(self, mock_load_passphrase):
        """Test passphrase verification when phrases don't match"""
        from vocal_passwords.voice_auth import verify_passphrase
        
        # Setup mocks
        mock_load_passphrase.return_value = "my secure passphrase"
        
        # Call the function with a different phrase
        result = verify_passphrase("incorrect passphrase")
        
        # Check result
        self.assertFalse(result)
        mock_load_passphrase.assert_called_once()
    
    @patch('vocal_passwords.voice_auth.load_passphrase')
    def test_verify_passphrase_no_stored_phrase(self, mock_load_passphrase):
        """Test passphrase verification when no stored phrase exists"""
        from vocal_passwords.voice_auth import verify_passphrase
        
        # Setup mocks
        mock_load_passphrase.return_value = None
        
        # Call the function
        result = verify_passphrase("my secure passphrase")
        
        # Check result
        self.assertFalse(result)
        mock_load_passphrase.assert_called_once()
    
    @patch('speech_recognition.Recognizer.recognize_google')
    @patch('speech_recognition.AudioFile')
    @patch('speech_recognition.Recognizer.record')
    def test_recognize_speech_success(self, mock_record, mock_audio_file, mock_recognize):
        """Test speech recognition when successful"""
        # We need to patch the right way - at the module level
        with patch('vocal_passwords.voice_auth.sr.Recognizer') as mock_recognizer_class:
            # Create a mock recognizer instance
            mock_recognizer_instance = MagicMock()
            mock_recognizer_class.return_value = mock_recognizer_instance
            
            # Set up the mock chain for recognize_google
            mock_recognizer_instance.recognize_google.return_value = "my secure passphrase"
            
            # Import here to ensure patches take effect
            from vocal_passwords.voice_auth import recognize_speech
            
            # Call the function
            result = recognize_speech("vocal_input.wav")
            
            # Check result
            self.assertEqual(result, "my secure passphrase")
            
            # Verify mocks were called
            mock_audio_file.assert_called_once_with("vocal_input.wav")
            mock_recognizer_instance.recognize_google.assert_called_once()

if __name__ == "__main__":
    unittest.main()