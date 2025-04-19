import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import tempfile
import numpy as np
import pytest

import ui

def test_summarize_array_statistics():
    arr = np.array([1.0, 2.0, 3.0, 4.0])
    result = ui.summarize_array(arr)
    assert result["mean"] == 2.5
    assert result["std"] == pytest.approx(1.118, rel=1e-3)
    assert result["min"] == 1.0
    assert result["max"] == 4.0

def test_edit_distance_identical_strings():
    assert ui.edit_distance("password", "password") == 0

def test_edit_distance_differences():
    assert ui.edit_distance("abc", "yabc") == 1
    assert ui.edit_distance("pass", "past") == 1
    assert ui.edit_distance("abc", "abcd") == 1
    assert ui.edit_distance("abcd", "abc") == 1
    assert ui.edit_distance("Password", "password") == 1

def test_calculate_entropy_empty_string():
    assert ui.calculate_entropy("") == 0

def test_calculate_entropy_single_char():
    assert ui.calculate_entropy("aaaa") == 0

def test_calculate_entropy_uniform_string():
    assert pytest.approx(ui.calculate_entropy("abcd"), 0.01) == 2.0

def test_log_security_creates_and_appends():
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "log.json")
        ui.log_security_test_result({"first": 1}, log_filename=fpath)
        ui.log_security_test_result({"second": 2}, log_filename=fpath)
        with open(fpath) as f:
            results = json.load(f)
        assert isinstance(results, list)
        assert results[0]["first"] == 1
        assert results[1]["second"] == 2

def test_load_fine_tuned_model_id_default(monkeypatch):
    monkeypatch.setattr(ui, "project_folder", "/non/existing/folder")
    monkeypatch.setattr(os.path, "exists", lambda p: False)
    fallback = ui.load_fine_tuned_model_id()
    assert fallback.startswith("ft:gpt-4o")

def test_load_fine_tuned_model_id_reads(monkeypatch, tmp_path):
    file = tmp_path / "model_info_fold0.txt"
    file.write_text("ft:custom:test-id")
    monkeypatch.setattr(ui, "project_folder", str(tmp_path))
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr(os.path, "join", lambda a, b: str(file))
    model_id = ui.load_fine_tuned_model_id()
    assert model_id == "ft:custom:test-id"
