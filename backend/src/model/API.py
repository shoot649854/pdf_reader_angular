import io

from flask import Flask, jsonify, request, send_file
from src.config import I140_PATH, OUTPUT_PDF_PATH
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.PDF.PDFManipulator import PDFManipulator
from src.view.PDFFormFiller import PDFFormFiller

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"message": "Welcome to PDF Form Filler API"})


@app.route("/fill_form", methods=["POST"])
def fill_form():
    try:
        if "json_data" in request.files:
            json_file = request.files["json_data"]
            json_data = json_file.read().decode("utf-8")
        else:
            return jsonify({"error": "No JSON file provided."}), 400

        data_loader = JSONFieldLoader()
        pdf_manipulator = PDFManipulator(I140_PATH)
        form_filler = PDFFormFiller(data_loader, pdf_manipulator)

        json_path = io.StringIO(json_data)
        form_filler.fill_form(json_path, OUTPUT_PDF_PATH)
        return send_file(OUTPUT_PDF_PATH, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
