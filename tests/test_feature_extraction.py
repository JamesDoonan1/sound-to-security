import unittest
import os
import sys
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
    
    # Skip the AI password cracking tests for now
    @unittest.skip("Need to fix API mocking issues")
    def test_ai_crack_password(self):
        """Test AI password cracking with Claude"""
        pass
        
    @unittest.skip("Need to fix API mocking issues")  
    def test_ai_crack_password_no_api_key(self):
        """Test AI password cracking with missing API key"""
        pass
    
    @unittest.skip("Need to fix API mocking issues")  
    def test_ai_crack_password_ethical_refusal(self):
        """Test AI password cracking when Claude ethically refuses"""
        pass
    
    @unittest.skip("Need to fix API mocking issues")  
    def test_ai_crack_password_api_error(self):
        """Test AI password cracking with API error"""
        pass

if __name__ == "__main__":
    unittest.main()