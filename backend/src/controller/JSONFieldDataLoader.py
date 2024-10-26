import json

from src.controller.FieldDataLoader import FieldDataLoader
from src.logging.Logging import logger


class JSONFieldDataLoader(FieldDataLoader):
    """Loads field data from a JSON file or a JSON object."""

    def load_data(self, json_path):
        """Loads field data from a JSON file path."""
        with open(json_path, "r") as json_file:
            fields_data = json.load(json_file)
        return self._process_fields(fields_data)

    def load_data_from_object(self, json_object):
        """Loads field data directly from a JSON object (a Python dictionary)."""
        return self._process_fields(json_object)

    def _process_fields(self, fields_data):
        """Processes the field data and returns a dictionary."""
        data_dict = {}
        for field in fields_data:
            field_name = field["field_name"]
            value = field.get("initial_value", "AAA")
            data_dict[field_name] = value
            logger.debug(f"'{value}' is loaded from json object.")
        logger.info("Data loading is complete from json object.")
        return data_dict
