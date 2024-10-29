import json

from src.logging.Logging import logger


class JSONWriter:
    """Handles writing data to JSON files."""

    def __init__(self, output_path):
        self.output_path = output_path

    def write(self, data):
        """Write data to JSON file."""
        with open(self.output_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        logger.info(f"Data written to {self.output_path}")
