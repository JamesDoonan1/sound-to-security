import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def validate_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment variables")
    openai.api_key = api_key

def check_file_paths(train_path, val_path):
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError("Training or validation file not found.")
    return True

def upload_file(path):
    with open(path, "rb") as f:
        return openai.files.create(file=f, purpose="fine-tune")

def start_fine_tuning(train_file_id, val_file_id, model="gpt-4o-2024-08-06"):
    return openai.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=val_file_id,
        model=model
    )

def save_model_id(model_id, output_path):
    with open(output_path, "w") as f:
        f.write(model_id)

def run_pipeline(data_path, fold=0):
    validate_api_key()

    train_path = os.path.join(data_path, f"train_data_fold{fold}.jsonl")
    val_path = os.path.join(data_path, f"val_data_fold{fold}.jsonl")

    check_file_paths(train_path, val_path)

    train_file = upload_file(train_path)
    val_file = upload_file(val_path)

    job = start_fine_tuning(train_file.id, val_file.id)
    save_model_id(job.id, os.path.join(data_path, f"model_info_fold{fold}.txt"))
    return job.id
