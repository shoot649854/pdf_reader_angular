import logging
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


@pytest.fixture
def mock_db():
    mock_db = MagicMock()
    with patch("src.db", mock_db):
        yield mock_db


@pytest.fixture(autouse=True)
def suppress_logs():
    """Fixture to suppress logging during tests."""
    # Disable all logging below CRITICAL level
    logging.disable(logging.CRITICAL)
    yield
    # Re-enable logging after the test
    logging.disable(logging.NOTSET)
