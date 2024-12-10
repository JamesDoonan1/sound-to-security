from flask import Blueprint, request, jsonify
from backend.services.passwords_service import process_audio_and_generate_password

passwords_routes = Blueprint("passwords_routes", __name__)

@passwords_routes.route("/", methods=["GET"])
def home():
    """
    Default route for the root URL.
    """
    return jsonify({"message": "Welcome to the Password Generator API!"})


@passwords_routes.route("/api/generate-password", methods=["POST"])
def generate_password():
    """
    Endpoint to accept audio data, extract features, and generate a password.
    """
    # Check if audio data is included in the request
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    # Save the audio file
    audio_file = request.files["audio"]
    audio_path = f"./temp/{audio_file.filename}"
    audio_file.save(audio_path)

    # Process the audio and generate a password
    try:
        password = process_audio_and_generate_password(audio_path)
        return jsonify({"password": password}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
