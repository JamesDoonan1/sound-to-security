import pytest
import os, sys
import random
import string
import time
import numpy as np
from unittest.mock import patch

# Import your modules
sys.path.append('/home/cormacgeraghty/Desktop/Project Code/sound-to-security/PasswordGenerator')

# Import your modules
from symmetric_key_generation import derive_key, new_salt
from encrypt_decrypt_password import encrypt_password, decrypt_password
from hash_password_generator import create_hash
from ai_password_generator import AIPasswordGenerator
from audio_feature_extraction import extract_features

# Helper functions for testing
def generate_random_password(length=12):
    """Generate a random password for testing purposes."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def create_mock_audio_features():
    """Create mock audio features for testing purposes."""
    features = {
        "MFCCs": np.random.rand(13),
        "Spectral Centroid": np.random.rand(100),
        "Spectral Contrast": np.random.rand(100),
        "Tempo": np.array([random.uniform(60, 180)]),
        "Beats": np.random.rand(100),
        "Harmonic Components": np.random.rand(100),
        "Percussive Components": np.random.rand(100),
        "Zero-Crossing Rate": np.random.rand(100),
        "Chroma Features (CENS)": np.random.rand(100)
    }
    return features

# Test suite for cryptographic operations
class TestCryptographicSecurity:
    
    def test_salt_uniqueness(self):
        """Test that salts are always unique."""
        # Generate multiple salts and ensure they're all unique
        salts = [new_salt() for _ in range(100)]
        assert len(set(salts)) == 100, "Salt values should always be unique"
        
    def test_salt_length(self):
        """Test that salt has the correct length."""
        salt = new_salt()
        assert len(salt) == 16, "Default salt length should be 16 bytes"
        
        # Test with custom length
        salt = new_salt(length=24)
        assert len(salt) == 24, "Custom salt length should be respected"
        
    def test_key_derivation_strength(self):
        """Test that the derived key has sufficient strength."""
        salt = new_salt()
        key = derive_key("test_hash", salt)
        
        # Check key length (32 bytes = 256 bits for Fernet)
        assert len(key) == 44, "Derived key should be 44 bytes when base64 encoded"
        
        # Check that different hashes produce different keys with the same salt
        key2 = derive_key("different_hash", salt)
        assert key != key2, "Different hashes should produce different keys"
        
    def test_key_derivation_consistency(self):
        """Test that key derivation is consistent for the same inputs."""
        salt = new_salt()
        hash_value = "test_hash"
        
        key1 = derive_key(hash_value, salt)
        key2 = derive_key(hash_value, salt)
        
        assert key1 == key2, "Key derivation should be deterministic for the same inputs"
        
    def test_encryption_decryption_roundtrip(self):
        """Test that encryption and decryption work correctly as a pair."""
        password = "T3st!P@ssw0rd"
        salt = new_salt()
        key = derive_key("test_hash", salt)
        
        encrypted = encrypt_password(password, key)
        decrypted = decrypt_password(encrypted, key)
        
        assert decrypted == password, "Decryption should recover the original password"
        
    def test_encryption_produces_different_outputs(self):
        """Test that encrypting the same password twice produces different outputs."""
        password = "SamePassword123!"
        salt = new_salt()
        key = derive_key("test_hash", salt)
        
        encrypted1 = encrypt_password(password, key)
        encrypted2 = encrypt_password(password, key)
        
        assert encrypted1 != encrypted2, "Encryption should use a random nonce for each call"
        
    def test_wrong_key_fails_decryption(self):
        """Test that using a wrong key fails the decryption process."""
        password = "T3st!P@ssw0rd"
        salt1 = new_salt()
        salt2 = new_salt()
        key1 = derive_key("test_hash", salt1)
        key2 = derive_key("test_hash", salt2)
        
        encrypted = encrypt_password(password, key1)
        
        with pytest.raises(Exception):
            decrypt_password(encrypted, key2)
            
    def test_modified_ciphertext_fails_decryption(self):
        """Test that tampering with the ciphertext causes decryption to fail."""
        password = "T3st!P@ssw0rd"
        salt = new_salt()
        key = derive_key("test_hash", salt)
        
        encrypted = encrypt_password(password, key)
        
        # Modify the encrypted text slightly
        modified = encrypted[:-1] + ('0' if encrypted[-1] != '0' else '1')
        
        with pytest.raises(Exception):
            decrypt_password(modified, key)


# Test suite for hash generation
class TestHashGeneration:
    
    def test_hash_determinism(self):
        """Test that the same features always produce the same hash."""
        features = create_mock_audio_features()
        
        hash1 = create_hash(features)
        hash2 = create_hash(features)
        
        assert hash1 == hash2, "Hash generation should be deterministic for the same features"
        
    def test_hash_uniqueness(self):
        """Test that different features produce different hashes."""
        features1 = create_mock_audio_features()
        features2 = create_mock_audio_features()
        
        hash1 = create_hash(features1)
        hash2 = create_hash(features2)
        
        assert hash1 != hash2, "Different features should produce different hashes"
        
    def test_hash_format(self):
        """Test that the hash has the correct format (MD5)."""
        features = create_mock_audio_features()
        hash_value = create_hash(features)
        
        # MD5 hashes are 32 hex characters
        assert len(hash_value) == 32, "Hash should be 32 characters long (MD5)"
        assert all(c in string.hexdigits for c in hash_value), "Hash should contain only hex digits"


# Test suite for password generation
class TestPasswordGeneration:
    
    @pytest.fixture
    def ai_password_generator(self):
        """Fixture to provide an AIPasswordGenerator instance."""
        return AIPasswordGenerator()
    
    @patch('ai_password_generator.AIPasswordGenerator._format_features_for_prompt')
    @patch('openai.OpenAI')
    def test_password_generation(self, mock_openai, mock_format, ai_password_generator):
        """Test that password generation produces a valid password."""
        # Mock the OpenAI response
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value.choices[0].message.content = "St@ongP4ss123"
        
        # Mock the feature formatting
        mock_format.return_value = "Formatted features"
        
        features = create_mock_audio_features()
        password = ai_password_generator.generate_password(features)
        
        assert password is not None, "Password generation should not return None"
        assert len(password) >= 8, "Password should be at least 8 characters long"
        
    def test_feature_formatting(self, ai_password_generator):
        """Test that audio features are correctly formatted for the prompt."""
        features = create_mock_audio_features()
        formatted = ai_password_generator._format_features_for_prompt(features)
        
        assert "audio characteristics" in formatted.lower(), "Formatted features should describe audio characteristics"
        assert isinstance(formatted, str), "Formatted features should be a string"


# Test suite for password strength
class TestPasswordStrength:
    
    def calculate_entropy(self, password):
        """Calculate password entropy."""
        # Count which character sets are used
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_symbols = any(not c.isalnum() for c in password)
        
        # Determine character set size
        char_set_size = 0
        if has_uppercase: char_set_size += 26
        if has_lowercase: char_set_size += 26
        if has_digits: char_set_size += 10
        if has_symbols: char_set_size += 33
        
        if char_set_size == 0:
            char_set_size = 95  # Default to ASCII printable
        
        # Calculate entropy
        return len(password) * (len(password) > 0) * (char_set_size > 0) * np.log2(char_set_size)
    
    @patch('ai_password_generator.AIPasswordGenerator._format_features_for_prompt')
    @patch('openai.OpenAI')
    def test_password_entropy(self, mock_openai, mock_format):
        """Test that generated passwords have sufficient entropy."""
        # Mock the OpenAI response with a deliberately strong password
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value.choices[0].message.content = "St@ongP4ss123"
        
        # Mock the feature formatting
        mock_format.return_value = "Formatted features"
        
        # Generate a password
        generator = AIPasswordGenerator()
        features = create_mock_audio_features()
        password = generator.generate_password(features)
        
        # Calculate entropy
        entropy = self.calculate_entropy(password)
        
        # A strong password should have at least 60 bits of entropy
        assert entropy >= 60, f"Password entropy ({entropy}) should be at least 60 bits"
    
    @patch('ai_password_generator.AIPasswordGenerator._format_features_for_prompt')
    @patch('openai.OpenAI')
    def test_password_character_diversity(self, mock_openai, mock_format):
        """Test that generated passwords use diverse character classes."""
        # Mock the OpenAI response
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.return_value.choices[0].message.content = "St@ongP4ss123"
        
        # Mock the feature formatting
        mock_format.return_value = "Formatted features"
        
        # Generate a password
        generator = AIPasswordGenerator()
        features = create_mock_audio_features()
        password = generator.generate_password(features)
        
        # Check character diversity
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digits = any(c.isdigit() for c in password)
        has_symbols = any(not c.isalnum() for c in password)
        
        assert has_uppercase, "Password should contain uppercase letters"
        assert has_lowercase, "Password should contain lowercase letters"
        assert has_digits, "Password should contain digits"
        assert has_symbols, "Password should contain special characters"


# Test suite for timing attacks
class TestTimingAttackResistance:
    
    def test_constant_time_key_derivation(self):
        """Test that key derivation runs in relatively constant time."""
        # Skip this test for CI environments since timing can be unreliable
        if os.environ.get("CI") == "true":
            pytest.skip("Skipping timing test in CI environment")
        
        # Create two hashes of different lengths
        short_hash = "a" * 10
        long_hash = "a" * 1000
        salt = new_salt()
        
        # Measure time for short hash (multiple times to reduce noise)
        short_times = []
        for _ in range(10):
            start = time.perf_counter()
            derive_key(short_hash, salt)
            end = time.perf_counter()
            short_times.append(end - start)
        
        # Measure time for long hash
        long_times = []
        for _ in range(10):
            start = time.perf_counter()
            derive_key(long_hash, salt)
            end = time.perf_counter()
            long_times.append(end - start)
        
        # Calculate averages
        avg_short = sum(short_times) / len(short_times)
        avg_long = sum(long_times) / len(long_times)
        
        # The times should be similar despite different input lengths
        # Allow for some variation due to system noise
        assert abs(avg_short - avg_long) / max(avg_short, avg_long) < 0.3, \
            "Key derivation time should not vary significantly with input length"
    
    def test_decryption_timing_consistency(self):
        """Test that decryption runs in relatively constant time."""
        # Skip this test for CI environments
        if os.environ.get("CI") == "true":
            pytest.skip("Skipping timing test in CI environment")
        
        password = "TestPassword123!"
        salt = new_salt()
        key = derive_key("test_hash", salt)
        encrypted = encrypt_password(password, key)
        
        # Measure time for successful decryption
        success_times = []
        for _ in range(10):
            start = time.perf_counter()
            try:
                decrypt_password(encrypted, key)
            except:
                pass
            end = time.perf_counter()
            success_times.append(end - start)
        
        # Measure time for failed decryption (with wrong key)
        wrong_key = derive_key("wrong_hash", salt)
        failure_times = []
        for _ in range(10):
            start = time.perf_counter()
            try:
                decrypt_password(encrypted, wrong_key)
            except:
                pass
            end = time.perf_counter()
            failure_times.append(end - start)
        
        # Calculate averages
        avg_success = sum(success_times) / len(success_times)
        avg_failure = sum(failure_times) / len(failure_times)
        
        # The times should be similar whether decryption succeeds or fails
        # Allow for some variation due to system noise
        assert abs(avg_success - avg_failure) / max(avg_success, avg_failure) < 0.5, \
            "Decryption time should not vary significantly between success and failure"


# Test suite for audio feature extraction security
class TestFeatureExtractionSecurity:
    
    @patch('librosa.feature.mfcc')
    @patch('librosa.feature.spectral_centroid')
    @patch('librosa.feature.spectral_contrast')
    @patch('librosa.beat.beat_track')
    @patch('librosa.effects.hpss')
    @patch('librosa.feature.zero_crossing_rate')
    @patch('librosa.feature.chroma_cens')
    def test_feature_extraction_handles_extreme_values(
        self, mock_chroma, mock_zcr, mock_hpss, mock_beat, 
        mock_contrast, mock_centroid, mock_mfcc
    ):
        """Test that feature extraction handles extreme audio values safely."""
        # Mock all librosa functions to return arrays
        mock_mfcc.return_value = np.random.rand(13, 100)
        mock_centroid.return_value = np.random.rand(1, 100)
        mock_contrast.return_value = np.random.rand(7, 100)
        mock_beat.return_value = (120.0, np.array([1, 2, 3]))
        mock_hpss.return_value = (np.random.rand(100), np.random.rand(100))
        mock_zcr.return_value = np.random.rand(1, 100)
        mock_chroma.return_value = np.random.rand(12, 100)
        
        # Create extreme audio values
        y = np.array([1e10, -1e10, np.nan, np.inf, -np.inf, 0, 0, 0])
        sr = 44100
        
        # This should not raise an exception
        features = extract_features(y, sr)
        
        assert features is not None, "Feature extraction should handle extreme values gracefully"
        
    def test_feature_extraction_with_empty_audio(self):
        """Test that feature extraction handles empty audio safely."""
        # Empty audio array
        y = np.array([])
        sr = 44100
        
        # This should not raise an exception, but return None
        features = extract_features(y, sr)
        
        assert features is None, "Feature extraction should return None for empty audio"


# Test suite for database security
class TestDatabaseSecurity:
    
    @patch('database_control.sqlite3.connect')
    def test_sql_injection_prevention(self, mock_connect):
        """Test that database operations are resistant to SQL injection."""
        from database_control import store_encrypted_password, get_encrypted_password_by_hash
        
        # Create a mock cursor and connection
        mock_cursor = mock_connect.return_value.execute
        mock_connect.return_value.commit = lambda: None
        mock_connect.return_value.close = lambda: None
        
        # Set up the mock cursor to return None for any query
        mock_connect.return_value.execute.return_value.fetchone = lambda: None
        
        # Attempt SQL injection in the username
        malicious_username = "'; DROP TABLE hash_passwords; --"
        audio_hash = "legitimate_hash"
        salt = "legitimate_salt"
        encrypted_password = "legitimate_encrypted_password"
        
        # This should safely escape the input
        store_encrypted_password(malicious_username, audio_hash, salt, encrypted_password)
        
        # Check that the SQL was parameterized (no string concatenation)
        args = mock_cursor.call_args[0]
        assert "?" in args[0], "SQL query should use parameterized queries"
        assert malicious_username in args[1], "Username should be passed as a parameter"
        
        # Test get_encrypted_password_by_hash with potential injection
        malicious_hash = "' OR '1'='1"
        get_encrypted_password_by_hash(malicious_hash)
        
        # Check that the SQL was parameterized
        args = mock_cursor.call_args[0]
        assert "?" in args[0], "SQL query should use parameterized queries"
        assert malicious_hash in args[1], "Hash should be passed as a parameter"