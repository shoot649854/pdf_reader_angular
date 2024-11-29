import os
import sys
from unittest.mock import Mock, patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from conftest import app
from src.model.GeneratePDF import generate_pdf


def test_generate_pdf(app):
    with app.test_request_context(json={"form_data": "sample_data"}):
        with patch(
            "src.controller.PDF.PDFManipulator.PDFManipulator.fill_form",
            return_value=None,
        ), patch(
            "src.controller.PDF.PDFManipulator.PDFManipulator.save_pdf",
            return_value=None,
        ), patch(
            "src.model.GeneratePDF.PDFFormFiller",
            return_value=Mock(),
        ):
            response = generate_pdf()
            assert response.status_code == 200, "PDF should be generated successfully"


if __name__ == "__main__":
    test_generate_pdf(app)
