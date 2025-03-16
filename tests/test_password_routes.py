import unittest
import os
import sys
import json
from io import BytesIO
from unittest.mock import patch, MagicMock
from flask import Flask

# ✅ Fix import issues for pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

class TestPasswordRoutes(unittest.TestCase):
    """Test Flask routes for password generation and testing"""

    def setUp(self):
        """Set up test Flask app and client"""
        from backend.routes.passwords_routes import passwords_routes

        self.app = Flask(__name__)
        self.app.register_blueprint(passwords_routes)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('backend.routes.passwords_routes.process_audio_and_generate_password')
    def test_generate_password_success(self, mock_process_audio):
        """Test successful password generation"""
        mock_process_audio.return_value = {
            'ai_password': 'AI_P@ssw0rd!',
            'traditional_passwords': ['Trad1P@ss!', 'Trad2P@ss!'],
            'comparison': [
                {'Type': 'AI-Generated', 'Password': 'AI_P@ssw0rd!', 'Entropy': 75.0},
                {'Type': 'Traditional', 'Password': 'Trad1P@ss!', 'Entropy': 70.0}
            ]
        }

        response = self.client.post(
            '/api/generate-password',
            data={'audio': (BytesIO(b'fake audio data'), 'test_audio.wav')},
            content_type='multipart/form-data'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['ai_password'], 'AI_P@ssw0rd!')
        mock_process_audio.assert_called_once()

    @patch('backend.routes.passwords_routes.process_audio_and_generate_password', side_effect=Exception("Processing error"))
    def test_generate_password_error(self, mock_process_audio):
        """Test error handling when password generation fails"""
        response = self.client.post('/api/generate-password',
                                    data={'audio': (BytesIO(b'fake audio data'), 'test_audio.wav')},
                                    content_type='multipart/form-data')

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Processing error", data["error"])

    @patch('backend.routes.passwords_routes.test_password_with_gpt')
    def test_test_password_gpt(self, mock_test_gpt):
        """Test GPT password security evaluation"""
        mock_test_gpt.return_value = {
            'cracked': False,
            'time': '2.50s',
            'attempts': ['Guess1', 'Guess2', 'Guess3'],
            'message': 'Failed to crack password'
        }

        response = self.client.post('/api/test-password', json={'password': 'TestP@ss!', 'test_type': 'gpt'},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertFalse(result['cracked'])
        mock_test_gpt.assert_called_once()

    @patch('backend.routes.passwords_routes.ai_crack_password')
    def test_test_password_claude(self, mock_ai_crack):
        """Test Claude AI password security evaluation"""
        mock_ai_crack.return_value = {
            'cracked': False,
            'message': 'AI generated similar passwords.',
            'attempts': ['C1@ud3Guess1!', 'C1@ud3Guess2!']
        }

        response = self.client.post('/api/test-password', json={'password': 'TestP@ss!', 'test_type': 'claude'},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertFalse(result['cracked'])
        self.assertEqual(len(result['attempts']), 2)
        mock_ai_crack.assert_called_once_with('TestP@ss!')

    @patch('backend.routes.passwords_routes.brute_force_crack')
    def test_test_password_brute_force(self, mock_brute_force):
        """Test brute force password security evaluation"""
        mock_brute_force.return_value = {
            'cracked': False,
            'message': 'Brute force timed out'
        }

        response = self.client.post('/api/test-password', json={'password': 'TestP@ss!', 'test_type': 'brute'},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertFalse(result['cracked'])
        self.assertEqual(result['message'], 'Brute force timed out')
        mock_brute_force.assert_called_once_with('TestP@ss!')

    @patch('backend.routes.passwords_routes.extract_voice_features', return_value=None)
    def test_test_password_missing_voice_features(self, mock_extract_voice):
        """Test error handling when voice features are missing"""
        response = self.client.post('/api/test-password', json={'password': 'TestP@ss!', 'test_type': 'gpt'},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Missing voice features", data["error"])

    @patch('backend.routes.passwords_routes.crack_password_with_hashcat')
    def test_test_password_with_hashcat(self, mock_crack_hashcat):
        """Test Hashcat password cracking endpoint"""
        mock_crack_hashcat.return_value = (True, "password123")

        response = self.client.post('/api/test-password-hashcat',
                                    json={'password_hash': '5f4dcc3b5aa765d61d8327deb882cf99', 'hash_type': '0',
                                          'attack_mode': '3'},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['cracked'])
        self.assertEqual(result['result'], "password123")
        mock_crack_hashcat.assert_called_once_with('0', '3', '5f4dcc3b5aa765d61d8327deb882cf99')

if __name__ == "__main__":
    unittest.main()
