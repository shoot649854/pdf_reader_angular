import io
import os

from flask import Blueprint, jsonify, request, send_file
from src.config import FILE_PDF_PATH, OUTPUT_PDF_PATH
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.DataHandle.JSONHandler import JSONHandler
from src.controller.PDF.PDFManipulator import PDFManipulator
from src.logging.Logging import logger

# from src.model.GoogleCloudStorage import get_bucket
from src.view.PDFFormFiller import PDFFormFiller

generate_pdf_bp = Blueprint("generate_pdf_bp", __name__)

form_data_storage = {}


@generate_pdf_bp.route("/save_form_data", methods=["POST"])
def save_form_data():
    """Save form data sent by the frontend."""
    form_data = request.json

    if isinstance(form_data, list):
        for page_data in form_data:
            page_number = page_data.get("page_number")
            if page_number is not None:
                form_data_storage[page_number] = page_data
            else:
                return (
                    jsonify({"error": "Invalid data, 'current_form_page_number' missing."}),
                    400,
                )
        return jsonify({"message": "Form data saved successfully."}), 200
    else:
        return jsonify({"error": "Invalid data format, expected a list."}), 400


def get_path_name_from_visa(visa_name: str):
    logger.info(visa_name)
    return os.path.join(FILE_PDF_PATH, "I-140.pdf")


@generate_pdf_bp.route("/generate_pdf/<string:visa_name>", methods=["POST"])
def generate_pdf(visa_name: str):
    """Generate PDF based on the submitted form data."""
    try:
        form_data = request.json
        if not form_data:
            logger.error("No form data provided")
            return {"error": "No form data provided"}, 400

        # Check if form_data is a dictionary or a list of dictionaries
        if not isinstance(form_data, (dict, list)):
            logger.error("Invalid form data format, expected a dictionary or " "list of dictionaries")
            return {"error": "Invalid form data format"}, 400

        if not form_data:
            logger.error("No form data provided")
            return {"error": "No form data provided"}, 400

        path_name = get_path_name_from_visa(visa_name)
        if not path_name:
            logger.error(f"Invalid visa name: {visa_name}")
            return {"error": f"Invalid visa name: {visa_name}"}, 400

        pdf_manipulator = PDFManipulator(path_name)
        data_loader = JSONFieldLoader()
        json_handler = JSONHandler()
        form_filler = PDFFormFiller(data_loader, pdf_manipulator, json_handler)

        # Fill the PDF with the form data
        form_filler.fill_form_from_object(form_data, OUTPUT_PDF_PATH)
        return send_file(
            OUTPUT_PDF_PATH,
            as_attachment=True,
            download_name="filled-form.pdf",
            mimetype="application/pdf",
        )

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return {"error": "An unexpected error occurred"}, 500


@generate_pdf_bp.route("/return_generate_pdf/<string:visa_name>", methods=["POST"])
def return_generate_pdf(visa_name: str):
    """Generate PDF based on the submitted form data."""
    form_data = request.json
    logger.debug(f"Received form_data: {form_data}")

    path_name = get_path_name_from_visa(visa_name)
    pdf_manipulator = PDFManipulator(path_name)
    data_loader = JSONFieldLoader()
    json_handler = JSONHandler()
    form_filler = PDFFormFiller(data_loader, pdf_manipulator, json_handler)
    form_filler.fill_form_from_object(form_data, OUTPUT_PDF_PATH)

    pdf_buffer = io.BytesIO()
    form_filler.fill_form_from_object_to_buffer(form_data, pdf_buffer)
    pdf_buffer.seek(0)

    # try:
    #     bucket = get_bucket()
    #     blob_name = "filled-form.pdf"
    #     blob = bucket.blob(blob_name)
    #     blob.upload_from_file(pdf_buffer, content_type="application/pdf")
    #     signed_url = blob.generate_signed_url(expiration=3600)

    #     logger.info(f"PDF uploaded to GCS bucket '{bucket.name}' as '{blob_name}'.")
    #     return (
    #         jsonify(
    #             {
    #                 "message": "PDF generated and uploaded successfully.",
    #                 "gcs_url": signed_url,
    #             }
    #         ),
    #         200,
    #     )

    # except Exception as e:
    #     logger.error(f"Failed to upload PDF to GCS: {str(e)}")
    #     return jsonify({"error": f"Failed to upload PDF to GCS: {str(e)}"}), 500
