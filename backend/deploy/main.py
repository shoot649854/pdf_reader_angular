import json
import os
import sys

import dotenv

# from google.cloud import storage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # noqa: E402

from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader  # noqa: E402
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor  # noqa: E402
from src.controller.VertexAI.GenerateResponse import GenerateResponse  # noqa: E402
from src.logging.Logging import logger  # noqa: E402
from src.model.GoogleCloudStorage import download_file, get_bucket  # noqa: E402

dotenv.load_dotenv(".env")


def process_pdf(event, context):
    """
    Cloud Function entry point.
    Triggered by a GCS "object.finalize" event when a PDF is uploaded.

    event (dict): The event payload. Must contain "bucket" and "name".
    context (google.cloud.functions.Context): Metadata of the triggering event.
    """

    # 1) Parse event data for bucket name and file name.
    source_bucket_name = event["bucket"]  # Source bucket (where PDF was uploaded)
    file_name = event["name"]  # PDF filename in source bucket

    logger.info(f"Triggered by file '{file_name}' in bucket '{source_bucket_name}'")

    # 2) Verify it's a PDF by extension. (Optional but recommended)
    if not file_name.lower().endswith(".pdf"):
        logger.info(f"File '{file_name}' is not a PDF. Skipping.")
        return f"File '{file_name}' is not a PDF. No action taken."

    # 3) Download the PDF to a temporary directory in Cloud Functions.
    #    /tmp is the only writable path in the Cloud Functions environment.
    temp_pdf_path = f"/tmp/{os.path.basename(file_name)}"
    download_file(source_bucket_name, file_name, temp_pdf_path)
    logger.info(f"Downloaded '{file_name}' to '{temp_pdf_path}'")

    # 4) Initialize classes for form extraction.
    generate_res = GenerateResponse()
    response_parser = JSONFieldLoader()
    extractor = PDFFormExtractor(temp_pdf_path, generate_res, response_parser)

    try:
        # 5) Extract fields (and any additional processing you’d like).
        logger.info("Extracting fields from the PDF...")
        fields_with_titles = extractor.get_fields_with_titles()
        fields_with_titles = extractor.apply_previous_title(fields_with_titles)
        fields_with_titles = extractor.add_descriptions(fields_with_titles)  # if you have this method
        fields_with_titles = extractor.grouping_by_title(fields_with_titles)  # if you have grouping
        logger.info(f"Extraction complete for '{file_name}'")

        # 6) Convert extracted fields to JSON string.
        json_output = json.dumps(fields_with_titles, indent=4)

        # 7) Determine the output JSON filename and bucket.
        #    For example: "myfile.pdf" --> "myfile_fields_with_titles_description.json"
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        output_json_name = f"{base_name}_fields_with_titles_description.json"

        output_bucket_name = os.getenv("GCS_OUTPUT_BUCKET")
        if not output_bucket_name:
            raise EnvironmentError("Environment variable 'GCS_OUTPUT_BUCKET' is not set.")

        # 8) Upload the JSON to the output bucket.
        output_bucket = get_bucket(output_bucket_name)
        output_blob = output_bucket.blob(output_json_name)
        output_blob.upload_from_string(json_output, content_type="application/json")

        logger.info(
            f"Successfully processed file '{file_name}'. " f"JSON output uploaded to '{output_bucket_name}/{output_json_name}'"
        )

        return f"PDF processing complete for {file_name}. " f"Output uploaded to {output_bucket_name}/{output_json_name}."

    except Exception as e:
        logger.error(f"Error processing file '{file_name}': {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # ローカルテスト用のイベント
    test_event = {"bucket": os.getenv("GCS_INPUT_BUCKET"), "name": "test-file.pdf"}
    test_context = None

    print("Test event:", test_event)
    print("Starting local function test...")
    result = process_pdf(test_event, test_context)
    print("Function result:", result)
