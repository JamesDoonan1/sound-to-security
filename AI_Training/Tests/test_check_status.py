import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import check_status
from unittest import mock

# --- Test: Missing API key should trigger error and exit ---
@mock.patch("check_status.openai.api_key", None)
@mock.patch.dict(os.environ, {}, clear=True)
def test_api_key_missing(capsys):
    with pytest.raises(SystemExit):
        check_status.validate_api_key()

    captured = capsys.readouterr()
    assert "OPENAI_API_KEY is not set" in captured.out


# --- Test: Successful model status output ---
@mock.patch("check_status.openai.fine_tuning.jobs.retrieve")
def test_status_output(mock_retrieve, tmp_path, capsys):
    mock_job = mock.Mock()
    mock_job.id = "ft-123"
    mock_job.status = "succeeded"
    mock_job.fine_tuned_model = "ft:gpt-4-custom"
    mock_job.created_at = 1710000000
    mock_job.training_file = "file-train123"
    mock_job.validation_file = "file-val123"
    mock_job.model = "gpt-4o"
    mock_job.error = None
    mock_retrieve.return_value = mock_job

    model_file = tmp_path / "model_info_fold0.txt"
    model_file.write_text("ft-123")

    check_status.check_fine_tune_status(model_id_path=str(model_file))

    output = capsys.readouterr().out
    assert "Job ID:           ft-123" in output
    assert "Status:           succeeded" in output
    assert "Model: ft:gpt-4-custom" in output


# --- Test: Missing model ID file should exit cleanly ---
def test_missing_model_file(tmp_path, capsys):
    model_path = tmp_path / "model_info_fold0.txt"

    with pytest.raises(SystemExit):
        check_status.check_fine_tune_status(model_id_path=str(model_path))

    output = capsys.readouterr().out
    assert "Model ID file" in output and "not found" in output


# --- Test: OpenAI API failure is handled gracefully ---
@mock.patch("check_status.openai.fine_tuning.jobs.retrieve")
def test_api_failure(mock_retrieve, tmp_path, capsys):
    mock_retrieve.side_effect = Exception("API failure")

    model_file = tmp_path / "model_info_fold0.txt"
    model_file.write_text("ft-bad")

    with pytest.raises(SystemExit):
        check_status.check_fine_tune_status(model_id_path=str(model_file))

    output = capsys.readouterr().out
    assert "Error retrieving job status: API failure" in output
