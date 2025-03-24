"""
Utility functions for testing the Sound-to-Security project.
"""
import os
import sys
import numpy as np
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Tuple, Optional

def setup_mock_voice_features() -> np.ndarray:
    """
    Set up mock voice features for testing.
    
    Returns:
        A numpy array with mock voice features
    """
    return np.array([120.5, 2500.75, 95.0], dtype=np.float32)

def setup_mock_audio() -> Tuple[np.ndarray, int]:
    """
    Set up mock audio data for testing.
    
    Returns:
        A tuple of (audio_data, sample_rate)
    """
    return np.zeros(1000), 22050

def setup_mock_password_response() -> Dict[str, Any]:
    """
    Set up a mock response for password generation.
    
    Returns:
        A dictionary with the expected API response
    """
    return {
        'ai_password': 'AI_P@ssw0rd123!',
        'traditional_passwords': [
            'Trad1P@ss!', 'Trad2P@ss!', 'Trad3P@ss!', 
            'Trad4P@ss!', 'Trad5P@ss!', 'Trad6P@ss!',
            'Trad7P@ss!', 'Trad8P@ss!', 'Trad9P@ss!', 'Trad10P@ss!'
        ],
        'comparison': [
            {'Type': 'AI-Generated', 'Password': 'AI_P@ssw0rd123!', 'Entropy': 75.0, 'Brute-Force Time (s)': 1000000},
            {'Type': 'Traditional', 'Password': 'Trad1P@ss!', 'Entropy': 70.0, 'Brute-Force Time (s)': 800000}
        ]
    }

def patch_password_test_modules():
    """
    Create patches for commonly used modules in password testing.
    
    Returns:
        A list of patches that can be used in a with statement
    """
    patches = [
        patch('librosa.load'),
        patch('models.claude_password_generator.generate_password_with_claude'),
        patch('vocal_passwords.feature_extraction.extract_audio_features'),
        patch('backend.services.passwords_service.generate_password_with_claude'),
        patch('requests.post')
    ]
    return patches

def apply_mock_gui_elements(gui_module: Any):
    """
    Apply mock elements to the GUI module.
    
    Args:
        gui_module: The frontend.gui module to modify
    """
    gui_module.result_label = MagicMock()
    gui_module.test_button = MagicMock()
    gui_module.compare_button = MagicMock()
    gui_module.generate_button = MagicMock()
    
    # Mock methods that would access files
    gui_module.save_hashed_password = MagicMock()
    gui_module.save_voiceprint = MagicMock()
    gui_module.save_passphrase = MagicMock()
    gui_module.load_password = MagicMock(return_value="AI_P@ssw0rd123!")
    gui_module.verify_passphrase = MagicMock(return_value=True)

def mock_api_response(status_code: int = 200, json_data: Optional[Dict] = None) -> MagicMock:
    """
    Create a mock API response object.
    
    Args:
        status_code: HTTP status code to return
        json_data: JSON data to return
        
    Returns:
        A mock response object
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    
    if json_data:
        mock_response.json.return_value = json_data
    
    return mock_response

def create_test_files(file_paths: List[str]):
    """
    Create empty test files for testing.
    
    Args:
        file_paths: List of file paths to create
    """
    for path in file_paths:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Create empty file
        with open(path, 'w') as f:
            f.write("")