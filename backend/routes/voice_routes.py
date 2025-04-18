import os
import logging
from flask import Blueprint, request, jsonify
from vocal_passwords.voice_processing import record_audio
from models.voice_recognition import save_voiceprint, verify_voice

voice_routes = Blueprint("voice_routes", __name__)
logging.basicConfig(level=logging.INFO)

@voice_routes.route("/api/register-voice", methods=["POST"])
def register_voice():
    """
    Records and saves a new voiceprint for authentication.
    """
    try:
        logging.info("🎤 Recording voice for registration...")
        audio, _ = record_audio()
        save_voiceprint("vocal_input.wav")
        logging.info(" Voiceprint successfully saved.")
        return jsonify({"message": " Voice registered successfully!"}), 200
    except Exception as e:
        logging.error(f" Error registering voice: {e}")
        return jsonify({"error": str(e)}), 500

@voice_routes.route("/api/verify-voice", methods=["POST"])
def verify_user():
    """
    Verifies a user's voice before generating a password.
    """
    try:
        logging.info("🎤 Verifying voice...")
        verified = verify_voice("vocal_input.wav")
        if verified:
            logging.info(" Voice authentication successful!")
            return jsonify({"verified": True, "message": " Voice verified!"}), 200
        else:
            logging.warning(" Voice authentication failed!")
            return jsonify({"verified": False, "message": " Voice not recognized!"}), 401
    except Exception as e:
        logging.error(f" Error verifying voice: {e}")
        return jsonify({"error": str(e)}), 500
