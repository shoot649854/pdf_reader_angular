import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FILE_PATH
from src.controller.DataHandle.JSONHandler import JSONHandler
from src.logging.Logging import logger


def check():
    json_handler = JSONHandler()

    # Load the correct titles and validate titles
    correct_data_path = os.path.join(FILE_PATH, "correct_value_140.json")
    fields_data_path = os.path.join(FILE_PATH, "fields_with_titles_description.json")

    # Load the data from the files
    correct_data = json_handler.load_data_from_path(correct_data_path)
    fields_data = json_handler.load_data_from_path(fields_data_path)

    # Convert correct_data to a dictionary with field_name as keys
    correct_titles_dict = {item["field_name"]: item["title"] for item in correct_data}

    # Track correct matches
    correct_matches = 0
    total_fields = len(fields_data)

    # Iterate over the fields and compare titles
    for field in fields_data:
        field_name = field["field_name"]
        title = field["title"]

        # Check if the title matches the correct one
        if field_name in correct_titles_dict.keys():
            correct_title = correct_titles_dict[field_name]
            if title == correct_title:
                correct_matches += 1

    # Calculate the percentage of correct matches
    if total_fields > 0:
        match_percentage = (correct_matches / total_fields) * 100
        logger.info(f"Percentage of Correct Titles: {match_percentage:.2f}%")
    else:
        logger.warning("No fields to compare.")


if __name__ == "__main__":
    check()
