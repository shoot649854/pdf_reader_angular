import json

from src.controller.FieldDataLoader import FieldDataLoader
from src.logging.Logging import logger


class JSONFieldDataLoader(FieldDataLoader):
    """Loads field data from a JSON file."""

    def load_data(self, json_path):
        with open(json_path, "r") as json_file:
            fields_data = json.load(json_file)
        data_dict = {}
        for field in fields_data:
            field_name = field["field_name"]
            value = field.get("initial_value", "AAA")
            data_dict[field_name] = value
            logger.info(f"'{value}' is loaded from json object. ")
        logger.info("Data loading is complete from json object. ")
        return data_dict
