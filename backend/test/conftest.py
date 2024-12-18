import os
import sys
from io import StringIO
from logging import CRITICAL, DEBUG
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app as main_app  # noqa: E402
from src.logging.Logging import file, logger, stream  # noqa: E402


@pytest.fixture
def app():
    main_app.config["TESTING"] = True
    return main_app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    mock_db = MagicMock()
    with patch("src.db", mock_db):
        yield mock_db


@pytest.fixture
def mock_fill_form():
    """Fixture to mock the fill_form method of PDFManipulator."""
    with patch("src.controller.PDF.PDFManipulator.PDFManipulator.fill_form") as mock:
        yield mock


@pytest.fixture
def mock_save_pdf():
    """Fixture to mock the save_pdf method of PDFManipulator."""
    with patch("src.controller.PDF.PDFManipulator.PDFManipulator.save_pdf") as mock:
        yield mock


@pytest.fixture(autouse=True)
def configure_logging():
    """Fixture to configure logging during tests."""

    # Backup original stdout and stderr
    stdout_backup = sys.stdout
    stderr_backup = sys.stderr

    # Redirect stdout and stderr to capture pytest outputs
    sys.stdout = captured_stdout = StringIO()
    sys.stderr = captured_stderr = StringIO()

    # Set logger levels
    logger.setLevel(DEBUG)
    stream.setLevel(CRITICAL)
    file.setLevel(DEBUG)

    logger.debug("Starting test session")

    try:
        yield
    finally:
        logger.debug(captured_stdout.getvalue())
        logger.debug(captured_stderr.getvalue())
        logger.debug("Test session completed")

        # Restore original stdout and stderr
        sys.stdout = stdout_backup
        sys.stderr = stderr_backup
