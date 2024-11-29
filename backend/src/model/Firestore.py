from flask import Blueprint, jsonify, request

# from flask_cors import cross_origin
from src import db
from src.logging.Logging import logger

form_data_storage = {}

firestore_bp = Blueprint("firestore_bp", __name__)


@firestore_bp.route("/save_form_data_to_firestore", methods=["POST"])
def save_form_data_to_firestore():
    """Save form data sent by the frontend to Firestore."""
    form_data = request.json

    if not isinstance(form_data, list):
        return jsonify({"error": "Invalid data format, expected a list."}), 400

    for page_data in form_data:
        required_fields = {"field_name", "page_number", "field_type", "initial_value"}
        missing_fields = required_fields - page_data.keys()
        if missing_fields:
            return (
                jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}),
                400,
            )

        page_number = page_data["page_number"]
        form_ref = db.collection("forms").document(page_data["field_name"])
        try:
            form_ref.set(page_data)
            logger.info(f"Form data for page {page_number} saved to Firestore.")
        except Exception as e:
            logger.error(f"Error saving form data for page {page_number}: {e}")
            return jsonify({"error": "Failed to save form data to Firestore."}), 500

    return jsonify({"message": "Form data saved successfully to Firestore."}), 200


@firestore_bp.route("/get_form_data/<string:field_name>", methods=["GET"])
def get_form_data(field_name):
    """Retrieve form data for a specific field_name from Firestore."""
    form_ref = db.collection("forms").document(field_name)
    doc = form_ref.get()

    if doc.exists:
        form_data = doc.to_dict()
        logger.info(f"Form data for field '{field_name}' retrieved from Firestore.")
        return jsonify(form_data), 200
    else:
        logger.warning(f"No form data found for field '{field_name}'.")
        return jsonify({"error": f"No form data found for field '{field_name}'."}), 404


# UPDATE - Update form data for a specific field_name in Firestore
@firestore_bp.route("/update_form_data/<string:field_name>", methods=["PUT"])
def update_form_data(field_name):
    """Update form data for a specific field_name in Firestore."""
    updated_data = request.json
    form_ref = db.collection("forms").document(field_name)
    doc = form_ref.get()

    if doc.exists:
        form_ref.update(updated_data)
        logger.info(f"Form data for field '{field_name}' updated in Firestore.")
        return (
            jsonify(
                {"message": f"Form data for field '{field_name}' updated successfully."}
            ),
            200,
        )
    else:
        logger.warning(f"No form data found for field '{field_name}'.")
        return jsonify({"error": f"No form data found for field '{field_name}'."}), 404


# DELETE - Delete form data for a specific field_name from Firestore
@firestore_bp.route("/delete_form_data/<string:field_name>", methods=["DELETE"])
def delete_form_data(field_name):
    """Delete form data for a specific field_name from Firestore."""
    form_ref = db.collection("forms").document(field_name)
    doc = form_ref.get()

    if doc.exists:
        form_ref.delete()
        logger.info(f"Form data for field '{field_name}' deleted from Firestore.")
        return (
            jsonify(
                {"message": f"Form data for field '{field_name}' deleted successfully."}
            ),
            200,
        )
    else:
        logger.warning(f"No form data found for field '{field_name}'.")
        return jsonify({"error": f"No form data found for field '{field_name}'."}), 404


@firestore_bp.route("/delete_all_form_data", methods=["DELETE"])
def delete_all_form_data():
    """Delete all form data from Firestore."""
    forms_ref = db.collection("forms")
    docs = forms_ref.stream()
    deleted_count = 0
    for doc in docs:
        forms_ref.document(doc.id).delete()
        deleted_count += 1

    if deleted_count > 0:
        logger.info(
            f"All form data deleted from Firestore. Total deleted: {deleted_count}."
        )
        return (
            jsonify(
                {
                    "message": "All form data deleted successfully. Total deleted: "
                    f"{deleted_count}."
                }
            ),
            200,
        )
    else:
        logger.warning("No form data found to delete.")
        return jsonify({"error": "No form data found to delete."}), 404


# READ ALL - Retrieve all form data from Firestore
@firestore_bp.route("/get_all_form_data", methods=["GET"])
def get_all_form_data():
    """Retrieve all form data from Firestore."""
    logger.info("Route /get_all_form_data has been accessed.")

    try:
        forms_ref = db.collection("forms")
        logger.info("Firestore connection successful.")
    except Exception as e:
        logger.error(f"Error connecting to Firestore: {str(e)}")
        return jsonify({"error": "Firestore connection failed."}), 500

    docs = forms_ref.stream()

    all_form_data = []
    for doc in docs:
        form_data = doc.to_dict()
        all_form_data.append(form_data)

    if all_form_data:
        logger.info("All form data retrieved from Firestore.")
        return jsonify(all_form_data), 200
    else:
        logger.warning("No form data found in Firestore.")
        return jsonify({"error": "No form data found."}), 404
