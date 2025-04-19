import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest import mock
from test_fine_tuned_model import generate_candidate_password, client

@pytest.fixture
def full_features():
    return {
        "MFCCs_mean": "1.0",
        "Spectral_Centroid_mean": "2.0",
        "Spectral_Contrast_mean": "3.0",
        "Tempo_mean": "4.0",
        "Beats_mean": "5.0",
        "Harmonic_Components_mean": "6.0",
        "Percussive_Components_mean": "7.0",
        "Zero_Crossing_Rate_mean": "8.0",
        "Chroma_Features_CENS_mean": "9.0"
    }

def test_generate_candidate_password_full_features(full_features):
    mock_response = mock.Mock()
    mock_response.choices = [mock.Mock(message=mock.Mock(content="StrongPassword123!"))]

    with mock.patch.object(client.chat.completions, "create", return_value=mock_response):
        result = generate_candidate_password(full_features, "mock-model")
        assert result == "StrongPassword123!"

def test_generate_candidate_password_with_missing_fields():
    partial = {"MFCCs_mean": "1.0"}  # All others will default to "N/A"
    mock_response = mock.Mock()
    mock_response.choices = [mock.Mock(message=mock.Mock(content="PartialPassword!"))]

    with mock.patch.object(client.chat.completions, "create", return_value=mock_response):
        result = generate_candidate_password(partial, "mock-model")
        assert result == "PartialPassword!"

def test_generate_candidate_password_with_empty_dict():
    mock_response = mock.Mock()
    mock_response.choices = [mock.Mock(message=mock.Mock(content="DefaultPassword!"))]

    with mock.patch.object(client.chat.completions, "create", return_value=mock_response):
        result = generate_candidate_password({}, "mock-model")
        assert result == "DefaultPassword!"

def test_generate_candidate_password_with_none_values():
    broken = {
        "MFCCs_mean": None,
        "Tempo_mean": None
    }
    mock_response = mock.Mock()
    mock_response.choices = [mock.Mock(message=mock.Mock(content="SafePass!"))]

    with mock.patch.object(client.chat.completions, "create", return_value=mock_response):
        result = generate_candidate_password(broken, "mock-model")
        assert result == "SafePass!"

def test_generate_candidate_password_raises_on_api_failure(full_features):
    with mock.patch.object(client.chat.completions, "create", side_effect=Exception("API failed")):
        with pytest.raises(Exception, match="API failed"):
            generate_candidate_password(full_features, "mock-model")

def test_generate_candidate_password_malformed_response(full_features):
    # simulate message being malformed (missing `content`)
    bad_message = mock.Mock()
    del bad_message.content  # removes the attribute so access throws AttributeError

    mock_choice = mock.Mock(message=bad_message)
    mock_response = mock.Mock(choices=[mock_choice])

    with mock.patch.object(client.chat.completions, "create", return_value=mock_response):
        with pytest.raises(AttributeError):
            generate_candidate_password(full_features, "mock-model")

def test_prompt_format_is_correct(full_features):
    with mock.patch.object(client.chat.completions, "create") as mock_create:
        mock_response = mock.Mock()
        mock_response.choices = [mock.Mock(message=mock.Mock(content="PromptCheck!"))]
        mock_create.return_value = mock_response

        generate_candidate_password(full_features, "mock-model")
        prompt = mock_create.call_args[1]["messages"][0]["content"]
        assert "- MFCC mean: 1.0" in prompt
        assert "Generate a secure access code." in prompt
