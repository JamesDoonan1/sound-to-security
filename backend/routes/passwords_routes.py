import numpy as np
import os
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.services.passwords_service import process_audio_and_generate_password
from backend.services.password_cracker import brute_force_crack
from backend.services.ai_password_cracker import ai_crack_password 
from backend.services.gpt_password_tester import test_password_with_gpt  
from backend.services.passwords_service import extract_passphrase, extract_voice_features
from services.hashcat_cracker import save_hash, crack_password_with_hashcat


# Initialize blueprint and logger
passwords_routes = Blueprint("passwords_routes", __name__)
logging.basicConfig(level=logging.INFO)

TEMP_DIR = os.getenv("TEMP_DIR", "./temp")
os.makedirs(TEMP_DIR, exist_ok=True)  

@passwords_routes.route("/", methods=["GET"])
def home():
    """ Default route for the root URL. """
    return jsonify({"message": "Welcome to the Password Generator API!"})

@passwords_routes.route("/api/generate-password", methods=["POST"])
def generate_password():
    """Endpoint to generate a password and compare it with traditional passwords."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    filename = secure_filename(audio_file.filename)
    audio_path = f"{TEMP_DIR}/{filename}"
    audio_file.save(audio_path)

    logging.info("Processing audio file for password generation...")

    try:
        result = process_audio_and_generate_password(audio_path)
        logging.info(f" Password successfully generated: {result['ai_password']}")

        return jsonify(result), 200
    except Exception as e:
        logging.error(f" Error generating password: {e}")
        return jsonify({"error": str(e)}), 500

@passwords_routes.route("/api/test-password", methods=["POST"])
def test_password():
    """
    Endpoint to test password security using GPT-4, Claude, and brute-force attacks.
    Handles missing passphrase and voice features correctly.
    """

    if not request.json or "password" not in request.json:
        return jsonify({"error": "Password not provided"}), 400

    target_password = request.json.get("password")
    test_type = request.json.get("test_type", "gpt")  # Default to GPT

    logging.info(f"🔍 Testing password security for: {target_password} using {test_type}")

    #  Extract passphrase and voice features
    passphrase = extract_passphrase()
    voice_features = extract_voice_features()

    #  Handle missing passphrase and voice features gracefully
    if passphrase is None:
        logging.warning(" No passphrase found, using placeholder.")
        passphrase = "UNKNOWN_PASSPHRASE"

    voice_features = extract_voice_features()  #  This is already a dictionary

    if voice_features is None:
        logging.error(" Missing voice features for GPT test.")
        return jsonify({"error": "Missing voice features for GPT test"}), 500

    #  FIXED: Use dictionary keys instead of list indexing
    voice_features_dict = {
        "mfcc": float(voice_features["mfcc"]),
        "spectral_centroid": float(voice_features["spectral_centroid"]),
        "tempo": float(voice_features["tempo"]),
    }


    #  Perform the requested test
    try:
        if test_type == "gpt":
            result = test_password_with_gpt(target_password, passphrase, voice_features_dict)
        elif test_type == "claude":
            result = ai_crack_password(target_password)
        elif test_type == "brute":
            result = brute_force_crack(target_password)
        else:
            result = {"error": "Invalid test type"}

        return jsonify(result)

    except Exception as e:
        logging.error(f" Error during {test_type} password testing: {e}")
        return jsonify({"error": f"{test_type} test failed: {str(e)}"}), 500

@passwords_routes.route("/api/test-password-hashcat", methods=["POST"])
def test_password_with_hashcat():
    """API to test password security using Hashcat."""
    data = request.get_json()
    password_hash = data.get("password_hash")
    hash_type = data.get("hash_type", "0")  # Default MD5
    attack_mode = data.get("attack_mode", "3")  # Default brute-force

    if not password_hash:
        return jsonify({"error": " No password hash provided!"}), 400

    # Save the hash for Hashcat
    save_hash(password_hash)

    # Run Hashcat to crack the hash
    cracked, result = crack_password_with_hashcat(hash_type, attack_mode)

    return jsonify({"cracked": cracked, "result": result}), 200
