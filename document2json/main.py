import json
import os

from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor
from src.logging.Logging import logger
from src.model.GoogleCloudStorage import download_file, get_bucket


def document2json(event, context):
    """
    Cloud Function entry point.
    Triggered by a GCS "object.finalize" event when a PDF is uploaded.

    event (dict): The event payload. Must contain "bucket" and "name".
    context (google.cloud.functions.Context): Metadata of the triggering event.
    """
    source_bucket_name = event["bucket"]
    file_name = event["name"]
    logger.info(f"Triggered by file '{file_name}' in bucket '{source_bucket_name}'")

    # Skip files that are not PDFs
    if not file_name.lower().endswith(".pdf"):
        logger.info(f"File '{file_name}' is not a PDF. Skipping.")
        return f"File '{file_name}' is not a PDF. No action taken."

    temp_pdf_path = f"/tmp/{os.path.basename(file_name)}"
    download_file(source_bucket_name, file_name, temp_pdf_path)
    logger.info(f"Downloaded '{file_name}' to '{temp_pdf_path}'")

    response_parser = JSONFieldLoader()
    extractor = PDFFormExtractor(temp_pdf_path, response_parser)

    # Check if PDF has text fields
    try:
        logger.info("Checking for text fields in the PDF...")
        if not extractor.has_text_fields():
            logger.info(f"PDF '{file_name}' does not contain any text fields. Skipping.")
            return f"PDF '{file_name}' does not contain any text fields. No action taken."
    except Exception as e:
        logger.error(f"Error checking text fields for '{file_name}': {e}", exc_info=True)
        raise

    # Proceed with processing
    try:
        logger.info("Extracting fields from the PDF...")
        fields_with_titles = extractor.get_fields_with_titles()
        fields_with_titles = extractor.apply_previous_title(fields_with_titles)
        fields_with_titles = extractor.add_descriptions(fields_with_titles)
        fields_with_titles = extractor.grouping_by_title(fields_with_titles)
        logger.info(f"Extraction complete for '{file_name}'")

        json_output = json.dumps(fields_with_titles, indent=4)

        # Save the JSON output in the same directory as the input PDF
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        output_json_name = f"{base_name}_fields_with_titles_description.json"
        output_json_path = os.path.join(os.path.dirname(file_name), output_json_name)

        # Save back to the same bucket
        output_bucket_name = source_bucket_name
        output_bucket = get_bucket(output_bucket_name)
        output_blob = output_bucket.blob(output_json_path)
        output_blob.upload_from_string(json_output, content_type="application/json")

        logger.info(
            f"Successfully processed file '{file_name}'. " f"JSON output uploaded to '{output_bucket_name}/{output_json_path}'"
        )
        return f"PDF processing complete for {file_name}. " f"Output uploaded to {output_bucket_name}/{output_json_path}."

    except Exception as e:
        logger.error(f"Error processing file '{file_name}': {e}", exc_info=True)
        raise


if __name__ == "__main__":
    test_event = {"bucket": os.getenv("GCS_INPUT_BUCKET"), "name": "g-28.pdf"}
    test_context = None
    logger.info("Starting local function test...")
    result = document2json(test_event, test_context)
    logger.info(f"Function result: {result}")
