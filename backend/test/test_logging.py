import os
import sys
from unittest.mock import patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.logging.Logging import logger


def test_logger_file_creation():
    log_file_path = logger.handlers[1].baseFilename
    assert os.path.exists(log_file_path), "Log file should be created"


def test_logger_error_level():
    with patch("src.logging.Logging.logger.error") as mock_error:
        logger.error("Test error")
        mock_error.assert_called_once_with("Test error")


if __name__ == "__main__":
    test_logger_file_creation()
    test_logger_error_level()
