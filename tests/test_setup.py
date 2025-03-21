import os
import sys
from flask import Flask

# ✅ Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# ✅ Now these imports should work
from backend.routes.passwords_routes import passwords_routes
from backend.routes.voice_routes import voice_routes

def create_test_app():
    """Create and configure a new Flask app for each test"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(passwords_routes, url_prefix="/api")
    app.register_blueprint(voice_routes, url_prefix="/api")
    return app
