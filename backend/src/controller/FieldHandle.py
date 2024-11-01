import json

from src.controller.GenerateResponse import GenerateResponse
from src.logging.Logging import logger


class FieldDescriptionGenerator:
    def __init__(self, response_generator: GenerateResponse):
        self._response_generator = response_generator

    def generate(self, input_text):
        """Concrete implementation of AIResponseGenerator"""
        return self._response_generator.generate_response(input_text)


class FieldProcessor:
    def __init__(self, data_loader, description_generator, response_parser):
        self.data_loader = data_loader
        self.description_generator = description_generator
        self.response_parser = response_parser

    def process_fields(self, input_path, output_path):
        """Service for processing fields and generating descriptions"""
        info = self.data_loader.load_json_data(input_path)
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

        self._write_to_file(info, output_path)
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
        input_text = self._generate_prompt(fields)
        return self.description_generator.generate(input_text)

    def _generate_prompt(self, fields):
        """Creates a prompt text for AI model based on the fields."""
        return f"""
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

    def _assign_descriptions(self, fields, descriptions, page_number):
        if not descriptions or len(descriptions) != len(fields):
            logger.warning(
                f"Mismatch in number of descriptions for page {page_number}. "
                "Filling missing descriptions with empty strings."
            )
            descriptions += [""] * (len(fields) - len(descriptions))

        for idx, field in enumerate(fields):
            field["description"] = descriptions[idx] if idx < len(descriptions) else ""

    def _write_to_file(self, data, output_path):
        with open(output_path, "w") as outfile:
            json.dump(data, outfile, indent=4)
