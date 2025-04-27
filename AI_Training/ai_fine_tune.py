import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def validate_api_key():
    """
    Validate that the OpenAI API key is loaded properly from environment variables.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment variables")
    openai.api_key = api_key

def check_file_paths(train_path, val_path):
    """
    Check if training and validation data files exist.

    Args:
        train_path (str): Path to the training file.
        val_path (str): Path to the validation file.

    Returns:
        bool: True if both files exist, raises error otherwise.
    """
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError("Training or validation file not found.")
    return True

def upload_file(path):
    """
    Upload a file to OpenAI for fine-tuning.

    Args:
        path (str): Path to the file to upload.

    Returns:
        openai.File: Uploaded file object.
    """
    with open(path, "rb") as f:
        return openai.files.create(file=f, purpose="fine-tune")

def start_fine_tuning(train_file_id, val_file_id, model="gpt-4o-2024-08-06"):
    """
    Start a fine-tuning job using the uploaded training and validation files.

    Args:
        train_file_id (str): ID of the uploaded training file.
        val_file_id (str): ID of the uploaded validation file.
        model (str): Base model to fine-tune.

    Returns:
        openai.FineTuningJob: The fine-tuning job object.
    """
    return openai.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=val_file_id,
        model=model
    )

def save_model_id(model_id, output_path):
    """
    Save the fine-tuning job ID (or model ID) to a text file.

    Args:
        model_id (str): ID of the fine-tuning job.
        output_path (str): File path to save the ID.
    """
    with open(output_path, "w") as f:
        f.write(model_id)

def run_pipeline(data_path, fold=0):
    """
    Full pipeline to validate environment, check files, upload data,
    start fine-tuning, and save the resulting model/job ID.

    Args:
        data_path (str): Directory containing training/validation files.
        fold (int, optional): Fold number for file naming. Defaults to 0.

    Returns:
        str: The fine-tuning job ID.
    """
    validate_api_key()

    train_path = os.path.join(data_path, f"train_data_fold{fold}.jsonl")
    val_path = os.path.join(data_path, f"val_data_fold{fold}.jsonl")

    check_file_paths(train_path, val_path)

    train_file = upload_file(train_path)
    val_file = upload_file(val_path)

    job = start_fine_tuning(train_file.id, val_file.id)
    save_model_id(job.id, os.path.join(data_path, f"model_info_fold{fold}.txt"))
    return job.id
