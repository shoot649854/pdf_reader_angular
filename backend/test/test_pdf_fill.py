import os
import sys
from unittest.mock import Mock, patch

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob

from src.config import FILE_PATH
from src.controller.PDF.PDFFill import PDFFill


def test_pdf_fill_save_pdf():
    mock_writer = Mock()
    pdf_paths = glob.glob(os.path.join(FILE_PATH, "*.pdf"))
    with patch("pypdf.PdfWriter", return_value=mock_writer):
        for pdf_path in pdf_paths:
            pdf_fill = PDFFill(pdf_path)
            pdf_fill.save_pdf(".log/test_output.pdf")

        assert mock_writer.write.call_count == len(pdf_paths), (
            f"Expected write to be called {len(pdf_paths)} times, " f"but it was called {mock_writer.write.call_count} times."
        )


if __name__ == "__main__":
    test_pdf_fill_save_pdf()
