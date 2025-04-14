import json
import os
import random
from sklearn.model_selection import train_test_split

# Constants
INPUT_JSON = "/home/cormacgeraghty/Desktop/Project Code/sample_audio_data.json"
OUTPUT_JSONL_TRAIN = "train_data.jsonl"
OUTPUT_JSONL_VAL = "val_data.jsonl"
VAL_SPLIT = 0.2  # 20% of data for validation

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
    Reads audio data from `input_file` and writes entries to training and validation files.
    """
    with open(input_file, "r") as f:
        data = json.load(f)
    
    # Split data into training and validation sets
    if len(data) > 5:  # Only split if we have enough data
        train_data, val_data = train_test_split(data, test_size=VAL_SPLIT, random_state=42)
    else:
        # For small datasets, use all for training and duplicate some for validation
        train_data = data
        val_data = random.sample(data, min(3, len(data)))  # Use up to 3 examples for validation
    
    print(f"Split dataset into {len(train_data)} training examples and {len(val_data)} validation examples")
    
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
    
    # Process Validation Data
    val_file_path = output_val.replace(".jsonl", "_fold0.jsonl")
    with open(val_file_path, "w") as f_val:
        for entry in val_data:
            prompt_text = build_prompt_text(entry)
            completion = f"Identifier: {entry['hash']}\nAccess Code: {entry['password']}"
            
            json.dump({
                "messages": [
                    {"role": "user", "content": prompt_text},
                    {"role": "assistant", "content": completion}
                ]
            }, f_val)
            f_val.write("\n")
    
    print(f"Validation data saved: {val_file_path} (Total examples: {len(val_data)})")

def test_script():
    """
    Runs JSON -> JSONL conversion using `sample_audio_data.json`
    """
    print("\n--- Running convert_to_jsonl on sample_audio_data.json ---\n")
    convert_to_jsonl(INPUT_JSON, OUTPUT_JSONL_TRAIN, OUTPUT_JSONL_VAL)

if __name__ == "__main__":
    test_script()