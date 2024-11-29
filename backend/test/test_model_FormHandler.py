import json
import os
import sys
from unittest.mock import mock_open, patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob

from src.config import FILE_PATH
from src.controller.DataHandle.JSONHandler import JSONHandler
from src.model.FormHandler import DATA_PATH

JSON_PATHS = glob.glob(os.path.join(FILE_PATH, "*updated.data.json"))
json_handler = JSONHandler()

url_prefix = "form"


###################################################
# update_from_data
###################################################
@patch("builtins.open", new_callable=mock_open)
def test_update_form_data_valid(mock_open, client):
    """Test updating form data with valid input."""
    updated_data = [
        {
            "field_name": "Full Name",
            "field_type": "text",
            "initial_value": "John Doe",
            "page_number": 1,
        },
        {
            "field_name": "Date of Birth",
            "field_type": "date",
            "initial_value": "1990-01-01",
            "page_number": 1,
        },
    ]

    response = client.post(f"/{url_prefix}/update-form-data", json=updated_data)
    assert response.status_code == 200
    assert response.get_json() == {"message": "Form data updated successfully."}

    # Verification
    mock_open.assert_called_once_with(DATA_PATH, "w")
    written_content = "".join(call[0][0] for call in mock_open().write.call_args_list)
    assert written_content == json.dumps(updated_data, indent=2)


@patch("builtins.open", new_callable=mock_open)
def test_update_form_data_invalid_format(mock_open, client):
    """Test updating form data with invalid input format."""
    invalid_data = {
        "field_name": "Full Name",
        "initial_value": "John Doe",
    }

    response = client.post(f"/{url_prefix}/update-form-data", json=invalid_data)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid data format. Expected an array."}

    # Verification
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open)
def test_update_form_data_exception(mock_open, client):
    """Test handling exceptions during the update."""
    mock_open.side_effect = Exception("Test exception")

    valid_data = [
        {
            "field_name": "Full Name",
            "field_type": "text",
            "initial_value": "John Doe",
            "page_number": 1,
        }
    ]

    response = client.post(f"/{url_prefix}/update-form-data", json=valid_data)
    assert response.status_code == 500
    assert response.get_json() == {"error": "Test exception"}
