# import io

# from flask import Flask, jsonify, request, send_file
# from PyPDF2 import PdfReader, PdfWriter
# app = Flask(__name__)

from src.config import I140_JSON_PATH, I140_PATH, OUTPUT_PDF_PATH
from src.controller.JSONFieldDataLoader import JSONFieldDataLoader

# from src.controller.PDFFill import PDFFill
from src.controller.PDFFormFiller import PDFFormFiller
from src.controller.PDFManipulator import PDFManipulator


def main():
    data_loader = JSONFieldDataLoader()
    pdf_manipulator = PDFManipulator(I140_PATH)
    form_filler = PDFFormFiller(data_loader, pdf_manipulator)
    form_filler.fill_form(I140_JSON_PATH, OUTPUT_PDF_PATH)

    # pdf_manipulator = PDFFill(pdf_path=I140_PATH)
    # pdf_manipulator.fill_family_name("Doe")
    # pdf_manipulator.fill_family_name("")
    # pdf_manipulator.save_pdf(OUTPUT_PDF_PATH)


if __name__ == "__main__":
    main()
