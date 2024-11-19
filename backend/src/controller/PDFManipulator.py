import pypdf
from src.logging.Logging import logger


class PDFManipulator:
    """Handles PDF reading, form filling, and writing."""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        logger.info(f"Initializing PDFManipulator with PDF path: {pdf_path}")
        self.pdf_reader = pypdf.PdfReader(pdf_path)
        self.pdf_writer = pypdf.PdfWriter()

    def fill_form(self, data_dict):
        logger.info(
            "Starting to fill form fields based on the provided data dictionary."
        )
        for page_num, page in enumerate(self.pdf_reader.pages, start=1):
            if "/Annots" in page:
                logger.debug(f"Page {page_num}: Found annotations for form fields.")
                annotations = page["/Annots"]
                for annotation in annotations:
                    field = annotation.get_object()
                    if "/T" in field:
                        field_name = self._get_field_name(field)
                        field_type = field.get("/FT")

                        logger.debug(
                            f"Processing field '{field_name}' of type '{field_type}'."
                        )
                        # logger.debug(
                        #     f"Available fields in data_dict: {data_dict.keys()}"
                        # )
                        if field_name in data_dict:
                            value = data_dict[field_name]
                            logger.debug(
                                f"Updating field '{field_name}' with value '{value}'."
                            )
                            self._update_field(field, field_type, value)
            else:
                logger.debug(f"Page {page_num}: No annotations found.")
            self.pdf_writer.add_page(page)
        logger.info("Completed form filling.")

    def save_pdf(self, output_pdf_path):
        logger.info(f"Saving filled PDF to: {output_pdf_path}")
        with open(output_pdf_path, "wb") as output_file:
            self.pdf_writer.write(output_file)
        logger.info(f"PDF saved successfully to {output_pdf_path}.")

    def save_pdf_to_buffer(self, pdf_buffer):
        """Save the filled PDF to an in-memory bytes buffer."""
        self.pdf_writer.write(pdf_buffer)
        logger.info("PDF saved successfully to in-memory buffer.")

    def _get_field_name(self, field):
        field_name_obj = field["/T"]
        field_name = (
            field_name_obj
            if isinstance(field_name_obj, str)
            else field_name_obj.decode("utf-8", errors="ignore")
        )
        logger.debug(f"Extracted field name: {field_name}")
        return field_name

    def _update_field(self, field, field_type, value):
        if field_type == "/Tx":  # Text field
            field.update(
                {
                    pypdf.generic.NameObject("/V"): pypdf.generic.create_string_object(
                        value
                    )
                }
            )
            logger.debug(f"Updated text field with value '{value}'.")
        elif field_type == "/Btn":  # Checkbox or radio button
            logger.debug(f"Updating button field with value '{value}'.")
            self._update_button_field(field, value)
        elif field_type == "/Ch":  # Choice field
            field.update(
                {
                    pypdf.generic.NameObject("/V"): pypdf.generic.create_string_object(
                        value
                    ),
                    pypdf.generic.NameObject("/DV"): pypdf.generic.create_string_object(
                        value
                    ),
                }
            )
            logger.debug(f"Updated choice field with value '{value}'.")
        else:
            # Other field types
            field.update(
                {
                    pypdf.generic.NameObject("/V"): pypdf.generic.create_string_object(
                        value
                    )
                }
            )
            logger.debug(f"Updated other field type with value '{value}'.")

    def _update_button_field(self, field, value):
        if isinstance(value, bool):
            value = "yes" if value else "no"

        elif isinstance(value, str):
            value = value.lower()

        if value.lower() == "yes":
            logger.debug("Checkbox/radio button checked (value: Yes).")
            on_value = self._get_on_value(field)
            field.update(
                {
                    pypdf.generic.NameObject("/V"): pypdf.generic.NameObject(on_value),
                    pypdf.generic.NameObject("/AS"): pypdf.generic.NameObject(on_value),
                }
            )
        else:
            logger.debug("Checkbox/radio button unchecked (value: Off).")
            field.update(
                {
                    pypdf.generic.NameObject("/V"): pypdf.generic.NameObject("/Off"),
                    pypdf.generic.NameObject("/AS"): pypdf.generic.NameObject("/Off"),
                }
            )

    def _get_on_value(self, field):
        if "/AP" in field:
            appearances = field["/AP"]
            if "/N" in appearances:
                normal_appearances = appearances["/N"]
                possible_values = list(normal_appearances.keys())
                on_values = [val for val in possible_values if val != "/Off"]
                logger.debug(f"Available 'on' values for button field: {on_values}")
                return on_values[0] if on_values else "/Yes"
            else:
                return "/Yes"
        else:
            return "/Yes"
