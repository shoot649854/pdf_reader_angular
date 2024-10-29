import PyPDF2
from src.logging.Logging import logger


class PDFFormExtractor:
    """Handles extraction of form fields from PDF files."""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def get_fields(self):
        """Extract form fields and their details from the PDF."""
        fields_info = []

        with open(self.pdf_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_number, page in enumerate(pdf_reader.pages, start=1):
                fields_info.extend(self._extract_fields_from_page(page, page_number))
        logger.info("Successfully extract form fields. ")
        return fields_info

    def _extract_fields_from_page(self, page, page_number):
        """Extract form fields from a single page."""
        fields_info = []
        if "/Annots" not in page:
            return fields_info

        annotations = page["/Annots"]
        for annotation in annotations:
            field = annotation.get_object()
            if "/T" in field:
                fields_info.append(self._get_field_info(field, page_number))
        logger.info("Successfully extract form fields from a single page.")
        return fields_info

    def _get_field_info(self, field, page_number):
        """Construct and return field information dictionary."""
        field_name = field.get("/T")
        field_type = field.get("/FT")
        initial_value = field.get("/V")

        field_info = {
            "field_name": str(field_name),
            "field_type": str(field_type),
            "initial_value": str(initial_value) if initial_value else "",
            "page_number": page_number,
        }

        if field_type == "/Ch":
            field_info["options"] = self._get_choice_options(field)
        elif field_type == "/Btn":
            field_info["possible_values"] = self._get_button_values(field)

        return field_info

    def _get_choice_options(self, field):
        """Retrieve options for choice fields."""
        options = field.get("/Opt")
        if not options:
            logger.warning("There was no option available. ")
            return []

        return [
            (
                str(option[0])
                if isinstance(option, PyPDF2.generic.ArrayObject)
                else str(option)
            )
            for option in options
        ]

    def _get_button_values(self, field):
        """Retrieve possible values for button fields (checkbox/radio)."""
        if "/AP" in field:
            appearances = field["/AP"]
            if "/N" in appearances:
                return [str(key) for key in appearances["/N"].keys()]
        return []
