from flask import Flask, jsonify, request, send_file
from src.config import I140_PATH, OUTPUT_PDF_PATH
from src.controller.JSONFieldDataLoader import JSONFieldDataLoader
from src.controller.PDFFormFiller import PDFFormFiller
from src.controller.PDFManipulator import PDFManipulator

app = Flask(__name__)
form_data_storage = {}


@app.route("/save_form_data", methods=["POST"])
def save_form_data():
    """Save form data sent by the frontend."""
    form_data = request.json  # Assuming this is a list of form data dictionaries

    if isinstance(form_data, list):
        # Loop through the list and save each form page
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
