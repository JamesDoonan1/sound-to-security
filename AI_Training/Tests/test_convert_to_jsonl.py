import sys, os
import json
import pytest
import copy
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from convert_to_jsonl import build_prompt_text, convert_to_jsonl

@pytest.fixture
def valid_entry():
    return {
        "features": {
            "MFCCs": {"mean": 1.0},
            "Spectral Centroid": {"mean": 2.0},
            "Spectral Contrast": {"mean": 3.0},
            "Tempo": {"mean": 4.0},
            "Beats": {"mean": 5.0},
            "Harmonic Components": {"mean": 6.0},
            "Percussive Components": {"mean": 7.0},
            "Zero-Crossing Rate": {"mean": 8.0},
            "Chroma Features (CENS)": {"mean": 9.0},
        },
        "hash": "abc123",
        "password": "Secret!1"
    }

def test_prompt_formatting(valid_entry):
    prompt = build_prompt_text(valid_entry)
    assert "- MFCC mean: 1.0" in prompt
    assert "- Chroma Features (CENS) mean: 9.0" in prompt
    assert "Generate the corresponding identifier" in prompt

def test_conversion_valid_output(tmp_path, valid_entry):
    test_data = [valid_entry.copy() for _ in range(10)]
    input_path = tmp_path / "audio_data.json"
    with open(input_path, "w") as f:
        json.dump(test_data, f)

    out_train = tmp_path / "train.jsonl"
    out_val = tmp_path / "val.jsonl"

    convert_to_jsonl(str(input_path), str(out_train), str(out_val))

    assert (tmp_path / "train_fold0.jsonl").exists()
    assert (tmp_path / "val_fold0.jsonl").exists()

    with open(tmp_path / "train_fold0.jsonl") as f:
        lines = f.readlines()
        assert len(lines) == 9  # 90% of 10
        assert all("Identifier: abc123" in json.loads(line)["messages"][1]["content"] for line in lines)

    with open(tmp_path / "val_fold0.jsonl") as f:
        lines = f.readlines()
        assert len(lines) == 1

def test_filtering_removes_incomplete_entries(tmp_path, valid_entry):
    incomplete_entry = copy.deepcopy(valid_entry)
    del incomplete_entry["features"]["Beats"]

    input_data = [valid_entry] * 5 + [incomplete_entry] * 5
    input_path = tmp_path / "audio_data.json"
    with open(input_path, "w") as f:
        json.dump(input_data, f)

    convert_to_jsonl(str(input_path), str(tmp_path / "train.jsonl"), str(tmp_path / "val.jsonl"))

    with open(tmp_path / "train_fold0.jsonl") as f:
        lines = f.readlines()
        assert len(lines) + len(open(tmp_path / "val_fold0.jsonl").readlines()) == 5

def test_handles_empty_file_gracefully(tmp_path):
    input_path = tmp_path / "audio_data.json"
    input_path.write_text("[]")

    convert_to_jsonl(str(input_path), str(tmp_path / "train.jsonl"), str(tmp_path / "val.jsonl"))

    assert Path(tmp_path / "train_fold0.jsonl").read_text().strip() == ""
    assert Path(tmp_path / "val_fold0.jsonl").read_text().strip() == ""

def test_handles_malformed_json(tmp_path, capsys):
    bad_path = tmp_path / "corrupt.json"
    bad_path.write_text("{ this is not valid json ")

    convert_to_jsonl(str(bad_path), str(tmp_path / "train.jsonl"), str(tmp_path / "val.jsonl"))

    out = capsys.readouterr().out
    assert "Error processing data" in out
