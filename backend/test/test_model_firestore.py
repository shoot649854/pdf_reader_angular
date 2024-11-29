import os
import sys
from unittest.mock import MagicMock, patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob

from src.config import FILE_PATH
from src.controller.DataHandle.JSONHandler import JSONHandler

JSON_PATHS = glob.glob(os.path.join(FILE_PATH, "*updated.data.json"))
json_handler = JSONHandler()

url_prefix = "firestore"


###################################################
# save_form_data_to_firestore
###################################################
def test_save_form_data_to_firestore_valid(client, mock_db):
    for path in JSON_PATHS:
        json_object = json_handler.load_data_from_path(path)
        response = client.post(
            f"/{url_prefix}/save_form_data_to_firestore", json=json_object
        )

        # Mock Firestore's set function
        collection = mock_db.collection.return_value
        document = collection.document.return_value
        document.set.return_value = None

        # Assertions
        assert response.status_code == 200
        assert response.get_json() == {
            "message": "Form data saved successfully to Firestore."
        }


###################################################
# get_form_data
###################################################
@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_get_form_data_valid(mock_db, client):
    field_name = "test_field"
    form_ref = mock_db.collection("forms").document(field_name)
    form_ref.get.return_value.exists = True
    form_ref.get.return_value.to_dict.return_value = {
        "field_name": field_name,
        "page_number": 1,
        "field_type": "text",
        "initial_value": "Sample value",
    }

    response = client.get(f"/{url_prefix}/get_form_data/{field_name}")
    assert response.status_code == 200
    assert response.get_json() == {
        "field_name": field_name,
        "page_number": 1,
        "field_type": "text",
        "initial_value": "Sample value",
    }


@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_get_form_data_not_found(mock_db, client):
    field_name = "non_existent_field"
    form_ref = mock_db.collection("forms").document(field_name)
    form_ref.get.return_value.exists = False

    response = client.get(f"/{url_prefix}/get_form_data/{field_name}")
    assert response.status_code == 404
    assert response.get_json() == {
        "error": f"No form data found for field '{field_name}'."
    }


###################################################
# update_from_data
###################################################
@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_update_form_data_valid(mock_db, client):
    field_name = "test_field"
    updated_data = {"initial_value": "Updated value"}

    form_ref = mock_db.collection("forms").document(field_name)
    form_ref.get.return_value.exists = True

    response = client.put(
        f"/{url_prefix}/update_form_data/{field_name}", json=updated_data
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "message": f"Form data for field '{field_name}' updated successfully."
    }


@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_update_form_data_not_found(mock_db, client):
    field_name = "non_existent_field"
    updated_data = {"initial_value": "Updated value"}

    form_ref = mock_db.collection("forms").document(field_name)
    form_ref.get.return_value.exists = False

    response = client.put(
        f"/{url_prefix}/update_form_data/{field_name}", json=updated_data
    )
    assert response.status_code == 404
    assert response.get_json() == {
        "error": f"No form data found for field '{field_name}'."
    }


###################################################
# delete_form_data
###################################################
@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_delete_form_data_valid(mock_db, client):
    field_name = "test_field"

    form_ref = mock_db.collection("forms").document(field_name)
    form_ref.get.return_value.exists = True

    response = client.delete(f"/{url_prefix}/delete_form_data/{field_name}")
    assert response.status_code == 200
    assert response.get_json() == {
        "message": f"Form data for field '{field_name}' deleted successfully."
    }


@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_delete_form_data_not_found(mock_db, client):
    field_name = "non_existent_field"

    form_ref = mock_db.collection("forms").document(field_name)
    form_ref.get.return_value.exists = False

    response = client.delete(f"/{url_prefix}/delete_form_data/{field_name}")
    assert response.status_code == 404
    assert response.get_json() == {
        "error": f"No form data found for field '{field_name}'."
    }


###################################################
# delete_all_form_data
###################################################


@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_delete_all_form_data(mock_db, client):
    forms_ref = mock_db.collection("forms")
    mock_docs = [MagicMock(id="doc1"), MagicMock(id="doc2"), MagicMock(id="doc3")]
    forms_ref.stream.return_value = mock_docs

    response = client.delete(f"/{url_prefix}/delete_all_form_data")
    assert response.status_code == 200
    assert response.get_json() == {
        "message": "All form data deleted successfully. Total deleted: 3."
    }


@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_delete_all_form_data_none(mock_db, client):
    forms_ref = mock_db.collection("forms")
    forms_ref.stream.return_value = []

    response = client.delete(f"/{url_prefix}/delete_all_form_data")
    assert response.status_code == 404
    assert response.get_json() == {"error": "No form data found to delete."}


###################################################
# get_all_form_data
###################################################
@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_get_all_form_data(mock_db, client):
    forms_ref = mock_db.collection("forms")
    mock_docs = [
        MagicMock(to_dict=lambda: {"field_name": "test_field_1", "value": "data1"}),
        MagicMock(to_dict=lambda: {"field_name": "test_field_2", "value": "data2"}),
    ]
    forms_ref.stream.return_value = mock_docs

    response = client.get(f"/{url_prefix}/get_all_form_data")
    assert response.status_code == 200
    assert response.get_json() == [
        {"field_name": "test_field_1", "value": "data1"},
        {"field_name": "test_field_2", "value": "data2"},
    ]


@patch("src.model.Firestore.db", new_callable=lambda: MagicMock())
def test_get_all_form_data_none(mock_db, client):
    forms_ref = mock_db.collection("forms")
    forms_ref.stream.return_value = []

    response = client.get(f"/{url_prefix}/get_all_form_data")
    assert response.status_code == 404
    assert response.get_json() == {"error": "No form data found."}
