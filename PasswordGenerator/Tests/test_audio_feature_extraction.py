import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np

from audio_feature_extraction import extract_features

def make_sine(duration=1.0, sr=22050, freq=440.0):
    """
    Generate a simple sine wave at given frequency.
    """
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * freq * t)
    return y, sr

def test_extract_features_keys_and_types():
    y, sr = make_sine()
    feats = extract_features(y, sr)
    assert isinstance(feats, dict)

    expected_keys = {
        "MFCCs",
        "Spectral Centroid",
        "Spectral Contrast",
        "Tempo",
        "Beats",
        "Harmonic Components",
        "Percussive Components",
        "Zero-Crossing Rate",
        "Chroma Features (CENS)",
    }
    assert set(feats.keys()) == expected_keys

    # Every feature should be a 1D numpy array
    for key, arr in feats.items():
        assert isinstance(arr, np.ndarray), f"{key} is not an ndarray"
        assert arr.ndim == 1, f"{key} is not 1D"

    # Tempo should always be length 1
    assert feats["Tempo"].shape == (1,)

def test_extract_features_value_ranges():
    # Sine wave has no percussive energy, so spectral contrast should be non-negative
    y, sr = make_sine(duration=0.5)
    feats = extract_features(y, sr)

    # All spectral centroid values >= 0
    sc = feats["Spectral Centroid"]
    assert np.all(sc >= 0)

    # Zero-crossing rate in [0,1]
    zcr = feats["Zero-Crossing Rate"]
    assert np.all((zcr >= 0) & (zcr <= 1))

    # Tempo should be a positive number
    tempo = feats["Tempo"][0]
    assert tempo >= 0

def test_extract_features_invalid_input_returns_none(capsys):
    # Passing invalid input should trigger the exception path
    result = extract_features(None, None)
    assert result is None
    captured = capsys.readouterr()
    assert "Error extracting features:" in captured.out
