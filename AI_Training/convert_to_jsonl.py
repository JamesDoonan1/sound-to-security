import json
import baml_py
from sklearn.model_selection import KFold

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
    harmonic_components: float,
    percussive_components: float,
    zero_crossing_rate: float,
    chroma_features: float
) -> str:
    """
    Given summarized audio features, predict the MD5 hash and the password.
    """

def convert_to_jsonl(input_file, output_train, output_val):
    with open(input_file, "r") as f:
        data = json.load(f)

    # Apply KFold cross-validation
    kf = KFold(n_splits=KFOLD_SPLITS, shuffle=True, random_state=42)
    data = list(data)

    for fold, (train_index, val_index) in enumerate(kf.split(data)):
        train_data = [data[i] for i in train_index]
        val_data = [data[i] for i in val_index]

        print(f"Preparing data for fold {fold}.")

        # Create training data
        train_file_path = output_train.replace(".jsonl", f"_fold{fold}.jsonl")
        with open(train_file_path, "w") as f_train:
            for entry in train_data:
                prompt = predict_hash_and_password(
                    mfccs=str(entry["features"]["MFCCs"]["mean"]),
                    spectral_centroid=str(entry["features"]["Spectral Centroid"]["mean"]),
                    spectral_contrast=str(entry["features"]["Spectral Contrast"]["mean"]),
                    tempo=entry["features"]["Tempo"]["mean"],
                    beats=int(entry["features"]["Beats"]["mean"]),
                    harmonic_components=entry["features"]["Harmonic Components"]["mean"],
                    percussive_components=entry["features"]["Percussive Components"]["mean"],
                    zero_crossing_rate=entry["features"]["Zero-Crossing Rate"]["mean"],
                    chroma_features=entry["features"]["Chroma Features (CENS)"]["mean"]
)

                completion = f"Hash: {entry['hash']}\nPassword: {entry['password']}"

                json.dump({
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": completion}
                    ]
                }, f_train)
                f_train.write("\n")
        
        # Write validation data
        val_file_path = output_val.replace(".jsonl", f"_fold{fold}.jsonl")
        with open(val_file_path, "w") as f_val:
            for entry in val_data:
                json.dump(entry, f_val)
                f_val.write("\n")

        print(f"Fold {fold} data saved.")

if __name__ == "__main__":
    # Final entry point to run the data conversion
    convert_to_jsonl(INPUT_JSON, OUTPUT_JSONL_TRAIN, OUTPUT_JSONL_VAL)
