import os
import sys
from unittest.mock import mock_open, patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.controller.PDF.PDFFormExtractor import PDFFormExtractor


def test_pdf_form_extractor_get_fields():
    with patch("builtins.open", mock_open(read_data="PDF content")), patch(
        "pypdf.PdfReader"
    ) as MockPdfReader:
        MockPdfReader.return_value.pages = []
        extractor = PDFFormExtractor("dummy_path.pdf")
        fields = extractor.get_fields()
        assert fields == [], "Should return an empty list when no fields are present"


if __name__ == "__main__":
    test_pdf_form_extractor_get_fields()
