import glob
import os
import sys
import warnings

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import FILE_PDF_PATH
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor
from src.controller.VertexAI.GenerateResponse import GenerateResponse

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*builtin type SwigPy.* has no __module__ attribute")

PDF_PATHS = glob.glob(os.path.join(FILE_PDF_PATH, "*.pdf"))


def test_pdf_form_extractor_get_fields_with_fields():
    generate_res = GenerateResponse()
    response_parser = JSONFieldLoader()

    extractor = PDFFormExtractor(PDF_PATHS[2], generate_res, response_parser)
    fields = extractor.get_fields_with_titles()
    assert len(fields) > 1, "Should return more than one field"
