import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env
load_dotenv()

# Set API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
MODEL_INFO_PATH = "/home/cormacgeraghty/Desktop/Project Code/model_info_fold0.txt"

def validate_api_key():
    """
    Validates that the OpenAI API key is present.
    Exits with an error message if not.
    """
    if not openai.api_key:
        print("Error: OPENAI_API_KEY is not set. Check your .env file or export the key.")
        exit(1)

def get_model_id():
    """
    Reads and returns the fine-tuned model ID from the text file.
    """
    if not os.path.exists(MODEL_INFO_PATH):
        print(f"Error: Model ID file not found: {MODEL_INFO_PATH}")
        exit(1)
    with open(MODEL_INFO_PATH, "r") as f:
        return f.read().strip()

def check_fine_tune_status(model_id_path="model_info_fold0.txt"):
    if not openai.api_key:
        print("Error: OPENAI_API_KEY is not set. Check your .env file or export the key.")
        exit(1)

    if not os.path.exists(model_id_path):
        print(f"Error: Model ID file '{model_id_path}' not found.")
        exit(1)

    with open(model_id_path, "r") as f:
        model_id = f.read().strip()

    try:
        job = openai.fine_tuning.jobs.retrieve(model_id)
        print("\n--- Fine-Tuning Job Status ---")
        print(f"Job ID:           {job.id}")
        print(f"Status:           {job.status}")
        print(f"Base Model:       {job.model}")
        print(f"Fine-Tuned Model: {job.fine_tuned_model}")
        print(f"Created At:       {job.created_at}")
        print(f"Training File:    {job.training_file}")
        print(f"Validation File:  {job.validation_file}")
        if job.error:
            print(f"Error:            {job.error}")
        print("------------------------------\n")
    except Exception as e:
        print(f"Error retrieving job status: {e}")
        exit(1)

if __name__ == "__main__":
    validate_api_key()
    model_id = get_model_id()
    check_fine_tune_status(model_id)