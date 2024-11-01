# import json
import os

# import re
import sys

# from abc import ABC, abstractmethod

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import FILE_PATH
from src.controller.FieldDataLoader import FieldDataLoader
from src.controller.FieldHandle import FieldDescriptionGenerator, FieldProcessor
from src.controller.GenerateResponse import GenerateResponse
from src.controller.JSONFieldData import JSONFieldDataLoader

# from src.logging.Logging import logger


# Entry point for running the script
if __name__ == "__main__":
    name = "i-907.data"
    path = os.path.join(FILE_PATH, name + ".json")
    output_filename = os.path.join(FILE_PATH, f"{name}.updated.data.json")

    data_loader = FieldDataLoader()
    response_generator = FieldDescriptionGenerator(GenerateResponse())
    response_parser = JSONFieldDataLoader()

    processor = FieldProcessor(data_loader, response_generator, response_parser)
    processor.process_fields(path, output_filename)
