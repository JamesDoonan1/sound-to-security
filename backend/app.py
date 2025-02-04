import sys
import os
from flask import Flask, jsonify

# Add the root directory to the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.routes.passwords_routes import passwords_routes
from backend.routes.voice_routes import voice_routes  # ✅ Import the new voice authentication routes

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)

    # Default route
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({"message": "Welcome to the Password Generator API!"})

    # Register blueprints (routes)
    app.register_blueprint(passwords_routes)
    app.register_blueprint(voice_routes)  # ✅ Register the new voice authentication routes

    return app

if __name__ == "__main__":
    # Print Python's module search path for debugging
    print("PYTHONPATH:", sys.path)

    # Create the Flask application
    app = create_app()

    # Run the application in debug mode
    app.run(debug=True)
