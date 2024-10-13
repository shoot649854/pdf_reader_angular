import os

import dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask

dotenv.load_dotenv()

CREDENTIAL_PATH = "~/.gcp/credentials/firestore-keyfile.json"

# credential_path = os.getenv("CREDENTIAL_PATH")
credential_path = CREDENTIAL_PATH
if not credential_path:
    raise EnvironmentError(
        "The environment variable 'CREDENTIAL_PATH' is not set. Please set it in "
        "your .env file or environment."
    )

ABS_CREDENTIAL_PATH = os.path.expanduser(credential_path)

cred = credentials.Certificate(ABS_CREDENTIAL_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)
