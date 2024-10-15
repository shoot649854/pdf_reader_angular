import json

import PyPDF2


def fill_pdf_from_json(pdf_path, output_pdf_path, json_path):
    # Read the JSON file
    with open(json_path, "r") as json_file:
        fields_data = json.load(json_file)

    data_dict = {}
    for field in fields_data:
        field_name = field["field_name"]
        if field["initial_value"]:
            value = field["initial_value"]
        else:
            value = "AAA"
        data_dict[field_name] = value

    pdf_writer = PyPDF2.PdfWriter()
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            if "/Annots" in page:
                annotations = page["/Annots"]
                for annotation in annotations:
                    field = annotation.get_object()
                    if "/T" in field:
                        field_name_obj = field["/T"]
                        field_name = (
                            field_name_obj
                            if isinstance(field_name_obj, str)
                            else field_name_obj.decode("utf-8", errors="ignore")
                        )
                        field_type = field.get("/FT")

                        if field_name in data_dict:
                            value = data_dict[field_name]

                            if field_type == "/Tx":  # Text field
                                field.update(
                                    {
                                        PyPDF2.generic.NameObject(
                                            "/V"
                                        ): PyPDF2.generic.create_string_object(value)
                                    }
                                )
                            elif field_type == "/Btn":  # Checkbox or radio button
                                if value.lower() == "yes":
                                    # Check the box
                                    if "/AP" in field:
                                        appearances = field["/AP"]
                                        if "/N" in appearances:
                                            normal_appearances = appearances["/N"]
                                            possible_values = list(
                                                normal_appearances.keys()
                                            )
                                            on_values = [
                                                val
                                                for val in possible_values
                                                if val != "/Off"
                                            ]
                                            if on_values:
                                                on_value = on_values[0]
                                            else:
                                                on_value = "/Yes"
                                        else:
                                            on_value = "/Yes"
                                    else:
                                        on_value = "/Yes"
                                    field.update(
                                        {
                                            PyPDF2.generic.NameObject(
                                                "/V"
                                            ): PyPDF2.generic.NameObject(on_value),
                                            PyPDF2.generic.NameObject(
                                                "/AS"
                                            ): PyPDF2.generic.NameObject(on_value),
                                        }
                                    )
                                else:
                                    # Uncheck the box
                                    field.update(
                                        {
                                            PyPDF2.generic.NameObject(
                                                "/V"
                                            ): PyPDF2.generic.NameObject("/Off"),
                                            PyPDF2.generic.NameObject(
                                                "/AS"
                                            ): PyPDF2.generic.NameObject("/Off"),
                                        }
                                    )
                            elif field_type == "/Ch":  # Choice field
                                field.update(
                                    {
                                        PyPDF2.generic.NameObject(
                                            "/V"
                                        ): PyPDF2.generic.create_string_object(value),
                                        PyPDF2.generic.NameObject(
                                            "/DV"
                                        ): PyPDF2.generic.create_string_object(value),
                                    }
                                )
                            else:
                                # Other field types
                                field.update(
                                    {
                                        PyPDF2.generic.NameObject(
                                            "/V"
                                        ): PyPDF2.generic.create_string_object(value)
                                    }
                                )
                pdf_writer.add_page(page)
            else:
                pdf_writer.add_page(page)

    # Write to output PDF
    with open(output_pdf_path, "wb") as output_file:
        pdf_writer.write(output_file)


# Usage example
pdf_path = "i-140.pdf"
output_pdf_path = "filled_form.pdf"
json_path = "form_fields.json"

fill_pdf_from_json(pdf_path, output_pdf_path, json_path)
