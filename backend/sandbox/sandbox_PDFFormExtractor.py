import json
import os
import sys

# import fitz
# from pypdf import PdfReader, generic

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FILE_PATH
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor
from src.controller.VertexAI.GenerateResponse import GenerateResponse

if __name__ == "__main__":
    pdf_path = os.path.join(FILE_PATH, "I-140.pdf")
    generate_res = GenerateResponse()
    response_parser = JSONFieldLoader()

    extractor = PDFFormExtractor(pdf_path, generate_res, response_parser)
    fields_with_titles = extractor.get_fields_with_titles()
    fields_with_titles = extractor.apply_previous_title(fields_with_titles)
    fields_with_titles_description = extractor.generating_descriptions(fields_with_titles)
    fields_with_titles = extractor.grouping_by_title(fields_with_titles)

    json_output = json.dumps(fields_with_titles, indent=4)
    file_name = "fields_with_titles_description.json"
    with open(os.path.join(FILE_PATH, file_name), "w") as json_file:
        json_file.write(json_output)
