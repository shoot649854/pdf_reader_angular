import argparse
import os
import sys

from pypdf.errors import DependencyError

if __name__ == "__main__":
    sys.path.append(os.path.abspath("../backend"))

from src.controller.DataHandle.JSONHandler import JSONHandler
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor
from src.logging.Logging import logger


class PDFDataCLI:
    """Handles command-line interface for PDF form extraction."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Extract form fields from PDF files and save as JSON."
        )
        self.parser.add_argument(
            "pdf_paths", nargs="+", help="Paths to one or more PDF files."
        )
        self.parser.add_argument(
            "-o",
            "--output",
            help="Path to the output JSON file (default: {pdf_name}.data.json)",
        )

    def parse_args(self):
        """Parse and return command-line arguments."""
        return self.parser.parse_args()

    def run(self):
        """Run the CLI tool."""
        args = self.parse_args()

        for pdf_path in args.pdf_paths:
            extractor = PDFFormExtractor(pdf_path)

            if args.output:
                output_path = f"./data/{args.output}"

            else:
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_path = f"./data/{pdf_name}.data.json"

            try:
                fields = extractor.get_fields()
                json_handler = JSONHandler()
                json_handler.save_data(output_path, fields)
                logger.debug(
                    f"Data extracted and written to {output_path} for {pdf_path}"
                )
            except DependencyError as e:
                logger.error("Dependency Error: %s", e)
            except Exception as e:
                logger.error("An unexpected error occurred with %s: %s", pdf_path, e)


if __name__ == "__main__":
    PDFDataCLI().run()
