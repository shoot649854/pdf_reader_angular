import json
import os
import sys

import dotenv
from google.cloud import storage

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor
from src.controller.VertexAI.GenerateResponse import GenerateResponse
from src.logging.Logging import logger
from src.model.GoogleCloudStorage import download_file, get_bucket

dotenv.load_dotenv(".env")


# Cloud Function entry point
def process_pdf(event) -> storage.Client:
    """
    Cloud Function to process a PDF file uploaded to a GCS bucket, extract fields, and output a JSON result.

    :param event: The event data containing details of the uploaded file.
    :param context: Metadata about the event.
    """
    try:
        # Extract file details from the event
        file_name = event.get("name")
        bucket_name = event.get("bucket")

        if not file_name or not bucket_name:
            raise ValueError("Invalid event data: 'name' or 'bucket' missing.")

        logger.info(f"Processing file '{file_name}' from bucket '{bucket_name}'")

        # Download the file from GCS to a temporary path
        temp_pdf_path = f"/tmp/{file_name}"
        # bucket = get_bucket(bucket_name)
        # blob = bucket.blob(file_name)

        # if not blob.exists():
        #     raise FileNotFoundError(f"File '{file_name}' not found in bucket '{bucket_name}'.")

        logger.info(f"Downloading file '{file_name}' to temporary path '{temp_pdf_path}'")
        download_file(file_name)

        # Process the PDF file
        generate_res = GenerateResponse()
        response_parser = JSONFieldLoader()
        extractor = PDFFormExtractor(temp_pdf_path, generate_res, response_parser)

        logger.info("Extracting fields from the PDF...")
        fields_with_titles = extractor.get_fields_with_titles()
        fields_with_titles = extractor.apply_previous_title(fields_with_titles)

        # Convert extracted fields to JSON
        json_output = json.dumps(fields_with_titles, indent=4)
        output_json_name = f"{file_name}_fields_with_titles_description.json"
        output_bucket_name = os.getenv("GCS_OUTPUT_BUCKET")

        if not output_bucket_name:
            raise EnvironmentError("Environment variable 'GCS_OUTPUT_BUCKET' is not set.")

        # Upload JSON to the output bucket
        output_bucket = get_bucket(output_bucket_name)
        output_blob = output_bucket.blob(output_json_name)
        output_blob.upload_from_string(json_output, content_type="application/json")

        logger.info(
            f"Successfully processed file '{file_name}'. JSON output uploaded to '{output_bucket_name}/{output_json_name}'"
        )

        return f"PDF processing complete for {file_name}. Output uploaded to {output_bucket_name}/{output_json_name}."

    except Exception as e:
        logger.error(f"An error occurred during PDF processing: {str(e)}")
        raise


if __name__ == "__main__":

    # Simulated GCS Event
    test_event = {"bucket": os.getenv("GCS_INPUT_BUCKET"), "name": "test-file.pdf"}
    test_context = None  # Context is not typically used in this function

    # Call the function directly
    print(test_event)
    print("Starting local function...")
    process_pdf(test_event, test_context)
