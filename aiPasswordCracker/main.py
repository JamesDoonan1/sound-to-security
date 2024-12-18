import os
import librosa
from audio_feature_extraction import extract_features, create_hash
from ai_password_generator import AIPasswordGenerator

# Set your audio folder path
AUDIO_FOLDER_PATH = "/media/sf_VM_Shared_Folder/Audio Files"

if not os.path.exists(AUDIO_FOLDER_PATH):
    print(f"The folder {AUDIO_FOLDER_PATH} does not exist.")
    exit()

password_gen = AIPasswordGenerator()

for file_name in os.listdir(AUDIO_FOLDER_PATH):
    if not file_name.endswith(".mp3"):
        continue

    file_path = os.path.join(AUDIO_FOLDER_PATH, file_name)
    print(f"\nProcessing file: {file_name}")

    try:
        # Load and process audio
        y, sr = librosa.load(file_path, sr=None)
        print(f"Loaded: {len(y)} samples, Sample Rate: {sr}")

        # Extract features and create hash
        features = extract_features(y, sr)
        audio_hash = create_hash(features)

        # Generate AI password
        password = password_gen.generate_password(features, audio_hash)
        if password:
            print(f"Generated Hash: {audio_hash}")
            print(f"Generated Password: {password}")
        else:
            print("Failed to generate password.")

    except Exception as e:
        print(f"Failed to process the file with Librosa: {e}")

    print("-" * 50)

print("Processing completed.")
