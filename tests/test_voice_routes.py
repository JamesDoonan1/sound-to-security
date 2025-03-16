import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from flask import Flask

# ✅ Fix import issues for pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

class TestVoiceRoutes(unittest.TestCase):
    """Test Flask routes for voice authentication"""

    def setUp(self):
        """Set up test Flask app and client"""
        from backend.routes.voice_routes import voice_routes

        self.app = Flask(__name__)
        self.app.register_blueprint(voice_routes)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('backend.routes.voice_routes.record_audio')
    @patch('backend.routes.voice_routes.save_voiceprint')
    def test_register_voice_success(self, mock_save_voiceprint, mock_record_audio):
        """Test successful voice registration"""
        mock_record_audio.return_value = (MagicMock(), 22050)  # Simulating recorded audio

        response = self.client.post('/api/register-voice')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('registered successfully', data['message'])

        mock_record_audio.assert_called_once()
        mock_save_voiceprint.assert_called_once_with("vocal_input.wav")

    @patch('backend.routes.voice_routes.record_audio', side_effect=Exception("Recording error"))
    def test_register_voice_error(self, mock_record_audio):
        """Test voice registration with error"""
        response = self.client.post('/api/register-voice')

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Recording error', data['error'])

        mock_record_audio.assert_called_once()

    @patch('backend.routes.voice_routes.verify_voice')
    def test_verify_voice_success(self, mock_verify_voice):
        """Test successful voice verification"""
        mock_verify_voice.return_value = True

        response = self.client.post('/api/verify-voice')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['verified'])
        self.assertIn('message', data)
        self.assertIn('Voice verified', data['message'])

        mock_verify_voice.assert_called_once_with("vocal_input.wav")

    @patch('backend.routes.voice_routes.verify_voice')
    def test_verify_voice_failure(self, mock_verify_voice):
        """Test voice verification when voice doesn't match"""
        mock_verify_voice.return_value = False

        response = self.client.post('/api/verify-voice')

        self.assertEqual(response.status_code, 401)  # Unauthorized
        data = json.loads(response.data)
        self.assertFalse(data['verified'])
        self.assertIn('message', data)
        self.assertIn('not recognized', data['message'])

        mock_verify_voice.assert_called_once_with("vocal_input.wav")

    @patch('backend.routes.voice_routes.verify_voice', side_effect=Exception("Verification error"))
    def test_verify_voice_error(self, mock_verify_voice):
        """Test voice verification with error"""
        response = self.client.post('/api/verify-voice')

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Verification error', data['error'])

        mock_verify_voice.assert_called_once_with("vocal_input.wav")

if __name__ == "__main__":
    unittest.main()
