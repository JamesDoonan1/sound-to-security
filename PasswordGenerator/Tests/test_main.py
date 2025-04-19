import sys, os
import json
import base64
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main

def test_summarize_array_basic():
    arr = np.array([2.0, 4.0, 6.0, 8.0])
    stats = main.summarize_array(arr)
    assert stats == {
        "mean": 5.0,
        "std": pytest.approx(2.23607, rel=1e-5),
        "min": 2.0,
        "max": 8.0
    }

def test_summarize_array_single_value():
    arr = np.array([42.0])
    stats = main.summarize_array(arr)
    assert stats["mean"] == 42.0
    assert stats["std"] == pytest.approx(0.0)
    assert stats["min"] == 42.0
    assert stats["max"] == 42.0

def test_summarize_array_negative_values():
    arr = np.array([-10, 0, 10])
    stats = main.summarize_array(arr)
    assert stats["mean"] == pytest.approx(0.0)
    assert stats["min"] == -10
    assert stats["max"] == 10

def test_summarize_array_empty_raises():
    with pytest.raises(ValueError):
        main.summarize_array(np.array([]))

class DummyPasswordGen:
    def __init__(self, result):
        self.result = result
        self.called = False
    def generate_password(self, features):
        self.called = True
        return self.result

@pytest.fixture(autouse=True)
def stub_dependencies(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "extract_features", lambda y, sr: {"feat": np.array([1, 2, 3])})
    monkeypatch.setattr(main, "create_hash", lambda feats: "HASH123")
    SALT = b"\x00" * 16
    monkeypatch.setattr(main, "new_salt", lambda: SALT)
    monkeypatch.setattr(main, "derive_key", lambda h, s: b"KEYBYTES")
    monkeypatch.setattr(main, "encrypt_password", lambda pw, key: pw[::-1])
    monkeypatch.setattr(main, "decrypt_password", lambda enc, key: enc[::-1])
    stored = {}
    def fake_store(username, audio_hash, salt, encrypted_password):
        stored['args'] = (username, audio_hash, salt, encrypted_password)
    monkeypatch.setattr(main, "store_encrypted_password", fake_store)
    yield stored

def test_process_audio_file_new_password(tmp_path, stub_dependencies):
    dummy_pg = DummyPasswordGen("MySecret!")
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(main, "get_encrypted_password_by_hash", lambda h: (None, None, None))
    out_json = tmp_path / "out.json"
    monkeypatch.setenv("OUTPUT_JSON_FILE", str(out_json))
    main.OUTPUT_JSON_FILE = str(out_json)
    main.audio_data_list = []
    main.USERNAME = "test_user"
    main.process_audio_file("file.mp3", None, None, dummy_pg, file_count=1)
    assert dummy_pg.called
    username, ahash, salt_b64, encrypted = stub_dependencies['args']
    assert username == "test_user"
    assert ahash == "HASH123"
    assert base64.b64decode(salt_b64) == b"\x00" * 16
    assert encrypted == "!terceSyM"
    data = json.loads(out_json.read_text())
    assert len(data) == 1
    assert data[0]["password"] == "MySecret!"
    monkeypatch.undo()

def test_process_audio_file_existing_password(tmp_path, stub_dependencies):
    dummy_pg = DummyPasswordGen("Unused")
    EXISTING_ENC = "!drowssaPdne"[::-1]
    SALT = b"\x00" * 16
    b64 = base64.b64encode(SALT).decode("utf-8")
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(main, "get_encrypted_password_by_hash", lambda h: ("user", b64, EXISTING_ENC))
    out_json = tmp_path / "out2.json"
    monkeypatch.setenv("OUTPUT_JSON_FILE", str(out_json))
    main.OUTPUT_JSON_FILE = str(out_json)
    main.audio_data_list = []
    main.USERNAME = "test_user"
    main.process_audio_file("file.mp3", None, None, dummy_pg, file_count=2)
    assert not dummy_pg.called
    assert stub_dependencies == {}
    data = json.loads(out_json.read_text())
    assert data[0]["password"] == "!drowssaPdne"
    monkeypatch.undo()

def test_process_audio_file_feature_extraction_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "extract_features", lambda y, sr: None)
    dummy_pg = DummyPasswordGen("ShouldNotBeCalled")
    main.audio_data_list = []
    main.OUTPUT_JSON_FILE = str(tmp_path / "fail.json")
    main.process_audio_file("file.mp3", None, None, dummy_pg, file_count=3)
    assert not os.path.exists(main.OUTPUT_JSON_FILE)

def test_process_audio_file_password_generation_fails(tmp_path, monkeypatch):
    class FailingGen:
        def __init__(self):
            self.called = False
        def generate_password(self, features):
            self.called = True
            return None
    monkeypatch.setattr(main, "get_encrypted_password_by_hash", lambda h: (None, None, None))
    gen = FailingGen()
    out_json = tmp_path / "fail_pw.json"
    monkeypatch.setenv("OUTPUT_JSON_FILE", str(out_json))
    main.OUTPUT_JSON_FILE = str(out_json)
    main.audio_data_list = []
    main.USERNAME = "test_user"
    main.process_audio_file("file.mp3", None, None, gen, file_count=4)
    assert gen.called
    data = json.loads(out_json.read_text())
    assert data[0]["password"] is None
    monkeypatch.undo()
