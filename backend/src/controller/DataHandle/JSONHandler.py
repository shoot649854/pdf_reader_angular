import json
from typing import Dict

from src.logging.Logging import logger


class JSONHandler:
    def __init__(self) -> None:
        pass

    def load_data(self, source):
        logger.error("Subclasses should implement this method.")
        raise NotImplementedError("Subclasses should implement this method.")

    def load_data_from_path(self, path_json: str) -> Dict:
        """Loads field data from a JSON file path."""
        try:
            with open(path_json, "r") as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {path_json}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from file: {path_json}")

    def get_num_item(self, json_data):
        data = json.loads(json_data)
        num = 0
        for _ in data:
            num += 1
        return num

    def save_data(self, path_save: str, json_data):
        try:
            with open(path_save, "w") as outfile:
                json.dump(json_data, outfile, indent=4)
            logger.info(f"Updated data written to {path_save}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from file: {path_save}")
