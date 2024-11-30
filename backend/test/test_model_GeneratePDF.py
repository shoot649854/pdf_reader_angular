import os
import sys
from io import BytesIO
from unittest.mock import patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob

from src.config import FILE_PATH
from src.controller.DataHandle.JSONHandler import JSONHandler

JSON_PATHS = glob.glob(os.path.join(FILE_PATH, "*updated.data.json"))
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
        response = client.post(f"/{url_prefix}/save_form_data", json=invalid_data)
        assert response.status_code == 400
        assert "Invalid data format" in response.json["error"]

        # Missing page number
        missing_page_data = [{"field_data": {"field1": "value1"}}]
        response = client.post(f"/{url_prefix}/save_form_data", json=missing_page_data)
        assert response.status_code == 400
        assert "current_form_page_number" in response.json["error"]


@patch("src.controller.PDF.PDFManipulator.PDFManipulator.save_pdf")
@patch("src.controller.PDF.PDFManipulator.PDFManipulator.fill_form")
def test_generate_pdf(mock_fill_form, mock_save_pdf, client):
    """Test generating PDF."""
    mock_save_pdf.return_value = None
    mock_fill_form.return_value = None

    for path in PDF_PATHS:
        # Valid form data
        valid_form_data = {"field1": "value1", "field2": "value2"}

        response = client.post(
            f"/{url_prefix}/generate_pdf/{path}", json=valid_form_data
        )

        # Debug the response object
        print("Response data:", response.data.decode())
        print("Response status code:", response.status_code)

        # Assertions
        assert (
            response.status_code == 200
        ), f"Unexpected status code: {response.status_code}"

        # Invalid form data
        invalid_form_data = {"invalid_key": "value"}
        response = client.post(
            f"/{url_prefix}/generate_pdf/{path}", json=invalid_form_data
        )
        print("Invalid form response data:", response.data.decode())
        print("Invalid form response status code:", response.status_code)

        assert (
            response.status_code != 200
        ), f"Unexpected status code for invalid data: {response.status_code}"


# if __name__ == "__main__":
#     from conftest import client

#     test_generate_pdf(client)
