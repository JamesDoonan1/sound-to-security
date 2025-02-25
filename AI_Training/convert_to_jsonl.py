import json
import baml_py

# File paths
INPUT_JSON = "../audio_data.json"
OUTPUT_JSONL_TRAIN = "train_data.jsonl"
OUTPUT_JSONL_VAL = "val_data.jsonl"
KFOLD_SPLITS = 5  # Number of K-Fold splits

