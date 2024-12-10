import os
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.services.passwords_service import process_audio_and_generate_password
from backend.services.password_cracker import brute_force_crack, dictionary_attack


# Initialize blueprint and logger
passwords_routes = Blueprint("passwords_routes", __name__)
logging.basicConfig(level=logging.INFO)

TEMP_DIR = os.getenv("TEMP_DIR", "./temp")
os.makedirs(TEMP_DIR, exist_ok=True)  # Ensure the temp directory exists

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

    Request:
    - Form-data with an 'audio' field containing the audio file.

    Response:
    - Success: {"password": "<generated_password>"}
    - Failure: {"error": "<error_message>"}
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    # Save the audio file
    audio_file = request.files["audio"]
    filename = secure_filename(audio_file.filename)
    audio_path = f"{TEMP_DIR}/{filename}"
    audio_file.save(audio_path)

    logging.info("Processing audio file for password generation...")

    try:
        password = process_audio_and_generate_password(audio_path)
        logging.info(f"Password successfully generated: {password}")
        return jsonify({"password": password}), 200
    except Exception as e:
        logging.error(f"Error generating password: {e}")
        return jsonify({"error": str(e)}), 500


@passwords_routes.route("/api/test-password", methods=["POST"])
def test_password():
    """
    Endpoint to test the security of a given password.

    Request:
    - JSON with a 'password' field containing the password to test.

    Response:
    - Combined results from brute force and dictionary attacks.
    """
    if not request.json or "password" not in request.json:
        return jsonify({"error": "Password not provided"}), 400

    target_password = request.json.get("password")
    logging.info(f"Testing password security for: {target_password}")

    # Run brute force attack
    brute_force_results = brute_force_crack(target_password)
    logging.info("Brute force attack completed")

    # Run dictionary attack
    dictionary_results = dictionary_attack(target_password)
    logging.info("Dictionary attack completed")

    # Combine results and return
    return jsonify({
        "brute_force": brute_force_results,
        "dictionary_attack": dictionary_results
    })
