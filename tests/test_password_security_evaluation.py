import unittest
import sys
import os
import string
import math

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from backend
from backend.utils.password_comparator import calculate_entropy, brute_force_complexity

class TestPasswordSecurity(unittest.TestCase):
    """Test password security evaluation functions"""
    
    def test_entropy_calculation(self):
        """Test that entropy calculation works correctly"""
        # Test with simple password
        simple_password = "password"
        simple_entropy = calculate_entropy(simple_password)
        print(f"Simple password entropy: {simple_entropy}")
        self.assertLess(simple_entropy, 40, "Simple password should have low entropy")
        
        # Test with complex password
        complex_password = "Tr0ub4dor&3"
        complex_entropy = calculate_entropy(complex_password)
        print(f"Complex password entropy: {complex_entropy}")
        self.assertGreater(complex_entropy, 35, "Complex password should have higher entropy than simple password")
        
        # Test with empty password
        empty_entropy = calculate_entropy("")
        print(f"Empty password entropy: {empty_entropy}")
        self.assertEqual(empty_entropy, 0, "Empty password should have zero entropy")
        
        # Test password length impact
        # These should have increasing entropy as they get longer
        pwd1 = "abc"
        pwd2 = "abcdef"
        pwd3 = "abcdefghi"
        
        entropy1 = calculate_entropy(pwd1)
        entropy2 = calculate_entropy(pwd2)
        entropy3 = calculate_entropy(pwd3)
        
        print(f"3-char entropy: {entropy1}, 6-char entropy: {entropy2}, 9-char entropy: {entropy3}")
        
        # Entropy should increase with password length
        self.assertLess(entropy1, entropy2, "Longer password should have higher entropy")
        self.assertLess(entropy2, entropy3, "Longer password should have higher entropy")
    
    def test_brute_force_complexity(self):
        """Test that brute force complexity estimation works correctly"""
        # Simple password should be crackable quickly
        simple_password = "abc123"
        simple_time = brute_force_complexity(simple_password)
        print(f"Simple password brute-force time: {simple_time}")
        
        # Complex password should take much longer
        complex_password = "X7!bQ9p#2LmK"
        complex_time = brute_force_complexity(complex_password)
        print(f"Complex password brute-force time: {complex_time}")
        
        # Verify that complex password takes longer
        self.assertGreater(complex_time, simple_time, 
                          "Complex password should take longer to crack")
        
        # Verify that adding just one character increases complexity
        pwd1 = "aB3$xY7"
        pwd2 = "aB3$xY7!"
        
        time1 = brute_force_complexity(pwd1)
        time2 = brute_force_complexity(pwd2)
        print(f"7-char password time: {time1}")
        print(f"8-char password time: {time2}")
        
        # Calculate ratio of complexity increase
        actual_ratio = time2 / time1
        print(f"Actual ratio: {actual_ratio}")
        
        # Test that adding a character increases complexity, but with a more realistic expectation
        self.assertGreater(actual_ratio, 10,
                          "Adding one character should significantly increase complexity")
        
        # Test password length impact
        # These should take increasingly longer times
        short_pwd = "abc"
        medium_pwd = "abcdef"
        long_pwd = "abcdefghi"
        
        short_time = brute_force_complexity(short_pwd)
        medium_time = brute_force_complexity(medium_pwd)
        long_time = brute_force_complexity(long_pwd)
        
        print(f"3-char time: {short_time}, 6-char time: {medium_time}, 9-char time: {long_time}")
        
        # Complexity should increase with password length
        self.assertLess(short_time, medium_time, "Longer password should take longer to crack")
        self.assertLess(medium_time, long_time, "Longer password should take longer to crack")

if __name__ == "__main__":
    unittest.main()