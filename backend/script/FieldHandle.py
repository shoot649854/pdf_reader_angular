import json

from src.logging.Logging import logger

from backend.src.controller.DataHandle.JSONFieldLoader import JSONFieldLoader
from backend.src.controller.DataHandle.JSONHandler import JSONHandler
from backend.src.controller.VertexAI.GenerateResponse import GenerateResponse


class FieldProcessor:
    def __init__(
        self,
        json_handler: JSONHandler,
        generate_res: GenerateResponse,
        response_parser: JSONFieldLoader,
    ):
        self.json_handler = json_handler
        self.generate_res = generate_res
        self.response_parser = response_parser
        self.json_handler = json_handler

    def generating_descriptions(self, input_path, output_path):
        """Service for processing fields and generating descriptions"""
        info = self.json_handler.load_data_from_path(input_path)
        fields_by_page = self._group_fields_by_page(info)

        for page_number, fields in fields_by_page.items():
            logger.info(f"Page: {page_number} has started to process.")
            self._initialize_field_descriptions(fields)
            ai_response = self._get_ai_response(fields)

            if not ai_response:
                logger.warning(f"No response for page {page_number}. Skipping.")
                continue

            descriptions = self.response_parser.parse(ai_response)
            self._assign_descriptions(fields, descriptions, page_number)

        self.json_handler.save_data(info)
        logger.info(f"Updated data written to {output_path}")

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
Please provide a concise description for each of the following fields on


Instructions:
- Return only the JSON array of objects.
- Do not include any additional text before or after the JSON.
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
