import openai
import os

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

DATA_PATH = "../../"