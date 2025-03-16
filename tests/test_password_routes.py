import unittest
import os
import sys
import json
from io import BytesIO
from unittest.mock import patch, MagicMock
from flask import Flask

# ✅ Dynamically adjust import paths for tests
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

if __name__ == "__main__":
    unittest.main()
