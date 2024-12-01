import json
import os
import sys

import fitz
from pypdf import PdfReader

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.config import FILE_PATH
from src.controller.PDF.PDFFormExtractor import PDFFormExtractor
from src.logging.Logging import logger


class PDFFormExtractor_V2(PDFFormExtractor):
    """Handles extraction of form fields and linking them with sections."""

    GRAY_TOLERANCE = 10

    def __init__(self, pdf_path, font_size_threshold=11):
        super().__init__(pdf_path)
        self.pdf_path = pdf_path
        self.font_size_threshold = font_size_threshold

    def get_fields_with_sections(self):
        """Extract form fields and link them with their sections."""
        fields_info = []
        with fitz.open(self.pdf_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                logger.info(f"Processing page {page_number}...")
                sections = self._extract_sections(page)
                # if sections:
                #     print(
                #         f"text: {sections[0]['text']} \nposition: {sections[0]['position']}"
                #     )
                form_fields = self._extract_form_fields(page_number)
                form_fields = self.sorting(form_fields, page.mediabox.width)
                # print(json.dumps(form_fields, indent=4))

                linked_fields = self._link_fields_to_sections(form_fields, sections, page.mediabox.width)
                # logger.debug(
                #     f"Current linked field: {json.dumps(linked_fields, indent=4)}"
                # )

                fields_info.extend(linked_fields)
        return fields_info

    @staticmethod
    def sorting(form_fields, page_width):
        """Sort form fields for left-to-right and top-to-bottom reading."""
        half_page = page_width / 2

        # Separate fields into left and right based on x-coordinate
        left_fields = [f for f in form_fields if f["rect"][0] <= half_page]
        right_fields = [f for f in form_fields if f["rect"][0] > half_page]

        # Sort fields by y-coordinate, then by x-coordinate
        left_fields.sort(key=lambda f: (f["rect"][1], f["rect"][0]), reverse=True)
        right_fields.sort(key=lambda f: (f["rect"][1], f["rect"][0]), reverse=True)
        return left_fields + right_fields

    def _extract_form_fields(self, page_number):
        """Extract form fields using PyPDF."""
        fields_info = []
        with open(self.pdf_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            page = pdf_reader.pages[page_number - 1]  # Page indexing starts at 0
            if "/Annots" not in page:
                return fields_info
            annotations = page["/Annots"]
            for annotation in annotations:
                field = annotation.get_object()
                if "/T" in field:  # Check if the field has a name
                    field_info = {
                        "field_name": str(field.get("/T")),
                        "field_type": str(field.get("/FT")),
                        "initial_value": (str(field.get("/V")) if field.get("/V") else ""),
                        "rect": field.get("/Rect"),  # Get field coordinates
                        "page_number": page_number,
                    }
                    fields_info.append(field_info)
        return fields_info
        # fields_info = []
        # with fitz.open(self.pdf_path) as doc:
        #     page = doc[page_number - 1]
        #     widgets = page.widgets()

        #     for widget in widgets:
        #         if widget.field_name:
        #             rect = widget.rect
        #             field_info = {
        #                 "field_name": widget.field_name,
        #                 "field_type": widget.field_type,
        #                 "initial_value": widget.field_value or "",
        #                 "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
        #                 "page_number": page_number,
        #             }
        #             fields_info.append(field_info)
        # return fields_info

    def _extract_sections(self, page):
        """Extract section headers based on font size and background color."""
        sections = []
        text_blocks = page.get_text("dict").get("blocks", [])
        drawing_blocks = self._extract_drawing_blocks(page)

        for block in text_blocks:
            if "lines" not in block:  # Skip blocks without lines
                continue

            # print(f"Position: {block['bbox']}, {block['lines'][0]['spans'][0]['text']}")
            block_rect = block.get("bbox")
            is_gray_background = self._is_within_gray_background(block_rect, drawing_blocks)

            section_text = ""
            section_position = block_rect

            for line in block["lines"]:
                for span in line["spans"]:
                    if is_gray_background and span["size"] > self.font_size_threshold:
                        section_text += span["text"] + " "

            if section_text.strip():
                sections.append(
                    {
                        "text": section_text.strip(),
                        "position": section_position,  # [x0, y0, x1, y1]
                    }
                )

        logger.info(f"Extracted {len(sections)} sections:\n\t" f"{'\n\t'.join([f'{section['text']}' for section in sections])}")
        return sections

    def _extract_drawing_blocks(self, page):
        """Extract drawing blocks from the page."""
        drawing_blocks = []
        for item in page.get_drawings():
            if item["type"] == "rect" or item["type"] == "fs":
                fill_color = item.get("color", None)
                if fill_color and self._is_gray_background(fill_color):
                    drawing_blocks.append(item["rect"])
        return drawing_blocks

    def _is_within_gray_background(self, block_rect, drawing_blocks):
        """Check if a given text block rectangle is within any gray drawing block."""
        for block in drawing_blocks:
            if self._rect_within(block_rect, block):
                return True
        return False

    @staticmethod
    def _rect_within(inner_rect, outer_rect):
        """Check if inner_rect is within outer_rect."""
        x0_inner, y0_inner, x1_inner, y1_inner = inner_rect
        x0_outer, y0_outer, x1_outer, y1_outer = outer_rect
        return x0_outer <= x0_inner and y0_outer <= y0_inner and x1_inner <= x1_outer and y1_inner <= y1_outer

    def _is_gray_background(self, color):
        """Check if a given color is a shade of gray."""
        if len(color) == 3:  # RGB color
            r, g, b = [int(c * 255) for c in color]  # PyMuPDF colors are in [0,1] range
            return abs(r - g) < self.GRAY_TOLERANCE and abs(g - b) < self.GRAY_TOLERANCE and abs(r - b) < self.GRAY_TOLERANCE
        return False

    def _link_fields_to_sections(self, fields, sections, page_width):
        """Link each form field to the closest section above it."""
        half_page = page_width / 2

        # Divide sections into left and right halves
        left_sections = []
        right_sections = []
        for section in sections:
            x0_section = section["position"][0]
            if x0_section <= half_page:
                left_sections.append(section)
            else:
                right_sections.append(section)

        # Sort sections in each half from top to bottom
        left_sections.sort(key=lambda s: s["position"][1])
        right_sections.sort(key=lambda s: s["position"][1])

        # Debug: Print sorted sections
        # print("Left Sections:", left_sections)
        # print("Right Sections:", right_sections)

        for field in fields:
            field_top = field["rect"][1]
            x0_field = field["rect"][0]
            linked_section = None

            # Field is in left half
            if x0_field <= half_page:
                for section in reversed(left_sections):
                    section_top = section["position"][1]
                    if section_top <= field_top:
                        linked_section = section["text"]
                        break
                    # else:
                    #     print(
                    #         "section['position'][1]': "
                    #         f"{section['position'][1]} {section['text']}\n"
                    #         f"field_top': {field_top} with {field['field_name']}"
                    #     )
                field["section"] = linked_section

            # Field is in right half
            elif x0_field > half_page:
                for section in reversed(right_sections):
                    section_top = section["position"][1]
                    if section_top <= field_top:
                        linked_section = section["text"]
                        break

                # If no section above in right half, check left half
                if linked_section is None:
                    for section in reversed(left_sections):
                        section_top = section["position"][1]
                        if section_top <= field_top:
                            linked_section = section["text"]
                            break
                field["section"] = linked_section

            # Assign the section or fallback value
            else:
                field["section"] = linked_section
        return fields

    @staticmethod
    def connect_sandwiched_sections(fields):
        """Connect sections for fields where the section is null (None),"""
        for i in range(1, len(fields) - 1):
            current_field = fields[i]
            previous_field = fields[i - 1]
            next_field = fields[i + 1]

            if (
                current_field["section"] is None
                and previous_field["section"] == next_field["section"]
                and previous_field["section"] is not None
            ):
                current_field["section"] = previous_field["section"]

        return fields

    @staticmethod
    def apply_previous_section(fields):
        """Replace null sections with the most recent non-null section."""
        previous_section = None

        for field in fields:
            if field["section"] is None:
                field["section"] = previous_section  # Use the last non-null section
            else:
                previous_section = field["section"]  # Update to the current section

        return fields


def transform_fields_to_sections(fields):
    """Group fields by their sections and transform the structure."""
    grouped_sections = {}

    for field in fields:
        section = field.get("section", "Unknown Section")
        if section not in grouped_sections:
            grouped_sections[section] = {
                "section": section,
                "description": "",
                "question": [],
            }
        # Add the field to the respective section
        grouped_sections[section]["question"].append(
            {
                "field_name": field["field_name"],
                "field_type": field["field_type"],
                "initial_value": field["initial_value"],
                "rect": field["rect"],
                "page_number": field["page_number"],
            }
        )

    # Convert grouped dictionary to a list for JSON serialization
    return list(grouped_sections.values())


if __name__ == "__main__":
    pdf_path = os.path.join(FILE_PATH, "I-140.pdf")
    extractor = PDFFormExtractor_V2(pdf_path)
    fields_with_sections = extractor.get_fields_with_sections()
    # fields_with_sections = extractor.connect_sandwiched_sections(fields_with_sections)
    fields_with_sections = extractor.apply_previous_section(fields_with_sections)
    fields_with_sections = transform_fields_to_sections(fields_with_sections)
    json_output = json.dumps(fields_with_sections, indent=4)

    # Print the JSON
    # print(json_output)

    # Optionally, save the JSON to a file
    with open(os.path.join(FILE_PATH, "fields_with_sections.json"), "w") as json_file:
        json_file.write(json_output)
