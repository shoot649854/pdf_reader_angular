# from src.config import OUTPUT_PDF_PATH
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.DataHandle.JSONHandler import JSONHandler
from src.controller.PDF.PDFManipulator import PDFManipulator
from src.logging.Logging import logger


class PDFFormFiller:
    """Coordinates data loading and PDF manipulation."""

    def __init__(
        self,
        data_loader: JSONFieldLoader,
        pdf_manipulator: PDFManipulator,
        json_handler: JSONHandler,
    ):
        self.data_loader = data_loader
        self.pdf_manipulator = pdf_manipulator
        self.json_handler = json_handler

    def fill_form(self, data_source, output_pdf_path):
        data_dict = self.json_handler.load_data(data_source)
        self.pdf_manipulator.fill_form(data_dict)
        self.pdf_manipulator.save_pdf(output_pdf_path)
        logger.info(f"Successfully filled the form: {output_pdf_path}")

    def fill_form_from_object(self, json_object, output_pdf_path):
        """Fills the form using data from a JSON object."""
        data_dict = self.data_loader.load_data_from_object(json_object)
        self.pdf_manipulator.fill_form(data_dict)
        self.pdf_manipulator.save_pdf(output_pdf_path)
        logger.info(f"Successfully filled the form from object: {output_pdf_path}")

    def fill_form_from_object_to_buffer(self, json_object, pdf_buffer):
        """Fills the form using data from a JSON object and
        writes to an in-memory buffer."""
        data_dict = self.data_loader.load_data_from_object(json_object)
        self.pdf_manipulator.fill_form(data_dict)
        self.pdf_manipulator.save_pdf_to_buffer(pdf_buffer)
        logger.info("Successfully filled the form from object and wrote to buffer.")
