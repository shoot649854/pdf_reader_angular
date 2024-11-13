import json
import re

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

    def parse(self, ai_response):
        """Parses the AI response to extract descriptions as a list."""
        try:
            ai_response = self._clean_response(ai_response)
            response_data = json.loads(ai_response)
            return [item.get("description", "") for item in response_data]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return []

    def _clean_response(self, ai_response):
        """Cleans AI response string by removing code block formatting."""
        ai_response = ai_response.strip()
        if ai_response.startswith("```") and ai_response.endswith("```"):
            return re.sub(r"^```[a-zA-Z]*\n", "", ai_response).rstrip("```")
        elif ai_response.startswith("```") and ai_response.endswith("\n```"):
            return ai_response[3:-3].strip()
        return ai_response
