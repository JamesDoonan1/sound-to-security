import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pytest

from hash_password_generator import create_hash

def test_create_hash_deterministic():
    feats = {
        "a": np.array([1, 2, 3], dtype=np.int32),
        "b": np.array([4, 5, 6], dtype=np.int32),
    }
    h1 = create_hash(feats)
    h2 = create_hash(feats)
    assert isinstance(h1, str) and len(h1) == 32
    assert h1 == h2

def test_create_hash_changes_with_feature_values():
    feats = {
        "x": np.array([10.0, 20.0], dtype=np.float64),
        "y": np.array([30.0], dtype=np.float64),
    }
    base = create_hash(feats)

    feats2 = {
        "x": np.array([10.0, 20.0], dtype=np.float64),
        "y": np.array([31.0], dtype=np.float64),
    }
    changed = create_hash(feats2)
    assert changed != base

def test_create_hash_empty_features_raises():
    # An empty dict yields no arrays to concatenate → ValueError
    with pytest.raises(ValueError):
        create_hash({})

def test_create_hash_with_different_dtypes():
    feats_int = {"v": np.array([1, 2, 3], dtype=np.int8)}
    feats_float = {"v": np.array([1.0, 2.0, 3.0], dtype=np.float64)}
    h_int = create_hash(feats_int)
    h_float = create_hash(feats_float)
    assert h_int != h_float

@pytest.mark.parametrize("order1, order2", [
    (["a", "b"], ["b", "a"]),
    (["x", "y", "z"], ["z", "y", "x"]),
])
def test_create_hash_order_sensitivity(order1, order2):
    arrays = {
        "a": np.array([7, 8], dtype=np.int16),
        "b": np.array([9], dtype=np.int16),
        "x": np.array([1], dtype=np.int16),
        "y": np.array([2], dtype=np.int16),
        "z": np.array([3], dtype=np.int16),
    }
    feats1 = {k: arrays[k] for k in order1}
    feats2 = {k: arrays[k] for k in order2}
    h1 = create_hash(feats1)
    h2 = create_hash(feats2)
    assert (h1 != h2) == (order1 != order2)

def test_non_array_values_converted_list():
    # Passing a Python list instead of ndarray should still work
    feats = {"lst": [1, 2, 3]}
    h = create_hash(feats)
    # Should be a valid MD5 hex
    assert isinstance(h, str) and len(h) == 32
