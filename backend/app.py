import sys
import os
from flask import Flask, jsonify

# Add the root directory to the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.routes.passwords_routes import passwords_routes
from backend.routes.voice_routes import voice_routes  

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)

@app.route('/generate-vocal-password', methods=['POST'])
def generate_vocal_password():
    # Simulate password generation from vocal input
    # In the future, you will replace this with real audio processing logic
    vocal_input = request.json.get('vocal_input', '')
    generated_password = f"secure-{vocal_input}"  # Example placeholder logic

    return jsonify({"password": generated_password})

if __name__ == '__main__':
    app.run(debug=True)
