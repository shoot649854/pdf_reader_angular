from typing import List

import fitz
from pypdf import PdfReader, generic
from src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from src.logging.Logging import logger


class PDFFormExtractor:
    """Handles extraction of form fields from PDF files."""

    GRAY_TOLERANCE = 10

    def __init__(
        self,
        pdf_path,
        response_parser: JSONFieldLoader,
        font_size_threshold=11,
    ):
        self.pdf_path = pdf_path
        self.response_parser = response_parser
        self.font_size_threshold = font_size_threshold

    def get_fields_with_titles(self) -> List[str]:
        """Extract form fields and link them with their titles."""
        fields_info = []
        with fitz.open(self.pdf_path) as doc:
            for page_number, _ in enumerate(doc, start=1):
                logger.info(f"Processing page {page_number}...")
                form_fields = self._extract_form_fields(page_number)
                fields_info.extend(form_fields)
        return fields_info

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
                        "title": str(self._get_title(field.get("/TU"))),
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
                        field_info["options"] = self._get_button_values(field)
                    if "BarCode" not in str(field.get("/TU")):
                        fields_info.append(field_info)
        return fields_info

    def _get_title(self, tooltip: str) -> str:
        if not tooltip:
            return ""
        parts = tooltip.split(".")
        base_title = " ".join(part.strip() for part in parts[:2])
        if len(parts) > 1 and parts[1].strip().startswith("Section"):
            return f"{base_title} {parts[3].strip()}"
        return base_title

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
    def apply_previous_title(fields):
        """Replace null titles with the most recent non-null title."""
        previous_title = None

        for field in fields:
            if field["title"] is None:
                field["title"] = previous_title
            else:
                previous_title = field["title"]

        return fields

    def add_descriptions(self, json_data) -> List[str]:
        fields_by_page = self._group_fields_by_page(json_data)
        for _, fields in fields_by_page.items():
            for field in fields:
                tool_tip = field.get("tool_tip", "")
                if tool_tip:
                    try:
                        split_tooltip = tool_tip.strip().split(".")
                        if len(split_tooltip) > 1:
                            description = split_tooltip[-2].strip()
                        else:
                            description = tool_tip
                    except IndexError:
                        description = self._get_ai_response(field)

                    field["description"] = description
                else:
                    field["description"] = "No description provided."
        return json_data

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

            try:
                grouped_titles[title]["questions"].append(
                    {
                        "field_name": (field["field_name"] if field["field_name"] is not None else ""),
                        "field_type": (field["field_type"] if field["field_type"] is not None else ""),
                        "description": (field["description"] if field["description"] is not None else ""),
                        "struct_parent": (field["struct_parent"] if field["struct_parent"] is not None else ""),
                        "tool_tip": (field["tool_tip"] if field["tool_tip"] is not None else ""),
                        "initial_value": (field["initial_value"] if field["initial_value"] is not None else ""),
                        "rect": field["rect"] if field["rect"] is not None else "",
                        "page_number": (field["page_number"] if field["page_number"] is not None else ""),
                        "options": (field["options"] if field["options"] is not None else ""),
                    }
                )

            except Exception:
                grouped_titles[title]["questions"].append(
                    {
                        "field_name": (field["field_name"] if field["field_name"] is not None else ""),
                        "field_type": (field["field_type"] if field["field_type"] is not None else ""),
                        "description": (field["description"] if field["description"] is not None else ""),
                        "struct_parent": (field["struct_parent"] if field["struct_parent"] is not None else ""),
                        "tool_tip": (field["tool_tip"] if field["tool_tip"] is not None else ""),
                        "initial_value": (field["initial_value"] if field["initial_value"] is not None else ""),
                        "rect": field["rect"] if field["rect"] is not None else "",
                        "page_number": (field["page_number"] if field["page_number"] is not None else ""),
                    }
                )
        logger.info("Grouping has completed.")
        return list(grouped_titles.values())
