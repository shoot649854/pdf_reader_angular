import os

from flask import Blueprint, jsonify, request, send_file
from google.cloud import storage
from src.logging.Logging import logger
from werkzeug.utils import secure_filename

storage_bp = Blueprint("storage_bp", __name__)


def get_gcs_client() -> storage.Client:
    """Initialize and return a Google Cloud Storage client."""
    try:
        return storage.Client()
    except Exception as e:
        logger.error(f"Failed to initialize GCS client: {e}")
        raise RuntimeError("Could not initialize Google Cloud Storage client.") from e


def get_bucket(bucket_name: str) -> storage.Bucket:
    """Retrieve the GCS bucket from configuration."""
    if not bucket_name:
        logger.error("Bucket name is required but was not provided.")
        raise ValueError("Bucket name is required.")

    client = get_gcs_client()
    try:
        return client.bucket(bucket_name)
    except Exception as e:
        logger.error(f"Failed to retrieve bucket {bucket_name}: {e}")
        raise RuntimeError(f"Could not retrieve bucket: {bucket_name}") from e


@storage_bp.route("/upload/file", methods=["POST"])
@storage_bp.route("/upload/file/<string:folder_name>", methods=["POST"])
def upload_file(folder_name: str = None):
    """Upload a single file to Google Cloud Storage."""
    if "file" not in request.files:
        logger.warning("No file part in the request.")
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]

    if file.filename == "":
        logger.warning("No selected file.")
        return jsonify({"error": "No selected file."}), 400

    try:
        filename = secure_filename(file.filename)
        filename_without_extension = os.path.splitext(filename)[0]
        gcs_path = f"{folder_name}/{filename_without_extension}/{filename}"
        if not folder_name:
            gcs_path = f"{filename_without_extension}/{filename}"

        bucket = get_bucket()
        blob = bucket.blob(gcs_path)
        blob.upload_from_file(file.stream)

        logger.info(f"File '{file.filename}' uploaded to bucket '{bucket.name}' " f"at '{gcs_path}'.")

        return (
            jsonify({"message": f"File '{file.filename}' uploaded successfully."}),
            200,
        )

    except Exception as e:
        logger.error(f"Failed to upload file '{file.filename}': {str(e)}")
        return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500


@storage_bp.route("/upload/files", methods=["POST"])
@storage_bp.route("/upload/files/<string:folder_name>", methods=["POST"])
def upload_files(folder_name: str = None):
    """Upload multiple files to Google Cloud Storage."""
    if "file" not in request.files:
        logger.warning("No file part in the request.")
        return jsonify({"error": "No file part in the request."}), 400

    files = request.files.getlist("file")

    if len(files) == 0 or all(file.filename == "" for file in files):
        logger.warning("No selected files.")
        return jsonify({"error": "No selected files."}), 400

    try:
        for file in files:
            filename = secure_filename(file.filename)
            filename_without_extension = os.path.splitext(filename)[0]
            gcs_path = f"{folder_name}/{filename_without_extension}/{filename}"
            if not folder_name:
                gcs_path = f"{filename_without_extension}/{filename}"

            bucket = get_bucket()
            blob = bucket.blob(gcs_path)
            blob.upload_from_file(file.stream)
            logger.info(f"File '{file.filename}' uploaded to bucket '{bucket.name}' " f"at '{gcs_path}'.")

        return jsonify({"message": "Files uploaded successfully!"}), 200

    except Exception as e:
        logger.error(f"Failed to upload files: {str(e)}")
        return jsonify({"error": f"Failed to upload files: {str(e)}"}), 500


def download_file(bucket_name, source_blob_name, destination_path):
    """Download a file from Google Cloud Storage and save it to a specified path."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        if not blob.exists(client=bucket.client):
            logger.warning(f"File '{source_blob_name}' does not exist in bucket '{bucket.name}'.")
            raise FileNotFoundError(f"File '{source_blob_name}' does not exist in bucket '{bucket.name}'.")

        # Download blob content into memory
        with open(destination_path, "wb") as f:
            blob.download_to_file(f)

        logger.info(f"File '{source_blob_name}' downloaded from GCS bucket '{bucket.name}' " f"to '{destination_path}'.")
    except Exception as e:
        logger.error(f"Failed to download file '{source_blob_name}': {str(e)}")
        raise


@storage_bp.route("/download_file/<string:filename>", methods=["GET"])
def route_download_file(filename):
    """Flask route to download a file from Google Cloud Storage."""
    try:
        file_obj = download_file(filename)
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf",
        )

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
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
        if not blob.exists(client=bucket.client):
            logger.warning(f"File '{filename}' does not exist in bucket '{bucket.name}'.")
            return jsonify({"error": f"File '{filename}' does not exist."}), 404

        blob.delete()
        logger.info(f"File '{filename}' deleted from GCS bucket '{bucket.name}'.")
        return jsonify({"message": f"File '{filename}' deleted successfully."}), 200
    except Exception as e:
        logger.error(f"Failed to delete file '{filename}': {str(e)}")
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500
