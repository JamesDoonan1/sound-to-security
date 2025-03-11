import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Flask test client
from flask import Flask
from flask.testing import FlaskClient

class TestVoiceRoutes(unittest.TestCase):
    """Test Flask routes for voice authentication"""
    
    def setUp(self):
        """Set up test Flask app and client"""
        from backend.routes.voice_routes import voice_routes
        
        # Create test Flask app
        self.app = Flask(__name__)
        self.app.register_blueprint(voice_routes)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('backend.routes.voice_routes.record_audio')
    @patch('backend.routes.voice_routes.save_voiceprint')
    def test_register_voice_success(self, mock_save_voiceprint, mock_record_audio):
        """Test successful voice registration"""
        # Configure mocks
        mock_record_audio.return_value = (MagicMock(), 22050)  # Return fake audio data
        
        # Make request
        response = self.client.post('/api/register-voice')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('message', data)
        self.assertIn('registered successfully', data['message'])
        
        # Verify mocks were called correctly
        mock_record_audio.assert_called_once()
        mock_save_voiceprint.assert_called_once_with("vocal_input.wav")
    
    @patch('backend.routes.voice_routes.record_audio')
    def test_register_voice_error(self, mock_record_audio):
        """Test voice registration with error"""
        # Configure mock to raise exception
        mock_record_audio.side_effect = Exception("Recording error")
        
        # Make request
        response = self.client.post('/api/register-voice')
        
        # Check response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        
        self.assertIn('error', data)
        self.assertIn('Recording error', data['error'])
        
        # Verify mock was called
        mock_record_audio.assert_called_once()
    
    @patch('backend.routes.voice_routes.verify_voice')
    def test_verify_voice_success(self, mock_verify_voice):
        """Test successful voice verification"""
        # Configure mock to return success
        mock_verify_voice.return_value = True
        
        # Make request
        response = self.client.post('/api/verify-voice')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['verified'])
        self.assertIn('message', data)
        self.assertIn('Voice verified', data['message'])
        
        # Verify mock was called correctly
        mock_verify_voice.assert_called_once_with("vocal_input.wav")
    
    @patch('backend.routes.voice_routes.verify_voice')
    def test_verify_voice_failure(self, mock_verify_voice):
        """Test voice verification when voice doesn't match"""
        # Configure mock to return failure
        mock_verify_voice.return_value = False
        
        # Make request
        response = self.client.post('/api/verify-voice')
        
        # Check response
        self.assertEqual(response.status_code, 401)  # Unauthorized
        data = json.loads(response.data)
        
        self.assertFalse(data['verified'])
        self.assertIn('message', data)
        self.assertIn('not recognized', data['message'])
        
        # Verify mock was called correctly
        mock_verify_voice.assert_called_once_with("vocal_input.wav")
    
    @patch('backend.routes.voice_routes.verify_voice')
    def test_verify_voice_error(self, mock_verify_voice):
        """Test voice verification with error"""
        # Configure mock to raise exception
        mock_verify_voice.side_effect = Exception("Verification error")
        
        # Make request
        response = self.client.post('/api/verify-voice')
        
        # Check response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        
        self.assertIn('error', data)
        self.assertIn('Verification error', data['error'])
        
        # Verify mock was called
        mock_verify_voice.assert_called_once_with("vocal_input.wav")

if __name__ == "__main__":
    unittest.main()