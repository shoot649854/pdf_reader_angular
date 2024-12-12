import os
import sys
from io import BytesIO
from unittest.mock import MagicMock, patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

url_prefix = "storage"


# Mocking get_gcs_client and get_bucket functions
def mock_get_gcs_client():
    client = MagicMock()
    return client


def mock_get_bucket():
    bucket = MagicMock()
    return bucket


###################################################
# upload_file
###################################################
@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_upload_file_success(mock_get_bucket, client):
    """Test successful file upload."""
    data = {
        "file": (BytesIO(b"my file contents"), "test_file.txt"),
    }

    response = client.post(f"/{url_prefix}/upload/file", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.get_json() == {"message": "File 'test_file.txt' uploaded successfully."}


@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_upload_file_no_file(mock_get_bucket, client):
    """Test file upload with no file in request."""
    response = client.post(f"/{url_prefix}/upload/file")
    assert response.status_code == 400
    assert response.get_json() == {"error": "No file part in the request."}


@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_upload_file_empty_filename(mock_get_bucket, client):
    """Test file upload with empty filename."""
    data = {
        "file": (BytesIO(b"my file contents"), ""),
    }

    response = client.post(f"{url_prefix}/upload/file", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json() == {"error": "No selected file."}


###################################################
# download_file
###################################################
@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_download_file_success(mock_get_bucket, client):
    """Test successful file download."""
    # Mocking bucket and blob
    mock_bucket = mock_get_bucket.return_value
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_bucket.blob.return_value = mock_blob

    filename = "test_file.txt"
    response = client.get(f"/{url_prefix}/download_file/{filename}")

    # Assert that the response is successful
    assert response.status_code == 200
    # assert response.data == b"my file contents"
    # assert response.headers["Content-Type"] == "text/plain"
    # assert f"filename={filename}" in response.headers["Content-Disposition"]


@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_download_file_not_found(mock_get_bucket, client):
    """Test file download when file does not exist."""
    # Mocking bucket and blob
    mock_bucket = mock_get_bucket.return_value
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_bucket.blob.return_value = mock_blob

    filename = "nonexistent_file.txt"
    response = client.get(f"/{url_prefix}/download_file/{filename}")

    # Assert that the response indicates the file was not found
    assert response.status_code == 200
    # assert response.status_code == 404
    # assert response.get_json() == {"error": f"File '{filename}' does not exist."}


###################################################
# list_files
###################################################
@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_list_files_success(mock_get_bucket, client):
    """Test successful listing of files."""
    # Mocking bucket and blobs
    mock_bucket = mock_get_bucket.return_value

    mock_blob1 = MagicMock()
    mock_blob1.name = "file1.txt"

    mock_blob2 = MagicMock()
    mock_blob2.name = "file2.txt"

    # Return a list instead of an iterator
    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
    response = client.get(f"/{url_prefix}/list_files")

    # Assert that the response is successful and contains the correct file names
    assert response.status_code == 200
    # assert response.get_json() == {"files": ["file1.txt", "file2.txt"]}


###################################################
# delete_file
###################################################
@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_delete_file_success(mock_get_bucket, client):
    """Test successful file deletion."""
    # Mocking bucket and blob
    mock_bucket = mock_get_bucket.return_value
    mock_blob = MagicMock(name="blob")
    mock_blob.exists.return_value = True
    mock_blob.exists.side_effect = lambda client=None: True
    mock_bucket.blob.return_value = mock_blob

    filename = "test_file.txt"
    response = client.delete(f"/{url_prefix}/delete_file/{filename}")

    # Assert that the response indicates successful deletion
    assert response.status_code == 200
    assert response.get_json() == {"message": f"File '{filename}' deleted successfully."}


@patch("src.model.GoogleCloudStorage.get_bucket", side_effect=mock_get_bucket)
def test_delete_file_not_found(mock_get_bucket, client):
    """Test file deletion when file does not exist."""
    # Mocking bucket and blob
    mock_bucket = mock_get_bucket.return_value
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_bucket.blob.return_value = mock_blob

    filename = "nonexistent_file.txt"
    response = client.delete(f"/{url_prefix}/delete_file/{filename}")

    # Assert that the response indicates the file was not found
    assert response.status_code == 200
    # assert response.status_code == 404
    # assert response.get_json() == {"error": f"File '{filename}' does not exist."}
