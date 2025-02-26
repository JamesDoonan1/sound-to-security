import json
import os
from sklearn.model_selection import KFold

# Constants
INPUT_JSON = "/home/cormacgeraghty/Desktop/Project Code/sample_audio_data.json"
OUTPUT_JSONL_TRAIN = "train_data.jsonl"
OUTPUT_JSONL_VAL = "val_data.jsonl"
KFOLD_SPLITS = 5

def build_prompt_text(entry: dict) -> str:
    """
    Manually builds a user prompt string based on audio features.
    """
    features = entry["features"]
    prompt = (
        "Given these summarized audio features:\n"
        f"- MFCC mean: {features['MFCCs']['mean']}\n"
        f"- Spectral Centroid mean: {features['Spectral Centroid']['mean']}\n"
        f"- Spectral Contrast mean: {features['Spectral Contrast']['mean']}\n"
        f"- Tempo mean: {features['Tempo']['mean']}\n"
        f"- Beats mean: {features['Beats']['mean']}\n"
        f"- Harmonic Components mean: {features['Harmonic Components']['mean']}\n"
        f"- Percussive Components mean: {features['Percussive Components']['mean']}\n"
        f"- Zero-Crossing Rate mean: {features['Zero-Crossing Rate']['mean']}\n"
        f"- Chroma Features (CENS) mean: {features['Chroma Features (CENS)']['mean']}\n"
        "Predict the MD5 hash and the password."
    )
    return prompt

def convert_to_jsonl(input_file, output_train, output_val):
    """
    Reads audio data from `input_file`, applies K-Fold splitting,
    then writes user+assistant messages to JSONL files for each fold.
    """
    with open(input_file, "r") as f:
        data = json.load(f)

    kf = KFold(n_splits=KFOLD_SPLITS, shuffle=True, random_state=42)
    data = list(data)

    for fold, (train_index, val_index) in enumerate(kf.split(data)):
        train_data = [data[i] for i in train_index]
        val_data = [data[i] for i in val_index]

        print(f"Preparing data for fold {fold}...")

        train_file_path = output_train.replace(".jsonl", f"_fold{fold}.jsonl")
        with open(train_file_path, "w") as f_train:
            for entry in train_data:
                prompt_text = build_prompt_text(entry)
                completion = f"Hash: {entry['hash']}\nPassword: {entry['password']}"
                json.dump({
                    "messages": [
                        {"role": "user", "content": prompt_text},
                        {"role": "assistant", "content": completion}
                    ]
                }, f_train)
                f_train.write("\n")

        val_file_path = output_val.replace(".jsonl", f"_fold{fold}.jsonl")
        with open(val_file_path, "w") as f_val:
            for entry in val_data:
                json.dump(entry, f_val)
                f_val.write("\n")

        print(f"Fold {fold} data saved. Train size: {len(train_data)}, Validation size: {len(val_data)}.")

def test_script():
    """
    Runs JSON -> JSONL conversion using `sample_audio_data.json`
    to ensure it's working correctly.
    """
    print("\n--- Running convert_to_jsonl on sample_audio_data.json ---\n")
    convert_to_jsonl(INPUT_JSON, OUTPUT_JSONL_TRAIN, OUTPUT_JSONL_VAL)

if __name__ == "__main__":
    test_script()
