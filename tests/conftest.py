"""
Pytest configuration file for Sound-to-Security project tests.
This defines fixtures and configuration settings for all tests.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# Mock problematic modules that might be imported by multiple tests
def pytest_configure(config):
    """Configure the pytest environment before running tests."""
    # Mock tkinter and related modules
    tk_mock = MagicMock()
    tk_mock.NORMAL = 'normal'
    tk_mock.DISABLED = 'disabled'
    sys.modules['tkinter'] = tk_mock
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.simpledialog'] = MagicMock()
    
    # Optional: Mock other problematic modules for improved isolation
    # Only uncomment these if tests are having conflicts
    # sys.modules['sounddevice'] = MagicMock()
    # sys.modules['soundfile'] = MagicMock()
    # sys.modules['resemblyzer'] = MagicMock()
    
    # Ensure temp directories exist
    os.makedirs("./temp", exist_ok=True)
    os.makedirs("./backend/data", exist_ok=True)
    os.makedirs("./backend/logs", exist_ok=True)

@pytest.fixture(scope="function")
def temp_env_vars():
    """Fixture to provide isolated environment variables for tests."""
    # Save original environment
    original_env = os.environ.copy()
    
    # Setup temp environment
    os.environ["TEMP_DIR"] = "./temp"
    
    # Yield control to the test
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture(scope="function")
def mock_audio_file(tmpdir):
    """Fixture to provide a dummy audio file for tests."""
    # Create a temporary audio file
    audio_path = os.path.join(tmpdir, "test_audio.wav")
    with open(audio_path, 'wb') as f:
        f.write(b'dummy audio data')
    
    return audio_path

@pytest.fixture(scope="function")
def mock_claude():
    """Fixture to provide a mocked Claude API for tests."""
    with pytest.MonkeyPatch.context() as mp:
        # Mock the Claude API client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_content_block = MagicMock()
        mock_content_block.text = "AI_P@ssw0rd123!"
        mock_response.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_response
        
        mp.setattr("anthropic.Anthropic", lambda *args, **kwargs: mock_client)
        
        yield mock_client