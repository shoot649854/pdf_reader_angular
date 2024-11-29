# backend/test/test_json_handler.py
import json
import os
import sys
from unittest.mock import mock_open, patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.controller.DataHandle.JSONHandler import JSONHandler


def test_json_handler_load_data_from_path():
    with patch("builtins.open", mock_open(read_data='{"key": "value"}')):
        handler = JSONHandler()
        data = handler.load_data_from_path("dummy_path.json")
        assert data == {"key": "value"}, "Should load JSON correctly"


def test_json_handler_save_data():
    with patch("builtins.open", mock_open()) as mock_file:
        handler = JSONHandler()
        handler.save_data("dummy_path.json", {"key": "value"})
        mock_file.assert_called_once_with("dummy_path.json", "w")
        written_data = "".join(
            call.args[0] for call in mock_file().write.call_args_list
        )
        expected_data = json.dumps({"key": "value"}, indent=4)
        assert (
            written_data == expected_data
        ), "Written data does not match expected JSON format"


if __name__ == "__main__":
    test_json_handler_load_data_from_path()
    test_json_handler_save_data()
