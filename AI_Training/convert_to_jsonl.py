import json
import baml_py

# File paths
INPUT_JSON = "../audio_data.json"
OUTPUT_JSONL_TRAIN = "train_data.jsonl"
OUTPUT_JSONL_VAL = "val_data.jsonl"
KFOLD_SPLITS = 5  # Number of K-Fold splits

@baml_py.prompt
def predict_hash_and_password(
    mfccs: str,
    spectral_centroid: str,
    spectral_contrast: str,
    tempo: float,
    beats: int,
) -> str:
    """
    Given summarized audio features, predict the MD5 hash and the password.
    """


