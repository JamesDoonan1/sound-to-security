import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest import mock
from ai_fine_tune import (
    validate_api_key,
    check_file_paths,
    upload_file,
    start_fine_tuning,
    save_model_id,
    run_pipeline
)

@mock.patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"})
def test_validate_api_key_passes():
    validate_api_key()

@mock.patch.dict(os.environ, {}, clear=True)
def test_validate_api_key_fails():
    with pytest.raises(EnvironmentError):
        validate_api_key()

def test_check_file_paths_success(tmp_path):
    train = tmp_path / "train.jsonl"
    val = tmp_path / "val.jsonl"
    train.write_text("data")
    val.write_text("data")
    assert check_file_paths(str(train), str(val)) is True

def test_check_file_paths_missing_file(tmp_path):
    train = tmp_path / "train.jsonl"
    with pytest.raises(FileNotFoundError):
        check_file_paths(str(train), str(tmp_path / "val.jsonl"))

@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="fake")
@mock.patch("openai.files.create")
def test_upload_file_calls_openai(mock_create, mock_open_file):
    upload_file("some/path.jsonl")
    mock_create.assert_called_once()

@mock.patch("openai.fine_tuning.jobs.create")
def test_start_fine_tuning_calls_api(mock_create):
    start_fine_tuning("train-id", "val-id")
    mock_create.assert_called_once_with(
        training_file="train-id",
        validation_file="val-id",
        model="gpt-4o-2024-08-06"
    )

def test_save_model_id_writes_file(tmp_path):
    file_path = tmp_path / "model_info.txt"
    save_model_id("job-123", str(file_path))
    assert file_path.read_text() == "job-123"

@mock.patch("ai_fine_tune.upload_file")
@mock.patch("ai_fine_tune.save_model_id")
@mock.patch("ai_fine_tune.start_fine_tuning")
@mock.patch("ai_fine_tune.check_file_paths")
@mock.patch("ai_fine_tune.validate_api_key")
def test_run_pipeline_success(mock_validate, mock_check, mock_start, mock_save, mock_upload, tmp_path):
    mock_upload.return_value.id = "file-id"
    mock_start.return_value.id = "model-id"
    
    train = tmp_path / "train_data_fold0.jsonl"
    val = tmp_path / "val_data_fold0.jsonl"
    train.write_text("dummy")
    val.write_text("dummy")
    
    model_id = run_pipeline(str(tmp_path), fold=0)
    assert model_id == "model-id"
