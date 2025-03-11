import unittest
import os
import sys
import anthropic
from unittest.mock import patch, MagicMock, mock_open

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestPasswordCrackers(unittest.TestCase):
    """Test password cracking functionality"""
    
    def test_brute_force_crack_success(self):
        """Test brute force cracking with a simple password (should succeed quickly)"""
        from backend.services.password_cracker import brute_force_crack
        
        # Use a very simple password that should crack immediately
        result = brute_force_crack("a", max_length=1, timeout=1)
        
        # Check result
        self.assertTrue(result['cracked'])
        self.assertEqual(result['guess'], "a")
        self.assertIn('time_taken', result)
    
    def test_brute_force_crack_timeout(self):
        """Test brute force cracking timeout"""
        from backend.services.password_cracker import brute_force_crack
        
        # Use a complex password that can't be cracked quickly
        result = brute_force_crack("C0mpl3x!P@$$w0rd", max_length=5, timeout=1)
        
        # Check result
        self.assertFalse(result['cracked'])
        self.assertIn('message', result)
        self.assertEqual(result['message'], "Brute force timed out")
    
    @patch('time.time')
    @patch('backend.services.password_cracker.brute_force_worker')
    def test_brute_force_worker_success(self, mock_worker, mock_time):
        """Test the brute force worker function"""
        from backend.services.password_cracker import brute_force_crack
        
        # Configure mocks
        start_times = [100.0]
        end_times = [105.0]
        mock_time.side_effect = lambda: start_times.pop(0) if start_times else end_times.pop(0)
        
        # Define behavior for worker function
        def side_effect(target_password, max_length, characters, result):
            result['cracked'] = True
            result['guess'] = target_password
            result['time_taken'] = 5.0
        
        mock_worker.side_effect = side_effect
        
        # Call function
        result = brute_force_crack("test", max_length=4, timeout=10)
        
        # Check result
        self.assertTrue(result['cracked'])
        self.assertEqual(result['guess'], "test")
        self.assertEqual(result['time_taken'], 5.0)
        mock_worker.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open, read_data="password\nadmin\ntest\n123456\n")
    def test_dictionary_attack_success(self, mock_file):
        """Test dictionary attack with password in dictionary"""
        from backend.services.password_cracker import dictionary_attack
        
        # Call function with password that's in the dictionary
        result = dictionary_attack("admin")
        
        # Check result
        self.assertTrue(result['cracked'])
        self.assertEqual(result['guess'], "admin")
        self.assertIn('time_taken', result)
        mock_file.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open, read_data="password\nadmin\ntest\n123456\n")
    def test_dictionary_attack_failure(self, mock_file):
        """Test dictionary attack with password not in dictionary"""
        from backend.services.password_cracker import dictionary_attack
        
        # Call function with password that's not in the dictionary
        result = dictionary_attack("secure_password123!")
        
        # Check result
        self.assertFalse(result['cracked'])
        self.assertEqual(result['message'], "Password not found in dictionary")
        mock_file.assert_called_once()
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_dictionary_attack_no_file(self, mock_file):
        """Test dictionary attack when dictionary file is missing"""
        from backend.services.password_cracker import dictionary_attack
        
        # Call function when dictionary file doesn't exist
        result = dictionary_attack("any_password")
        
        # Check result
        self.assertFalse(result['cracked'])
        self.assertEqual(result['message'], "Dictionary file not found")
        mock_file.assert_called_once()
    
    @patch('anthropic.Anthropic')
    @patch('os.getenv')
    

    def ai_crack_password(password):
    # Check for API key first
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                'cracked': False,
                'message': "AI API key missing"
            }
        
        try:
            # Initialize Anthropic client
            client = anthropic.Anthropic(api_key=api_key)
            
            # Construct prompt
            prompt = f"""Generate password variations for the password '{password}'.
            Provide 3-5 potential variations that could be used to crack this password."""
            
            # Make API call
            response = client.messages.create(
                model="claude-2",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Process response
            attempts = response.content[0].text.strip().split('\n')
            
            # Check if any attempt matches the original password
            cracked = any(attempt == password for attempt in attempts)
            
            return {
                'cracked': cracked,
                'attempts': attempts,
                'message': "AI generated similar passwords." if not cracked else "Password cracked!"
            }
        
        except Exception as e:
            return {
                'cracked': False,
                'message': f"AI Cracking Error: {str(e)}"
            }
        
    @patch('anthropic.Anthropic')
    @patch('os.getenv')
    def test_ai_crack_password_ethical_refusal(self, mock_getenv, mock_anthropic):
        """Test AI password cracking when Claude ethically refuses"""
        from backend.services.ai_password_cracker import ai_crack_password
        
        # Configure mocks
        mock_getenv.return_value = "fake-api-key"
        
        # Create mock client and response
        mock_client = MagicMock()
        mock_messages = MagicMock()
        mock_client.messages.create.return_value = mock_messages
        mock_anthropic.return_value = mock_client
        
        # Configure response indicating ethical refusal
        mock_messages.content = [MagicMock(text="I refuse to generate password variations due to ethical concerns.")]
        
        # Call the function
        result = ai_crack_password("test_password")
        
        # Check results - should indicate refusal
        self.assertFalse(result['cracked'])
        self.assertEqual(result['message'], "AI refused to generate password variations.")
        self.assertIn('explanation', result)
        
        # Verify API was called
        mock_anthropic.assert_called_once()
        mock_client.messages.create.assert_called_once()
    
    @patch('anthropic.Anthropic')
    @patch('os.getenv')
    def test_ai_crack_password_no_api_key(self, mock_getenv, mock_anthropic):
        """Test AI password cracking with missing API key"""
        from backend.services.ai_password_cracker import ai_crack_password
        
        # Configure mocks - API key missing
        mock_getenv.return_value = None
        
        # Call the function
        result = ai_crack_password("test_password")
        
        # Check results
        self.assertFalse(result['cracked'])
        self.assertEqual(result['message'], "AI API key missing")
        
        # Verify Anthropic client was not created
        mock_anthropic.assert_not_called()
    
    @patch('anthropic.Anthropic')
    @patch('os.getenv')
    def test_ai_crack_password_api_error(self, mock_getenv, mock_anthropic):
        """Test AI password cracking with API error"""
        from backend.services.ai_password_cracker import ai_crack_password
        
        # Configure mocks
        mock_getenv.return_value = "fake-api-key"
        
        # Create mock client that raises an exception
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        # Call the function
        result = ai_crack_password("test_password")
        
        # Check results
        self.assertFalse(result['cracked'])
        self.assertIn('message', result)
        self.assertIn('Error', result['message'])
        
        # Verify API attempt was made
        mock_anthropic.assert_called_once()
        mock_client.messages.create.assert_called_once()

if __name__ == "__main__":
    unittest.main()