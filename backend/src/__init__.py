import os

import dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask
from flask_cors import CORS

dotenv.load_dotenv()

CREDENTIAL_PATH = os.getenv("CREDENTIAL_PATH")
if not CREDENTIAL_PATH:
    raise EnvironmentError(
        "The environment variable 'CREDENTIAL_PATH' is not set. Please set it in "
        "your .env file or environment."
    )

ABS_CREDENTIAL_PATH = os.path.expanduser(CREDENTIAL_PATH)
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ABS_CREDENTIAL_PATH
cred = credentials.Certificate(ABS_CREDENTIAL_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)
CORS(app=app, resources={r"/*": {"origins": "http://localhost:4200"}})

from src.model.Firestore import firestore_bp
from src.model.FormHandler import form_bp
from src.model.GeneratePDF import generate_pdf_bp
from src.model.GoogleCloudStorage import storage_bp

# Register blueprints
app.register_blueprint(firestore_bp, url_prefix="/firestore")
app.register_blueprint(generate_pdf_bp, url_prefix="/generate_pdf")
app.register_blueprint(storage_bp, url_prefix="/storage")
app.register_blueprint(form_bp, url_prefix="/form")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
