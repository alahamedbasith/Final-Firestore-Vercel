from flask import Flask, jsonify, request, send_from_directory
from firebase_admin import credentials, firestore, initialize_app
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Firebase credentials from environment variables
firebase_key = os.getenv("PRIVATE_KEY").replace(r'\\n', '\n')
cred = credentials.Certificate({
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": firebase_key,
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN")
})

initialize_app(cred)
db = firestore.client()
content_ref = db.collection('content')

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Serve static files
def serve_static_file(file_name):
    static_dir = os.path.join(os.getcwd(), "static")
    return send_from_directory(static_dir, file_name)

@app.route('/static/<path:file_name>', methods=['GET'])
def static_files(file_name):
    return serve_static_file(file_name)

# API to get all content
@app.route("/content", methods=["GET"])
def get_content():
    try:
        docs = content_ref.stream()
        content = {doc.id: doc.to_dict() for doc in docs}
        return jsonify(content), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching content: {str(e)}"}), 500

# API to update content
@app.route("/content/<string:key>", methods=["POST"])
def update_content(key):
    try:
        data = request.get_json()
        if not data or "value" not in data:
            return jsonify({"error": "Invalid payload"}), 400

        content_ref.document(key).set({"value": data["value"]})
        return jsonify({"message": f"Content with key '{key}' updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Error updating content: {str(e)}"}), 500

# Serve index.html
@app.route("/", methods=["GET"])
def get_index():
    try:
        return serve_static_file("index.html")
    except Exception as e:
        return jsonify({"error": f"Error loading index.html: {str(e)}"}), 500

# Serve admin.html
@app.route("/admin", methods=["GET"])
def get_admin():
    try:
        return serve_static_file("admin.html")
    except Exception as e:
        return jsonify({"error": f"Error loading admin.html: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
