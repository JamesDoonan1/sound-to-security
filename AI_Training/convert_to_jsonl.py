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
                    mfccs=str(entry["features"]["MFCCs"]),
                    spectral_centroid=str(entry["features"]["Spectral Centroid"]),
                    spectral_contrast=str(entry["features"]["Spectral Contrast"]),
                    tempo=entry["features"]["Tempo"]["mean"],
                    beats=int(entry["features"]["Beats"]["mean"])
                )

                completion = f"Hash: {entry['hash']}\nPassword: {entry['password']}"

                json.dump({
                    "messages": [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": completion}
                    ]
                }, f_train)
                f_train.write("\n")
