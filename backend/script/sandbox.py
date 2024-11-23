import os
import sys

import vertexai
from google.oauth2 import service_account

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import ABS_CREDENTIAL_PATH

# from src.config import I140_PATH
from src.controller.GenerateResponse import GenerateResponse
from vertexai.generative_models import Part

# Set up your project details
PROJECT_ID = os.getenv("PROJECT_ID")
if not PROJECT_ID:
    print("Error: PROJECT_ID environment variable is not set.")
    sys.exit(1)

LOCATION = os.getenv("REGION")
if not LOCATION:
    print("Error: REGION is not set.")
    sys.exit(1)

credentials = service_account.Credentials.from_service_account_file(ABS_CREDENTIAL_PATH)
vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

# Initialize the GenerateResponse class
generate_response = GenerateResponse(model="gemini-1.5-flash-002")
pdf_file = Part.from_uri(
    uri="gs://shoto_test_bucket/filled-form.pdf",
    mime_type="application/pdf",
)

# Your summarization prompt
prompt = """
You are a very professional document summarization specialist.
Please summarize the given document.
"""

# Combine the PDF and the prompt
contents = [pdf_file, prompt]
summary = generate_response.generate_response(contents)
print(summary)
