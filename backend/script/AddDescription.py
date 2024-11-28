import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import FILE_PATH
from src.controller.DataHandle.JSONHandler import JSONHandler
from src.controller.PDF.PDFManipulator import PDFManipulator

from backend.script.FieldHandle import FieldProcessor
from backend.src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader

if __name__ == "__main__":
    name = "i-907.data"
    path = os.path.join(FILE_PATH, name + ".json")
    output_filename = os.path.join(FILE_PATH, f"{name}.updated.data.json")

    data_loader = JSONFieldLoader()
    pdf_manipulator = PDFManipulator(path)
    json_handler = JSONHandler()

    processor = FieldProcessor(data_loader, pdf_manipulator, json_handler)
    processor.generating_descriptions(path, output_filename)
