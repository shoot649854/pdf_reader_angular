import io
import json
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.logging.Logging import logger

current_dir = os.path.dirname(__file__)  # backend/src/controller
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
DATA_PATH = os.path.join(project_root, "frontend", "src", "assets", "form_data.json")
PERSONAL_INFO = os.path.abspath(os.path.join(current_dir, "../data/personal_data.json"))


def prepopulate():
    try:
        # Check if PERSONAL_INFO exists and is readable
        if not os.path.isfile(PERSONAL_INFO):
            logger.error(f"File not found: {PERSONAL_INFO}")
            return None
        if not os.access(PERSONAL_INFO, os.R_OK):
            logger.error(f"File not readable: {PERSONAL_INFO}")
            return None
        if os.path.getsize(PERSONAL_INFO) == 0:
            logger.error(f"File is empty: {PERSONAL_INFO}")
            return None

        # Load JSON data from PERSONAL_INFO
        with open(PERSONAL_INFO, "r") as json_file:
            data = json.load(json_file)

            # Extract specific information if 'people' key exists
            if "people" in data and isinstance(data["people"], list) and data["people"]:
                person = data["people"][0]
                FamilyName = person.get("FamilyName", "")
                GivenName = person.get("GivenName", "")
                Age = person.get("Age", "")
                address = person.get("Address", {})
                Street = address.get("Street", "")
                City = address.get("City", "")
                State = address.get("State", "")
                ZipCode = address.get("ZipCode", "")

                logger.info(
                    "Return the extracted values as a dictionary for easier access"
                )
                return {
                    "FamilyName": FamilyName,
                    "GivenName": GivenName,
                    "Age": Age,
                    "Street": Street,
                    "City": City,
                    "State": State,
                    "ZipCode": ZipCode,
                }
            else:
                logger.error("JSON data is missing 'people' key or it is not a list")
                return None

    except io.UnsupportedOperation as e:
        logger.error(f"io.UnsupportedOperation: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
    return None


def prefill():
    # Retrieve personal information values from PERSONAL_INFO
    personal_info = prepopulate()
    if not personal_info:
        logger.error("Failed to retrieve data from PERSONAL_INFO")
        return

    try:
        # Load DATA_PATH JSON data
        with open(DATA_PATH, "r") as data_file:
            data = json.load(data_file)

        # Process each field entry in DATA_PATH data
        for field in data:
            # Modify fields based on the `field_name`
            if (
                field.get("field_name")
                == "form1[0].#subform[0].Pt1Line1a_FamilyName[0]"
            ):
                field["initial_value"] = personal_info["FamilyName"]
            elif (
                field.get("field_name") == "form1[0].#subform[0].Pt1Line1b_GivenName[0]"
            ):
                field["initial_value"] = personal_info["GivenName"]
            elif field.get("field_name") == "form1[0].#subform[0].Line6d_CityOrTown[0]":
                field["initial_value"] = personal_info["City"]
            elif field.get("field_name") == "form1[0].#subform[0].Line6i_Country[0]":
                field["initial_value"] = personal_info[
                    "State"
                ]  # Assuming this is where "State" goes
            elif field.get("field_name") == "form1[0].#subform[0].Line6g_PostalCode[0]":
                field["initial_value"] = personal_info["ZipCode"]

        # Write updated data back to DATA_PATH
        with open(DATA_PATH, "w") as json_file:
            json.dump(data, json_file, indent=4)

        logger.info(f"Successfully updated {DATA_PATH} with data from {PERSONAL_INFO}")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    prefill()
