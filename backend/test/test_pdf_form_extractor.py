import glob
import os
import sys
import warnings

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import FILE_PATH
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor

warnings.filterwarnings("ignore", category=DeprecationWarning, module=".*Swig.*")

PDF_PATHS = glob.glob(os.path.join(FILE_PATH, "*.pdf"))


def test_pdf_form_extractor_get_fields():
    print(PDF_PATHS)
    extractor = PDFFormExtractor(PDF_PATHS[2])
    fields = extractor.get_fields()
    print(fields)
    assert len(fields) > 1, "Should return more than one field"


def test_pdf_form_extractor_get_fields_with_fields():
    print(PDF_PATHS)
    extractor = PDFFormExtractor(PDF_PATHS[2])
    fields = extractor.get_fields_with_sections()
    assert len(fields) > 1, "Should return more than one field"
