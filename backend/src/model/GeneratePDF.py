from flask import Flask, jsonify, request, send_file
from src import db
from src.config import I140_PATH, OUTPUT_PDF_PATH
from src.controller.JSONFieldDataLoader import JSONFieldDataLoader
from src.controller.PDFFormFiller import PDFFormFiller
from src.controller.PDFManipulator import PDFManipulator
from src.logging.Logging import logger

app = Flask(__name__)
form_data_storage = {}


@app.route("/save_form_data_to_firestore", methods=["POST"])
def save_form_data_to_firestore():
    """Save form data sent by the frontend to Firestore."""
    form_data = request.json

    if isinstance(form_data, list):
        for page_data in form_data:
            # Extract page number and other data fields
            page_number = page_data.get("page_number")
            field_name = page_data.get("field_name")
            description = page_data.get("description")
            field_type = page_data.get("field_type")
            initial_value = page_data.get("initial_value")

            # Check if page number is provided
            if page_number is not None:
                form_ref = db.collection("forms").document(str(page_number))
                form_document_data = {
                    "field_name": field_name,
                    "description": description,
                    "field_type": field_type,
                    "initial_value": initial_value,
                    "page_number": page_number,
                }

                # Save the data to Firestore
                form_ref.set(form_document_data)
                logger.info(f"Form data for page {page_number} saved to Firestore.")
            else:
                return (
                    jsonify({"error": "Invalid data, 'page_number' is missing."}),
                    400,
                )

        return jsonify({"message": "Form data saved successfully to Firestore."}), 200
    else:
        return jsonify({"error": "Invalid data format, expected a list."}), 400


@app.route("/save_form_data", methods=["POST"])
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


@app.route("/generate_pdf", methods=["POST"])
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
