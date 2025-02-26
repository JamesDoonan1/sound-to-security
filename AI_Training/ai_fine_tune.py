import openai
import os

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

DATA_PATH = "../../"

# Fine-tune for each K-Fold split
for fold in range(5):
    train_path = os.path.join(DATA_PATH, f"train_data_fold{fold}.jsonl")
    val_path = os.path.join(DATA_PATH, f"val_data_fold{fold}.jsonl")

    # Check if files exist
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        print(f"Error: Missing files for fold {fold}: {train_path} or {val_path}")
        continue

    print(f"Using files: {train_path}, {val_path}")

    train_file = openai.File.create(file=open(train_path, "rb"), purpose="fine-tune")
    val_file = openai.File.create(file=open(val_path, "rb"), purpose="fine-tune")

    response = openai.FineTune.create(
        training_file=train_file["id"],
        validation_file=val_file["id"],
        model="gpt-4o",
        n_epochs=5,
        learning_rate_multiplier=0.1
    )

    with open(f"model_info_fold{fold}.txt", "w") as f:
        f.write(response["id"])

    print(f"Fine-tuning started for fold {fold}. Model ID: {response['id']}")