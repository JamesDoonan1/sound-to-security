from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask server is running", 200

@app.route('/generate-vocal-password', methods=['POST'])
def generate_vocal_password():
    vocal_input = request.json.get('vocal_input', 'default_input')
    generated_password = f"secure-{vocal_input}"  # Simple password logic
    return jsonify({"generated_password": generated_password})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
