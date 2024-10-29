import argparse

from src.controller.JSONWriter import JSONWriter
from src.controller.PDFFormExtractor import PDFFormExtractor


class PDFDataCLI:
    """Handles command-line interface for PDF form extraction."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Extract form fields from a PDF and save as JSON."
        )
        self.parser.add_argument("pdf_path", help="Path to the PDF file.")
        self.parser.add_argument(
            "-o",
            "--output",
            default="output.json",
            help="Path to the output JSON file (default: output.json)",
        )

    def parse_args(self):
        """Parse and return command-line arguments."""
        return self.parser.parse_args()

    def run(self):
        """Run the CLI tool."""
        args = self.parse_args()
        extractor = PDFFormExtractor(args.pdf_path)
        fields = extractor.get_fields()
        writer = JSONWriter(args.output)
        writer.write(fields)


if __name__ == "__main__":
    PDFDataCLI().run()
