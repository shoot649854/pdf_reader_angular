import json

import PyPDF2


def extract_form_fields(pdf_path, output_json_path):
    fields_info = []

    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_number, page in enumerate(pdf_reader.pages, start=1):
            # Check if the page has annotations (form fields)
            if "/Annots" in page:
                annotations = page["/Annots"]
                for annotation in annotations:
                    field = annotation.get_object()
                    # Check if the annotation is a form field
                    if "/T" in field:
                        field_name = field.get("/T")
                        field_type = field.get("/FT")
                        initial_value = field.get("/V")
                        # Prepare field information
                        field_info = {
                            "field_name": str(field_name),
                            "field_type": str(field_type),
                            "initial_value": (
                                str(initial_value) if initial_value else ""
                            ),
                            "page_number": page_number,
                        }
                        # Add any other necessary fields
                        # For choice fields, include options
                        if field_type == "/Ch":
                            options = field.get("/Opt")
                            if options:
                                # Convert options to a list of strings
                                options_list = []
                                for option in options:
                                    if isinstance(option, PyPDF2.generic.ArrayObject):
                                        options_list.append(str(option[0]))
                                    else:
                                        options_list.append(str(option))
                                field_info["options"] = options_list
                        # For checkboxes and radio buttons, get possible values
                        elif field_type == "/Btn":
                            if "/AP" in field:
                                appearances = field["/AP"]
                                if "/N" in appearances:
                                    normal_appearances = appearances["/N"]
                                    possible_values = [
                                        str(key) for key in normal_appearances.keys()
                                    ]
                                    field_info["possible_values"] = possible_values
                        # Append to the list
                        fields_info.append(field_info)
    # Write the fields_info to a JSON file
    with open(output_json_path, "w") as json_file:
        json.dump(fields_info, json_file, indent=4)


# Usage example:
pdf_path = "i-140.pdf"
output_json_path = "form_fields.json"
extract_form_fields(pdf_path, output_json_path)
