import io

from flask import Blueprint, jsonify, request, send_file
from src.config import I140_PATH, OUTPUT_PDF_PATH
from src.controller.JSONFieldDataLoader import JSONFieldDataLoader
from src.controller.PDFFormFiller import PDFFormFiller
from src.controller.PDFManipulator import PDFManipulator

# from src.logging.Logging import logger

generate_pdf_bp = Blueprint("generate_pdf_bp", __name__)

form_data_storage = {}


@generate_pdf_bp.route("/save_form_data", methods=["POST"])
def save_form_data():
    """Save form data sent by the frontend."""
    form_data = request.json

    if isinstance(form_data, list):
        for page_data in form_data:
            page_number = page_data.get("current_form_page_number")
            if page_number is not None:
                form_data_storage[page_number] = page_data
            else:
                return (
                    jsonify(
                        {"error": "Invalid data, 'current_form_page_number' missing."}
                    ),
                    400,
                )
        return jsonify({"message": "Form data saved successfully."}), 200
    else:
        return jsonify({"error": "Invalid data format, expected a list."}), 400


@generate_pdf_bp.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    """Generate PDF based on the submitted form data."""
    form_data = request.json
    pdf_manipulator = PDFManipulator(I140_PATH)
    data_loader = JSONFieldDataLoader()
    form_filler = PDFFormFiller(data_loader, pdf_manipulator)
    form_filler.fill_form_from_object(form_data, OUTPUT_PDF_PATH)
    return send_file(
        OUTPUT_PDF_PATH, as_attachment=True, download_name="filled-form.pdf"
    )


@generate_pdf_bp.route("/return_generate_pdf", methods=["POST"])
def return_generate_pdf():
    """Generate PDF based on the submitted form data."""
    form_data = request.json
    # logger.info(f"Received form_data: {form_data}")

    pdf_manipulator = PDFManipulator(I140_PATH)
    data_loader = JSONFieldDataLoader()
    form_filler = PDFFormFiller(data_loader, pdf_manipulator)

    pdf_buffer = io.BytesIO()

    # Fill the PDF form using the form data and write it to the buffer
    form_filler.fill_form_from_object_to_buffer(form_data, pdf_buffer)

    # Check the buffer size for debugging
    pdf_buffer.seek(0)
    # buffer_content = pdf_buffer.getvalue()
    # logger.info(f"Buffer size before sending: {len(buffer_content)} bytes")

    # with open("filled-debug.pdf", "wb") as f:
    #     f.write(buffer_content)

    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="filled-form.pdf",
        mimetype="application/pdf",
    )
