import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import I140_JSON_PATH, I140_PATH, LOG_FILE_PATH


def test_log_file_path():
    assert os.path.exists(os.path.dirname(LOG_FILE_PATH)), "Log file path should exist"


def test_data_paths():
    assert I140_PATH.endswith("I-140.pdf"), "I140_PATH should point to I-140.pdf"
    assert I140_JSON_PATH.endswith("I-140_fields.json"), "JSON path should be I-140_fields.json"


if __name__ == "__main__":
    test_log_file_path()
    test_data_paths()
