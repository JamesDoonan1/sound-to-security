import unittest
import os
import sys
import time
import json
from unittest.mock import patch, MagicMock, create_autospec
from openai import OpenAI

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestGPTPasswordTester(unittest.TestCase):
    """Test GPT-based password testing functionality"""
    
    @patch('backend.services.gpt_password_tester.OpenAI')
    @patch('os.getenv')
    @patch('time.time')
    def test_test_password_with_gpt_success(self, mock_time, mock_getenv, mock_openai_class):
        """Test GPT password testing with successful response"""
        from backend.services.gpt_password_tester import test_password_with_gpt
        
        # Configure time mock for predictable elapsed time
        mock_time.side_effect = [1000.0, 1005.0]
        
        # Configure mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Configure chat completion response
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(
                    content="P@ssw0rd123!\nSecur3P@ss!\nStrongP@ss1!\nVoic3P@ss!\nAuth3nt1c@te!"
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Test data
        password = "P@ssw0rd123!"  # This will be "cracked" by GPT
        passphrase = "my secure passphrase"
        voice_features = {
            'mfcc': 120.5,
            'spectral_centroid': 2500.75,
            'tempo': 95.0
        }
        
        # Call the function
        result = test_password_with_gpt(password, passphrase, voice_features)
        
        # Check results
        self.assertTrue(result['cracked'])
        self.assertEqual(result['time'], "5.00s")
        self.assertEqual(len(result['attempts']), 5)
        self.assertIn(password, result['attempts'])
        self.assertEqual(result['message'], "Password cracked!")
        
        # Verify API was called correctly
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('backend.services.gpt_password_tester.OpenAI')
    @patch('os.getenv')
    @patch('time.time')
    def test_test_password_with_gpt_not_cracked(self, mock_time, mock_getenv, mock_openai_class):
        """Test GPT password testing when password is not cracked"""
        from backend.services.gpt_password_tester import test_password_with_gpt
        
        # Configure time mock
        mock_time.side_effect = [1000.0, 1003.0]
        
        # Configure mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Configure chat completion response with guesses that don't match
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(
                    content="WrongP@ss1!\nIncorr3ct2#\nN0tR1ght3$\nTr1edBut@No\nLastAttempt!"
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Test data - different from the guesses
        password = "CompletelyDifferent123!"
        passphrase = "my secure passphrase"
        voice_features = {
            'mfcc': 120.5,
            'spectral_centroid': 2500.75,
            'tempo': 95.0
        }
        
        # Call the function
        result = test_password_with_gpt(password, passphrase, voice_features)
        
        # Check results
        self.assertFalse(result['cracked'])
        self.assertEqual(result['time'], "3.00s")
        self.assertEqual(len(result['attempts']), 5)
        self.assertEqual(result['message'], "Failed to crack password")
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('backend.services.gpt_password_tester.OpenAI')
    @patch('os.getenv')
    @patch('time.time')
    def test_test_password_with_gpt_fewer_responses(self, mock_time, mock_getenv, mock_openai_class):
        """Test GPT password testing when GPT returns fewer than 5 responses"""
        from backend.services.gpt_password_tester import test_password_with_gpt
        
        # Configure time mock
        mock_time.side_effect = [1000.0, 1002.0]
        
        # Configure mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Configure chat completion response with only 2 guesses
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(
                    content="WrongP@ss1!\nIncorr3ct2#"
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Test data
        password = "CompletelyDifferent123!"
        passphrase = "my secure passphrase"
        voice_features = {
            'mfcc': 120.5,
            'spectral_centroid': 2500.75,
            'tempo': 95.0
        }
        
        # Call the function
        result = test_password_with_gpt(password, passphrase, voice_features)
        
        # Check results - should have 5 attempts with placeholders filled in
        self.assertFalse(result['cracked'])
        self.assertEqual(len(result['attempts']), 5)
        self.assertEqual(result['attempts'][0], "WrongP@ss1!")
        self.assertEqual(result['attempts'][1], "Incorr3ct2#")
        self.assertTrue(result['attempts'][2].startswith("GuessAttempt"))
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('backend.services.gpt_password_tester.OpenAI')
    @patch('os.getenv')
    @patch('time.time')
    def test_test_password_with_gpt_api_error(self, mock_time, mock_getenv, mock_openai_class):
        """Test GPT password testing when API error occurs"""
        from backend.services.gpt_password_tester import test_password_with_gpt
        
        # Configure time mock
        mock_time.side_effect = [1000.0, 1001.0]
        
        # Configure mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Configure mock to raise an exception when creating chat completion
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Test data
        password = "TestPassword123!"
        passphrase = "my secure passphrase"
        voice_features = {
            'mfcc': 120.5,
            'spectral_centroid': 2500.75,
            'tempo': 95.0
        }
        
        # Call the function
        result = test_password_with_gpt(password, passphrase, voice_features)
        
        # Check results - should handle error gracefully
        self.assertFalse(result['cracked'])
        self.assertEqual(result['time'], "1.00s")
        self.assertEqual(len(result['attempts']), 5)
        self.assertTrue(all(attempt.startswith("Error") for attempt in result['attempts']))
        self.assertIn("Error during testing", result['message'])
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('backend.services.gpt_password_tester.OpenAI')
    @patch('os.getenv')
    @patch('time.time')
    @patch('backend.services.gpt_password_tester.print')
    def test_debug_outputs(self, mock_print, mock_time, mock_getenv, mock_openai_class):
        """Test debug output formatting"""
        from backend.services.gpt_password_tester import test_password_with_gpt
        
        # Configure time mock
        mock_time.side_effect = [1000.0, 1002.0]
        
        # Configure mocks
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Configure chat completion response
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(
                    content="P@ssw0rd123!\nSecur3P@ss!"
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Call function
        result = test_password_with_gpt(
            "TestPass123!", 
            "test passphrase", 
            {'mfcc': 100.0, 'spectral_centroid': 2000.0, 'tempo': 90.0}
        )
        
        # Verify debug print statements were called
        self.assertGreaterEqual(mock_print.call_count, 3)  # At least 3 debug prints
        
        # Check for expected debug patterns
        debug_strings = [str(args[0]) for args, _ in mock_print.call_args_list]
        self.assertTrue(any("DEBUG: GPT Generated Passwords" in s for s in debug_strings))
        self.assertTrue(any("DEBUG: GPT Cracked Password?" in s for s in debug_strings))
        self.assertTrue(any("DEBUG: GPT Processing Time" in s for s in debug_strings))

if __name__ == "__main__":
    unittest.main()