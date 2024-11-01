import json

from src.logging.Logging import logger


class FieldDataLoader:
    """Abstract class responsible for loading field data."""

    def load_data(self, source):
        logger.error("Subclasses should implement this method.")
        raise NotImplementedError("Subclasses should implement this method.")

    def load_json_data(self, path):
        """Loads data from a JSON file and returns the content."""
        try:
            with open(path, "r") as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from file: {path}")

    def save_data(self, path, data):
        with open(path, "w") as outfile:
            json.dump(data, outfile, indent=4)
        logger.info(f"Updated data written to {path}")
