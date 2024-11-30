import os
import sys

# from io import BytesIO
from unittest.mock import patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob
import tempfile

from src.config import FILE_PATH
from src.controller.DataHandle.JSONHandler import JSONHandler

JSON_PATHS = glob.glob(os.path.join(FILE_PATH, "*.data.json"))
PDF_PATHS = glob.glob(os.path.join(FILE_PATH, "*.pdf"))
json_handler = JSONHandler()
url_prefix = "generate_pdf"


###################################################
# save_form_data
###################################################
@patch("src.controller.PDF.PDFManipulator.PDFManipulator.save_pdf")
@patch("src.controller.PDF.PDFManipulator.PDFManipulator.fill_form")
def test_save_form_data(mock_fill_form, mock_save_pdf, client):
    """Test saving form data."""
    for path in JSON_PATHS:
        json_object = json_handler.load_data_from_path(path)
        response = client.post(f"/{url_prefix}/save_form_data", json=json_object)
        assert response.status_code == 200
        assert response.json == {"message": "Form data saved successfully."}

        # Invalid data format
        invalid_data = {"field_data": {"field1": "value1"}}
        response = client.post(
            f"/{url_prefix}/{url_prefix}/save_form_data", json=invalid_data
        )
        assert response.status_code == 500
        # assert "Invalid data format" in response.json["error"]

        # Missing page number
        missing_page_data = [{"field_data": {"field1": "value1"}}]
        response = client.post(
            f"/{url_prefix}/{url_prefix}/save_form_data", json=missing_page_data
        )
        assert response.status_code == 500
        # assert "current_form_page_number" in response.json["error"]


###################################################
# generate_pdf
###################################################


@patch("src.view.PDFFormFiller.PDFFormFiller.fill_form_from_object")
def test_generate_pdf_success(mock_fill_form, client):
    """Test successful PDF generation."""
    visa_name = "I-140"
    form_data = {
        "field1": "value1",
        "field2": "value2",
        # Add other required fields as per your form specification
    }

    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
        with patch("src.config.OUTPUT_PDF_PATH", temp_pdf.name):
            mock_fill_form.return_value = None
            response = client.post(
                f"/{url_prefix}/generate_pdf/{visa_name}", json=form_data
            )
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/pdf"
            assert response.data  # Ensure that PDF data is returned


def test_generate_pdf_no_form_data(client):
    """Test PDF generation with no form data provided."""
    visa_name = "I-140"
    response = client.post(f"/{url_prefix}/generate_pdf/{visa_name}", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "No form data provided"}


def test_generate_pdf_invalid_form_data(client):
    """Test PDF generation with invalid form data format."""
    visa_name = "I-140"
    response = client.post(
        f"/{url_prefix}/generate_pdf/{visa_name}",
        data="Invalid data",
        content_type="application/json",
    )
    assert response.status_code == 500
    # assert response.get_json() == {"error": "Invalid form data format"}


@patch("src.model.GeneratePDF.get_path_name_from_visa")
def test_generate_pdf_invalid_visa_name(mock_get_path_name_from_visa, client):
    """Test PDF generation with an invalid visa name."""
    visa_name = "invalid-visa"
    form_data = {
        "field1": "value1",
        "field2": "value2",
    }

    # Mock get_path_name_from_visa to return None for an invalid visa name
    mock_get_path_name_from_visa.return_value = None

    response = client.post(f"/{url_prefix}/generate_pdf/{visa_name}", json=form_data)
    assert response.status_code == 400
    # assert response.get_json() == {"error": f"Invalid visa name: {visa_name}"}


@patch("src.view.PDFFormFiller.PDFFormFiller.fill_form_from_object")
def test_generate_pdf_exception(mock_fill_form, client):
    """Test PDF generation when an exception occurs during processing."""
    visa_name = "I-140"
    form_data = {
        "field1": "value1",
        "field2": "value2",
    }
    mock_fill_form.side_effect = Exception("Test exception")
    response = client.post(f"/{url_prefix}/generate_pdf/{visa_name}", json=form_data)
    assert response.status_code == 500
    assert response.get_json() == {"error": "An unexpected error occurred"}
