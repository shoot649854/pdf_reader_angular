import math
import re

import fitz  # PyMuPDF
import pypdf
from src.logging.Logging import logger


class PDFFormExtractor:
    """Handles extraction of form fields and their associated questions from PDF files."""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_reader = pypdf.PdfReader(pdf_path)
        self.doc = fitz.open(pdf_path)

    def get_fields_with_questions(self):
        """Extract form fields along with their associated questions from the PDF."""
        fields_info = []

        for page_number in range(len(self.pdf_reader.pages)):
            page = self.pdf_reader.pages[page_number]
            form_fields = self._extract_fields_from_page(page, page_number + 1)
            text_blocks = self._extract_text_blocks(page_number + 1)

            # Build a mapping from numbering to label text
            label_mapping = self._build_label_mapping(text_blocks)

            # Build a keyword-based label mapping
            keyword_label_mapping = self._build_keyword_label_mapping(text_blocks)

            for field in form_fields:
                # Extract numbering from the field name
                field_numbering = self._extract_field_numbering(field["field_name"])

                if field_numbering and field_numbering in label_mapping:
                    # Directly map using numbering
                    question = label_mapping[field_numbering]
                else:
                    # Attempt to map using keyword-based association
                    field_identifier = self._get_field_identifier(field["field_name"])
                    question = keyword_label_mapping.get(field_identifier, "")

                    if not question:
                        # Fallback to spatial association
                        question = self._find_nearest_question(
                            field["rect"], text_blocks
                        )

                field["question"] = question
                fields_info.append(field)

        logger.info("Successfully extracted form fields with associated questions.")
        return fields_info

    def _extract_fields_from_page(self, page, page_number):
        """Extract form fields from a single page, including their positions."""
        fields_info = []
        if "/Annots" not in page:
            return fields_info

        annotations = page["/Annots"]
        for annotation in annotations:
            field = annotation.get_object()
            if "/T" in field:
                field_info = self._get_field_info(field, page_number)
                fields_info.append(field_info)
        logger.info(f"Successfully extracted form fields from page {page_number}.")
        return fields_info

    def _get_field_info(self, field, page_number):
        """Construct and return field information dictionary, including position."""
        field_name = field.get("/T")
        field_type = field.get("/FT")
        initial_value = field.get("/V")
        rect = field.get("/Rect")

        # Convert PDF coordinates to a dictionary
        if rect and isinstance(rect, pypdf.generic.ArrayObject):
            rect = [float(coord) for coord in rect]
            # PDF coordinates: lower-left origin. PyMuPDF uses the same.
            rect = {"x0": rect[0], "y0": rect[1], "x1": rect[2], "y1": rect[3]}
        else:
            rect = None

        field_info = {
            "field_name": str(field_name),
            "field_type": str(field_type),
            "initial_value": str(initial_value) if initial_value else "",
            "page_number": page_number,
            "rect": rect,  # Now a dictionary instead of a Rect object
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
            logger.warning("No options available for choice field.")
            return []

        return [
            (
                str(option[0])
                if isinstance(option, pypdf.generic.ArrayObject)
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

    def _extract_text_blocks(self, page_number):
        """Extract text blocks with their bounding boxes from a page using PyMuPDF."""
        page = self.doc.load_page(page_number - 1)  # 0-based index
        text_blocks = page.get_text(
            "blocks"
        )  # Returns list of tuples: (x0, y0, x1, y1, "text", block_no, ...)

        # Convert to a list of dicts for easier handling
        blocks = [
            {
                "rect": {
                    "x0": block[0],
                    "y0": block[1],
                    "x1": block[2],
                    "y1": block[3],
                },
                "text": block[4].strip(),
            }
            for block in text_blocks
            if block[4].strip()  # Ignore empty text
        ]
        return blocks

    def _build_label_mapping(self, text_blocks):
        """
        Build a mapping from numbering to label text.

        Parameters:
            text_blocks (list): List of text blocks with their rectangles and text.

        Returns:
            dict: Mapping of numbering (e.g., "1.a") to label text.
        """
        label_mapping = {}
        # Regex to match labels starting with numbering like "1.a. ", "2. ", etc.
        numbering_pattern = re.compile(
            r"^(\d+(\.\w+)?)\.\s+(.+)"
        )  # Matches "1.a. Label Text"

        for block in text_blocks:
            text = block["text"]
            match = numbering_pattern.match(text)
            if match:
                numbering = match.group(1)  # e.g., "1.a"
                label_text = match.group(3)  # e.g., "Family Name (Last Name)"
                label_mapping[numbering] = self._clean_label_text(label_text)

        logger.debug(f"Label mapping for the page: {label_mapping}")
        return label_mapping

    def _build_keyword_label_mapping(self, text_blocks):
        """
        Build a mapping from keywords to label text.

        Parameters:
            text_blocks (list): List of text blocks with their rectangles and text.

        Returns:
            dict: Mapping of keywords to label text.
        """
        keyword_mapping = {}
        # Define keywords and their corresponding field identifiers
        keywords = {
            "Attorney": "Attorney",
            "Accredited Representative": "Attorney",
            "Attorney or Accredited Representative": "Attorney",
            "Certification": "Certification",
            "Remarks": "Remarks",
            "USCIS Online Account Number": "USCISOnlineAccountNumber",
            "Tax Number": "TaxNumber",
            "Social Security Number": "SSN",
            "Representative": "Representative",
            "In Care Of Name": "InCareOfName",
            "Street Number and Name": "StreetNumberName",
            "Apt/Ste/Flr Number": "AptSteFlrNumber",
            "City or Town": "CityOrTown",
            "Postal Code": "PostalCode",
            "Country": "Country",
            # Add more keywords as needed
        }

        for block in text_blocks:
            text = block["text"]
            for keyword, identifier in keywords.items():
                if keyword.lower() in text.lower():
                    # If multiple labels match the same identifier, prefer the first one
                    if identifier not in keyword_mapping:
                        keyword_mapping[identifier] = self._clean_label_text(text)
                    break  # Assume one keyword per label

        logger.debug(f"Keyword label mapping for the page: {keyword_mapping}")
        return keyword_mapping

    def _extract_field_numbering(self, field_name):
        """
        Extract numbering from the field name.

        Parameters:
            field_name (str): The name of the form field.

        Returns:
            str or None: The extracted numbering (e.g., "1.a") or None if not found.
        """
        # Extract patterns like "Line1a_", "Line2_", "Line6a_", "Pt2Line2_", etc.
        numbering_pattern = re.compile(r"(?:Pt\d+)?Line(\d+)([a-zA-Z]?)_")
        match = numbering_pattern.search(field_name)
        if match:
            number = match.group(1)  # e.g., "1"
            sub = match.group(2).lower()  # e.g., "a"
            if sub:
                return f"{number}.{sub}"
            else:
                return number
        else:
            return None

    def _find_nearest_question(
        self,
        field_rect,
        text_blocks,
        max_vertical_distance=100,
        max_horizontal_distance=150,
    ):
        """
        Find the nearest text block relative to the form field within specified distances.
        Prioritizes text to the left, then above, then to the right, and optionally below.

        Parameters:
            field_rect (dict): Dictionary containing 'x0', 'y0', 'x1', 'y1' of the field.
            text_blocks (list): List of text blocks with their rectangles and text.
            max_vertical_distance (float): Maximum vertical distance to search for above/below.
            max_horizontal_distance (float): Maximum horizontal distance to search for left/right.

        Returns:
            str: The nearest question text, or an empty string if none found.
        """
        if not field_rect:
            return ""

        field_center_x = (field_rect["x0"] + field_rect["x1"]) / 2
        field_center_y = (field_rect["y0"] + field_rect["y1"]) / 2

        nearest_text = ""
        min_metric = (float("inf"), float("inf"))  # (priority, distance)

        # Define regex to include only relevant labels
        inclusion_pattern = re.compile(
            r"^\d+(\.\w+)?\.\s+"
        )  # Matches "1. ", "1.a. ", etc.

        # Define regex to exclude irrelevant symbols and short texts
        exclusion_pattern = re.compile(
            r"^[\W_]{1,}$"
        )  # Matches strings consisting only of non-alphanumerics

        for block in text_blocks:
            text = block["text"]

            # Inclusion Filter: Only consider text blocks that start with label patterns
            if not inclusion_pattern.match(text):
                continue

            # Exclusion Filter: Skip if text is only symbols or too short
            if exclusion_pattern.match(text) or len(text) < 3:
                continue

            text_rect = block["rect"]
            text_center_x = (text_rect["x0"] + text_rect["x1"]) / 2
            text_center_y = (text_rect["y0"] + text_rect["y1"]) / 2

            # Calculate Euclidean distance
            delta_x = text_center_x - field_center_x
            delta_y = text_center_y - field_center_y
            distance = math.sqrt(delta_x**2 + delta_y**2)

            # Determine the relative position
            direction = None
            if delta_x < 0 and abs(delta_x) <= max_horizontal_distance:
                # Text is to the left
                direction = "left"
            elif delta_y < 0 and abs(delta_y) <= max_vertical_distance:
                # Text is above
                direction = "above"
            elif delta_x > 0 and abs(delta_x) <= max_horizontal_distance:
                # Text is to the right
                direction = "right"
            elif delta_y > 0 and abs(delta_y) <= max_vertical_distance:
                # Text is below (optional)
                direction = "below"

            if direction:
                # Assign priority based on direction
                priority = {"left": 1, "above": 2, "right": 3, "below": 4}.get(
                    direction, 5
                )

                combined_metric = (priority, distance)

                if combined_metric < min_metric:
                    min_metric = combined_metric
                    nearest_text = self._clean_label_text(text)

        # Log the association for debugging
        logger.debug(
            f"Field at {field_rect} associated with question: '{nearest_text}'"
        )

        return nearest_text

    def _clean_label_text(self, text):
        """
        Clean the label text by removing numbering and unnecessary characters.

        Parameters:
            text (str): The raw text extracted from the PDF.

        Returns:
            str: The cleaned label text.
        """
        # Remove leading numbering (e.g., "1.a. ")
        cleaned_text = re.sub(r"^\d+(\.\w+)?\.\s+", "", text)
        # Replace multiple spaces and newlines with a single space
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)
        # Remove trailing punctuation if necessary
        cleaned_text = re.sub(r"[\.\-\:]+$", "", cleaned_text)
        return cleaned_text.strip()

    def _get_field_identifier(self, field_name):
        """
        Identify the field category based on its name.

        Parameters:
            field_name (str): The name of the form field.

        Returns:
            str or None: The identifier for keyword mapping.
        """
        # Define a mapping from field name patterns to identifiers
        identifier_mapping = {
            "attyStateBarNumber": "Attorney",
            "attyUSCISOnlineNum": "USCISOnlineAccountNumber",
            "Line6c_AptSteFlrNumber": "AptSteFlrNumber",
            "Line6d_CityOrTown": "CityOrTown",
            "Line6g_PostalCode": "PostalCode",
            "Line6i_Country": "Country",
            "Pt2Line2_USCISOnlineActNumber": "USCISOnlineAccountNumber",
            "Pt1Line3_TaxNumber": "TaxNumber",
            "Line4_SSN": "SSN",
            # Add more mappings as needed
        }

        for identifier, patterns in identifier_mapping.items():
            if identifier.lower() in field_name.lower():
                return identifier
        return None

    def visualize_associations(self, fields_info, output_pdf_path="annotated_form.pdf"):
        """Visualize form fields and their associated questions on the PDF."""
        for field in fields_info:
            page_number = field["page_number"] - 1
            page = self.doc.load_page(page_number)
            rect = field["rect"]
            if rect:
                # Draw rectangle around the field (red color)
                page.draw_rect(
                    fitz.Rect(rect["x0"], rect["y0"], rect["x1"], rect["y1"]),
                    color=(1, 0, 0),
                    width=1,
                )
                # Insert text label above the field (blue color)
                page.insert_text(
                    (rect["x0"], rect["y0"] - 10),
                    field.get("question", "N/A"),
                    fontsize=8,
                    color=(0, 0, 1),
                )
        # Save the annotated PDF
        self.doc.save(output_pdf_path)
        logger.info(f"Annotated PDF saved as '{output_pdf_path}'.")
