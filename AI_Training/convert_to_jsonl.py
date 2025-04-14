import json
import os
from sklearn.model_selection import KFold

# Constants
INPUT_JSON = "/home/cormacgeraghty/Desktop/Project Code/sample_audio_data.json"
OUTPUT_JSONL_TRAIN = "train_data.jsonl"
OUTPUT_JSONL_VAL = "val_data.jsonl"
KFOLD_SPLITS = 1 # Use all data for training

def build_prompt_text(entry: dict) -> str:
    """
    Builds a user prompt string based on audio features.
    """
    features = entry["features"]
    prompt = (
        "Based on these summarized audio characteristics:\n"
        f"- MFCC mean: {features['MFCCs']['mean']}\n"
        f"- Spectral Centroid mean: {features['Spectral Centroid']['mean']}\n"
        f"- Spectral Contrast mean: {features['Spectral Contrast']['mean']}\n"
        f"- Tempo mean: {features['Tempo']['mean']}\n"
        f"- Beats mean: {features['Beats']['mean']}\n"
        f"- Harmonic Components mean: {features['Harmonic Components']['mean']}\n"
        f"- Percussive Components mean: {features['Percussive Components']['mean']}\n"
        f"- Zero-Crossing Rate mean: {features['Zero-Crossing Rate']['mean']}\n"
        f"- Chroma Features (CENS) mean: {features['Chroma Features (CENS)']['mean']}\n"
        "Generate the corresponding identifier and secure access code."
    )
    return prompt

def convert_to_jsonl(input_file, output_train, output_val):
    """
    Reads audio data from `input_file` and writes all entries to a single training file.
    """
    with open(input_file, "r") as f:
        data = json.load(f)
    
    train_data = data # Use all data for training
    val_data = [] # No validation set
    
    print(f"Using entire dataset for training. Total examples: {len(train_data)}")
    
    # Process Training Data
    train_file_path = output_train.replace(".jsonl", "_fold0.jsonl")
    with open(train_file_path, "w") as f_train:
        for entry in train_data:
            prompt_text = build_prompt_text(entry)
            completion = f"Identifier: {entry['hash']}\nAccess Code: {entry['password']}"
            
            json.dump({
                "messages": [
                    {"role": "user", "content": prompt_text},
                    {"role": "assistant", "content": completion}
                ]
            }, f_train)
            f_train.write("\n")
    
    print(f"Training data saved: {train_file_path} (Total examples: {len(train_data)})")

def test_script():
    """
    Runs JSON -> JSONL conversion using `sample_audio_data.json`
    """
    print("\n--- Running convert_to_jsonl on sample_audio_data.json ---\n")
    convert_to_jsonl(INPUT_JSON, OUTPUT_JSONL_TRAIN, OUTPUT_JSONL_VAL)

if __name__ == "__main__":
    test_script()