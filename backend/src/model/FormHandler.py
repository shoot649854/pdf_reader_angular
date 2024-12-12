import json
import os

from flask import Blueprint, jsonify, request

form_bp = Blueprint("form_controller", __name__)

current_dir = os.path.dirname(__file__)  # backend/src/controller
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
DATA_PATH = os.path.join(project_root, "frontend", "src", "assets", "form_data.json")
PERSONAL_INFO = os.path.abspath(os.path.join(current_dir, "../../data/personal_data.json"))


@form_bp.route("/update-form-data", methods=["POST"])
def update_form_data():
    try:
        updated_data = request.get_json()

        if not isinstance(updated_data, list):
            return jsonify({"error": "Invalid data format. Expected an array."}), 400

        with open(DATA_PATH, "w") as json_file:
            json.dump(updated_data, json_file, indent=2)

        return jsonify({"message": "Form data updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
