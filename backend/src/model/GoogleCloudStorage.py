import os
import tempfile

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_cors import cross_origin
from google.cloud import storage
from src.logging.Logging import logger

storage_bp = Blueprint("storage_bp", __name__)


def get_gcs_client():
    """Initialize and return a Google Cloud Storage client."""
    return storage.Client()


def get_bucket():
    """Retrieve the GCS bucket from configuration."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        logger.error("GCS_BUCKET_NAME is not set in configuration.")
        raise EnvironmentError("GCS_BUCKET_NAME is not set in configuration.")
    client = get_gcs_client()
    return client.bucket(bucket_name)


@cross_origin(origins="http://localhost:4200")
@storage_bp.route("/upload_file", methods=["POST"])
def upload_file():
    """Upload a file to Google Cloud Storage."""
    if "file" not in request.files:
        logger.warning("No file part in the request.")
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]

    if file.filename == "":
        logger.warning("No selected file.")
        return jsonify({"error": "No selected file."}), 400

    if file:
        try:
            bucket = get_bucket()
            blob = bucket.blob(file.filename)
            blob.upload_from_file(file.stream)
            logger.info(
                f"File '{file.filename}' uploaded to GCS bucket '{bucket.name}'."
            )
            return (
                jsonify({"message": f"File '{file.filename}' uploaded successfully."}),
                200,
            )
        except Exception as e:
            logger.error(f"Failed to upload file '{file.filename}': {str(e)}")
            return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500


@storage_bp.route("/download_file/<string:filename>", methods=["GET"])
def download_file(filename):
    """Download a file from Google Cloud Storage."""
    try:
        bucket = get_bucket()
        blob = bucket.blob(filename)
        if not blob.exists():
            logger.warning(
                f"File '{filename}' does not exist in bucket '{bucket.name}'."
            )
            return jsonify({"error": f"File '{filename}' does not exist."}), 404

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            blob.download_to_filename(temp_file.name)
            logger.info(
                f"File '{filename}' downloaded from GCS bucket '{bucket.name}'."
            )
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=filename,
                mimetype=blob.content_type,
            )
    except Exception as e:
        logger.error(f"Failed to download file '{filename}': {str(e)}")
        return jsonify({"error": f"Failed to download file: {str(e)}"}), 500


@storage_bp.route("/list_files", methods=["GET"])
def list_files():
    """List all files in the Google Cloud Storage bucket."""
    try:
        bucket = get_bucket()
        blobs = bucket.list_blobs()
        files = [blob.name for blob in blobs]
        logger.info(f"Listed {len(files)} files from GCS bucket '{bucket.name}'.")
        return jsonify({"files": files}), 200
    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        return jsonify({"error": f"Failed to list files: {str(e)}"}), 500


@storage_bp.route("/delete_file/<string:filename>", methods=["DELETE"])
def delete_file(filename):
    """Delete a file from Google Cloud Storage."""
    try:
        bucket = get_bucket()
        blob = bucket.blob(filename)
        if not blob.exists():
            logger.warning(
                f"File '{filename}' does not exist in bucket '{bucket.name}'."
            )
            return jsonify({"error": f"File '{filename}' does not exist."}), 404

        blob.delete()
        logger.info(f"File '{filename}' deleted from GCS bucket '{bucket.name}'.")
        return jsonify({"message": f"File '{filename}' deleted successfully."}), 200
    except Exception as e:
        logger.error(f"Failed to delete file '{filename}': {str(e)}")
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500
