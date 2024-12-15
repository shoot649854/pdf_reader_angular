import json
import os
import sys

# import fitz
# from pypdf import PdfReader, generic

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FILE_JSON_PATH, FILE_PDF_PATH, FILE_VALID_PATH
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.DataHandle.JSONHandler import JSONHandler
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor
from src.controller.VertexAI.GenerateResponse import GenerateResponse
from src.logging.Logging import logger

if __name__ == "__main__":
    pdf_path = os.path.join(FILE_PDF_PATH, "I-140.pdf")
    generate_res = GenerateResponse()
    response_parser = JSONFieldLoader()

    extractor = PDFFormExtractor(pdf_path, generate_res, response_parser)
    fields_with_titles = extractor.get_fields_with_titles()
    fields_with_titles = extractor.apply_previous_title(fields_with_titles)
    fields_with_titles_description = extractor.add_descriptions(fields_with_titles)
    # fields_with_titles = extractor.grouping_by_title(fields_with_titles)

    json_output = json.dumps(fields_with_titles, indent=4)
    file_name = "fields_with_titles_description.json"
    with open(os.path.join(FILE_JSON_PATH, file_name), "w") as json_file:
        json_file.write(json_output)

    correct_data_path = os.path.join(FILE_VALID_PATH, "correct_value_140.json")
    fields_data_path = os.path.join(FILE_JSON_PATH, "fields_with_titles_description.json")
    json_handler = JSONHandler()
    correct_data = json_handler.load_data_from_path(correct_data_path)
    fields_data = json_handler.load_data_from_path(fields_data_path)
    correct_titles_dict = {item["field_name"]: item["title"] for item in correct_data}

    # Track correct matches
    correct_matches = 0
    total_fields = len(fields_data)
    for field in fields_data:
        field_name = field["field_name"]
        title = field["title"]

        # Check if the title matches the correct one
        if field_name in correct_titles_dict.keys():
            correct_title = correct_titles_dict[field_name]
            if title == correct_title:
                correct_matches += 1

    # Calculate the percentage of correct matches
    if total_fields > 0:
        match_percentage = (correct_matches / total_fields) * 100
        logger.info(f"Percentage of Correct Titles: {match_percentage:.2f}%")
    else:
        logger.warning("No fields to compare.")
