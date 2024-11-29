import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from conftest import app, mock_db
from src.model.Firestore import save_form_data_to_firestore


def test_save_form_data_to_firestore(app, mock_db):
    # Mock valid form data
    form_data = [
        {
            "page_number": 1,
            "field_name": "example_field",
            "field_type": "text",
            "initial_value": "example_value",
        }
    ]

    with app.test_request_context(json=form_data):
        # Mock Firestore's set function to simulate successful save
        collection = mock_db.collection.return_value
        document = collection.document.return_value
        document.set.return_value = None

        # Call the function
        response, status_code = save_form_data_to_firestore()

        # Assertions
        assert status_code == 200, "Data should be saved successfully"
        assert response.get_json() == {
            "message": "Form data saved successfully to Firestore."
        }


if __name__ == "__main__":
    test_save_form_data_to_firestore(app, mock_db)
