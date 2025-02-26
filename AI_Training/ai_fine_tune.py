import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check if API key is set
if not openai.api_key:
    print("Error: OPENAI_API_KEY is not set. Check your .env file or export the key.")
    exit(1)

# Define data path
DATA_PATH = "/home/cormacgeraghty/Desktop/Project Code/"

# Use only Fold 0 for testing
fold = 0
train_path = os.path.join(DATA_PATH, f"train_data_fold{fold}.jsonl")
val_path = os.path.join(DATA_PATH, f"val_data_fold{fold}.jsonl")

# Check if files exist before proceeding
if not os.path.exists(train_path) or not os.path.exists(val_path):
    print(f"Error: Missing files for fold {fold}: {train_path} or {val_path}")
    exit(1)  # Exit if files are missing
else:
    print(f"Using files: {train_path}, {val_path}")

# Upload files for fine-tuning
train_file = openai.files.create(file=open(train_path, "rb"), purpose="fine-tune")
val_file = openai.files.create(file=open(val_path, "rb"), purpose="fine-tune")

# Retrieve file IDs
train_file_id = train_file.id
val_file_id = val_file.id

# Create a fine-tuning job (using the correct model and API version)
response = openai.fine_tuning.jobs.create(
    training_file=train_file_id,
    validation_file=val_file_id,
    model="gpt-4o-2024-08-06"  # Corrected model name
)

# Save model ID to a text file
model_info_path = os.path.join(DATA_PATH, f"model_info_fold{fold}.txt")
with open(model_info_path, "w") as f:
    f.write(response.id)

print(f"Fine-tuning started for fold {fold}. Model ID: {response.id}")
