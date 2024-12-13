import json
import re
from typing import List

import fitz
from pypdf import PdfReader, generic
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.controller.VertexAI.GenerateResponse import GenerateResponse
from src.logging.Logging import logger


class PDFFormExtractor:
    """Handles extraction of form fields from PDF files."""

    GRAY_TOLERANCE = 10

    def __init__(
        self,
        pdf_path,
        generate_res: GenerateResponse,
        response_parser: JSONFieldLoader,
        font_size_threshold=11,
    ):
        self.pdf_path = pdf_path
        self.generate_res = generate_res
        self.response_parser = response_parser
        self.font_size_threshold = font_size_threshold

    def get_fields(self) -> List[str]:
        """Extract form fields and link them with their titles."""
        fields_info = []
        with fitz.open(self.pdf_path) as doc:
            for page_number, _ in enumerate(doc, start=1):
                logger.info(f"Processing page {page_number}...")
                form_fields = self._extract_form_fields(page_number)
                fields_info.extend(form_fields)
        return fields_info

    def get_fields_with_titles(self) -> List[str]:
        """Extract form fields and link them with their titles."""
        fields_info = []
        with fitz.open(self.pdf_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                logger.info(f"Processing page {page_number}...")
                titles = self._extract_titles(page)
                form_fields = self._extract_form_fields(page_number)
                form_fields = self.sorting(form_fields, page.mediabox.width)
                form_fields = self._link_fields_to_titles(form_fields, titles, page.mediabox.width)
                fields_info.extend(form_fields)
        return fields_info

    def _extract_titles(self, page):
        """Extract title headers based on font size and background color."""
        titles = []
        text_blocks = page.get_text("dict").get("blocks", [])
        # drawing_blocks = self._extract_drawing_blocks(page)

        for block in text_blocks:
            if "lines" not in block:
                continue

            block_rect = block.get("bbox")
            title_text = ""
            title_position = block_rect

            for line in block["lines"]:
                for span in line["spans"]:
                    if span["size"] > self.font_size_threshold:
                        title_text += span["text"] + " "

            if title_text.strip():
                titles.append(
                    {
                        "text": title_text.strip(),
                        "position": [
                            title_position[0],
                            title_position[1],
                            title_position[2],
                            title_position[3],
                        ],
                    }
                )

        logger.info(
            f"Extracted {len(titles)} titles:\n\t"
            f"{'\n\t'.join([f'{title['text']}\n{title['position']}' for title in titles])}"
        )
        return titles

    def _extract_drawing_blocks(self, page):
        """Extract drawing blocks from the page."""
        drawing_blocks = []
        for item in page.get_drawings():
            if item["type"] == "rect" or item["type"] == "fs":
                fill_color = item.get("color", None)
                if fill_color and self._is_gray_background(fill_color):
                    drawing_blocks.append(item["rect"])
        return drawing_blocks

    def _is_gray_background(self, color):
        """Check if a given color is a shade of gray."""
        if len(color) == 3:
            r, g, b = [int(c * 255) for c in color]
            return abs(r - g) < self.GRAY_TOLERANCE and abs(g - b) < self.GRAY_TOLERANCE and abs(r - b) < self.GRAY_TOLERANCE
        return False

    def _extract_form_fields(self, page_number):
        """Extract form fields using PyPDF, not fitz since I/O is PyPDF."""
        fields_info = []
        with open(self.pdf_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            page = pdf_reader.pages[page_number - 1]
            if "/Annots" not in page:
                return fields_info
            annotations = page["/Annots"]

            for annotation in annotations:
                field = annotation.get_object()
                struct_parent = field.get("/StructParent")
                if "/T" in field:
                    field_info = {
                        "field_name": str(field.get("/T")),
                        "field_type": str(field.get("/FT")),
                        "struct_parent": struct_parent,
                        "initial_value": (str(field.get("/V")) if field.get("/V") else ""),
                        "tool_tip": str(field.get("/TU")) if field.get("/TU") else None,
                        "rect": field.get("/Rect"),
                        "page_number": page_number,
                    }
                    if str(field.get("/FT")) == "/Ch":
                        field_info["options"] = self._get_choice_options(field)
                    elif str(field.get("/FT")) == "/Btn":
                        field_info["possible_values"] = self._get_button_values(field)
                    fields_info.append(field_info)
        return fields_info

    def _get_choice_options(self, field):
        """Retrieve options for choice fields."""
        options = field.get("/Opt")
        if not options:
            logger.warning("There was no option available. ")
            return []
        return [(str(option[0]) if isinstance(option, generic.ArrayObject) else str(option)) for option in options]

    def _get_button_values(self, field):
        """Retrieve possible values for button fields (checkbox/radio)."""
        if "/AP" in field:
            appearances = field["/AP"]
            if "/N" in appearances:
                return [str(key) for key in appearances["/N"].keys()]
        return []

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

    def _link_fields_to_titles(self, fields, titles, page_width):
        """Link each form field to the most logical title."""
        title_sections = []
        for title in titles:
            section = self._extract_section_identifier(title["text"])
            title_sections.append(
                {
                    "text": title["text"],
                    "position": title["position"],
                    "section": section,
                }
            )

        for field in fields:
            # Extract section identifier from the field's tooltip
            tooltip = field.get("tool_tip", "")
            field_section = self._extract_section_identifier(tooltip)

            # Attempt to match field to title based on section identifier
            linked_title = None
            if field_section:
                for title in title_sections:
                    if title["section"] == field_section:
                        linked_title = title["text"]
                        break

            # If no logical match found, fallback to spatial proximity
            if not linked_title:
                linked_title = self._find_closest_title(field, title_sections, page_width)

            field["title"] = linked_title

        return fields

    def _extract_section_identifier(self, text):
        """Extracts section identifier (e.g., 'Part 2') from a given text."""
        match = re.search(r"(Part\s*\d+)", text, re.IGNORECASE)
        return match.group(1) if match else None

    def _find_closest_title(self, field, titles, page_width):
        """Finds the closest title above the field based on spatial proximity."""
        half_page = page_width / 2
        field_bottom = field["rect"][1]
        field_x = (field["rect"][0] + field["rect"][2]) / 2
        linked_title = None

        # Determine if field is on left or right half
        if field_x < half_page:
            relevant_titles = [t for t in titles if (t["position"][0] + t["position"][2]) / 2 <= half_page]
        else:
            relevant_titles = [t for t in titles if (t["position"][0] + t["position"][2]) / 2 > half_page]

        # Sort titles from bottom to top (reverse order)
        relevant_titles.sort(key=lambda s: s["position"][1], reverse=True)

        # Find the closest title above the field
        for title in relevant_titles:
            title_bottom = title["position"][1]
            if title_bottom <= field_bottom:
                linked_title = title["text"]
                break

        return linked_title

    @staticmethod
    def apply_previous_title(fields):
        """Replace null titles with the most recent non-null title."""
        previous_title = None

        for field in fields:
            if field["title"] is None:
                field["title"] = previous_title
            else:
                previous_title = field["title"]

        return fields

    def generating_descriptions(self, json_data) -> List[str]:
        """Service for processing fields and generating descriptions"""
        fields_by_page = self._group_fields_by_page(json_data)

        for page_number, fields in fields_by_page.items():
            logger.info(f"Page: {page_number} has started to process.")
            self._initialize_field_descriptions(fields)
            ai_response = None
            ai_response = self._get_ai_response(fields)

            if not ai_response:
                logger.warning(f"No response for page {page_number}. Skipping.")
                continue

            descriptions = self.response_parser.parse(ai_response)
            self._assign_descriptions(fields, descriptions, page_number)

        return json_data

    def _group_fields_by_page(self, fields):
        fields_by_page = {}
        for field in fields:
            page_number = field.get("page_number")
            if page_number not in fields_by_page:
                fields_by_page[page_number] = []
            fields_by_page[page_number].append(field)
        return fields_by_page

    def _initialize_field_descriptions(self, fields):
        for field in fields:
            field["description"] = ""

    def _get_ai_response(self, fields):
        input_text = f"""
Please provide a concise name for users to show. For each of the following fields on

Instructions:
- Return only the JSON array of objects.
- Each object should have the keys "field_name" and "description".
- Do not include any Markdown formatting or code block syntax.
- Ensure the JSON is properly formatted.

Fields:
{json.dumps([{'field_name': field['field_name']} for field in fields], indent=4)}
"""
        return self.generate_res.generate_response(input_text)

    def _assign_descriptions(self, fields, descriptions, page_number):
        if not descriptions or len(descriptions) != len(fields):
            logger.warning(f"Mismatch of descriptions: page {page_number}. ")
            descriptions += [""] * (len(fields) - len(descriptions))

        for idx, field in enumerate(fields):
            field["description"] = descriptions[idx] if idx < len(descriptions) else ""

    @staticmethod
    def grouping_by_title(fields):
        """Group fields by their titles and transform the structure."""
        grouped_titles = {}

        for field in fields:
            title = field.get("title", "Unknown title")
            if title not in grouped_titles:
                grouped_titles[title] = {
                    "title": title,
                    "description": "",
                    "questions": [],
                }
            grouped_titles[title]["questions"].append(
                {
                    "field_name": field["field_name"] if field["field_name"] is not None else "",
                    "field_type": field["field_type"] if field["field_type"] is not None else "",
                    "description": field["description"] if field["description"] is not None else "",
                    "struct_parent": field["struct_parent"] if field["struct_parent"] is not None else "",
                    "tool_tip": field["tool_tip"] if field["tool_tip"] is not None else "",
                    "initial_value": field["initial_value"] if field["initial_value"] is not None else "",
                    "rect": field["rect"] if field["rect"] is not None else "",
                    "page_number": field["page_number"] if field["page_number"] is not None else "",
                }
            )
        logger.info("Grouping has completed.")
        return list(grouped_titles.values())
