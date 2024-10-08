from src.controller.FieldDataLoader import FieldDataLoader
from src.controller.PDFFill import PDFFill
from src.controller.PDFManipulator import PDFManipulator
from src.logging.Logging import logger


class PDFFormFiller:
    """Coordinates data loading and PDF manipulation."""

    def __init__(self, data_loader: FieldDataLoader, pdf_manipulator: PDFManipulator):
        self.data_loader = data_loader
        self.pdf_manipulator = pdf_manipulator

    def fill_form(self, data_source, output_pdf_path):
        data_dict = self.data_loader.load_data(data_source)
        self.pdf_manipulator.fill_form(data_dict)
        self.pdf_manipulator.save_pdf(output_pdf_path)
        logger.info(f"Successfully filled the form: {output_pdf_path}")
