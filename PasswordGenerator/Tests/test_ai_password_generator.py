import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np

import ai_password_generator
from ai_password_generator import AIPasswordGenerator

# Helpers to fake the OpenAI response
class DummyChoice:
    def __init__(self, content):
        # Mimic the .message.content structure
        self.message = type("M", (), {"content": content})

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

def test_format_features_high_brightness_rich_harmonic():
    gen = AIPasswordGenerator()
    features = {
        "MFCCs": np.array([1.0, 2.0]),
        "Spectral Centroid": np.array([3000.0]),
        "Tempo": np.array([130.0]),
        "Beats": np.arange(150)
    }
    desc = gen._format_features_for_prompt(features)
    assert "- Bright, high-frequency tones" in desc
    assert "- Rich harmonic profile" in desc
    assert "Energetic tempo (130.00 BPM)" in desc
    assert "- Many beats" in desc

def test_format_features_low_brightness_darker_profile():
    gen = AIPasswordGenerator()
    features = {
        "MFCCs": np.array([-1.0, -2.0]),
        "Spectral Centroid": np.array([1000.0]),
        "Tempo": np.array([80.0]),
        "Beats": np.arange(50)
    }
    desc = gen._format_features_for_prompt(features)
    assert "- Mellow, low-frequency tones" in desc
    assert "- Darker harmonic profile" in desc
    assert "Relaxed tempo (80.00 BPM)" in desc
    assert "- Few beats" in desc

def test_format_features_mixed_cases():
    # borderline: mean_spectral_centroid exactly 2000, mean_mfcc = 0, tempo = 120, beats = 100
    gen = AIPasswordGenerator()
    features = {
        "MFCCs": np.array([0.0, 0.0]),
        "Spectral Centroid": np.array([2000.0, 2000.0]),
        "Tempo": np.array([120.0]),
        "Beats": np.arange(100)
    }
    desc = gen._format_features_for_prompt(features)
    # Spectral Centroid <=2000 should go mellow
    assert "- Mellow, low-frequency tones" in desc
    # MFCC == 0 → treated as darker profile
    assert "- Darker harmonic profile" in desc
    # Tempo ==120 → relaxed
    assert "Relaxed tempo (120.00 BPM)" in desc
    # Beats ==100 → few beats
    assert "- Few beats" in desc

def test_generate_password_success(monkeypatch):
    dummy_pw = "AbcdEf12#Gh"  # 12 chars
    def fake_create(model, messages, temperature, top_p, frequency_penalty, presence_penalty):
        assert model == "gpt-4o"
        assert messages[0]["role"] == "system"
        assert "Generate a secure password that reflects these audio characteristics" in messages[1]["content"]
        return DummyResponse(dummy_pw)

    monkeypatch.setattr(
        ai_password_generator.client.chat.completions,
        "create",
        fake_create
    )

    features = {
        "MFCCs": np.zeros(1),
        "Spectral Centroid": np.zeros(1),
        "Tempo": np.array([120.0]),
        "Beats": np.zeros(0, dtype=int)
    }
    gen = AIPasswordGenerator()
    pw = gen.generate_password(features)
    assert pw == dummy_pw

def test_generate_password_api_error(monkeypatch, capsys):
    def fake_raise(*args, **kwargs):
        raise RuntimeError("API failure")

    monkeypatch.setattr(
        ai_password_generator.client.chat.completions,
        "create",
        fake_raise
    )

    gen = AIPasswordGenerator()
    # supply minimal valid features so formatting succeeds
    features = {
        "MFCCs": np.zeros(1),
        "Spectral Centroid": np.zeros(1),
        "Tempo": np.array([120.0]),
        "Beats": np.zeros(0, dtype=int)
    }
    pw = gen.generate_password(features)
    captured = capsys.readouterr()
    assert pw is None
    assert "Error generating password: API failure" in captured.out
