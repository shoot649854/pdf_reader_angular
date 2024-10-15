import PyPDF2


def fill_pdf_with_aaa(pdf_path, output_pdf_path):
    pdf_writer = PyPDF2.PdfWriter()
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            # Check if the page has annotations (form fields)
            if "/Annots" in page:
                annotations = page["/Annots"]
                for annotation in annotations:
                    field = annotation.get_object()
                    # Check if the annotation is a form field
                    if "/T" in field:
                        field_name = field["/T"]
                        field_type = field.get("/FT")
                        # Uncomment the following line to see field names and types
                        # print(f"Field name: {field_name}, Field type: {field_type}")

                        if field_type == "/Tx":  # Text field
                            # Set the text field value to 'AAA'
                            field.update(
                                {
                                    PyPDF2.generic.NameObject(
                                        "/V"
                                    ): PyPDF2.generic.create_string_object("AAA")
                                }
                            )
                        elif (
                            field_type == "/Btn"
                        ):  # Button field (checkbox or radio button)
                            # For checkboxes, set the value to 'Yes' or the appropriate on value
                            # First, check if it's a checkbox
                            if field.get("/V") == PyPDF2.generic.NameObject("/Off"):
                                # Attempt to find the 'on' value
                                if "/AP" in field:
                                    appearances = field["/AP"]
                                    if "/N" in appearances:
                                        normal_appearances = appearances["/N"]
                                        possible_values = list(
                                            normal_appearances.keys()
                                        )
                                        # Exclude '/Off' from possible on values
                                        on_values = [
                                            val
                                            for val in possible_values
                                            if val != "/Off"
                                        ]
                                        if on_values:
                                            on_value = on_values[0]
                                        else:
                                            on_value = "/Yes"  # Default value
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
                        elif field_type == "/Ch":  # Choice field (dropdown)
                            # Set the dropdown value to 'AAA'
                            field.update(
                                {
                                    PyPDF2.generic.NameObject(
                                        "/V"
                                    ): PyPDF2.generic.create_string_object("AAA"),
                                    PyPDF2.generic.NameObject(
                                        "/DV"
                                    ): PyPDF2.generic.create_string_object("AAA"),
                                }
                            )
                        else:
                            # For other field types, set the value to 'AAA'
                            field.update(
                                {
                                    PyPDF2.generic.NameObject(
                                        "/V"
                                    ): PyPDF2.generic.create_string_object("AAA")
                                }
                            )
                pdf_writer.add_page(page)
            else:
                pdf_writer.add_page(page)

    # Write the modified content to a new PDF file
    with open(output_pdf_path, "wb") as output_file:
        pdf_writer.write(output_file)


# Replace 'i-140.pdf' with the path to your PDF form
# Replace 'filled_form.pdf' with the desired output file name
pdf_path = "i-140.pdf"
fill_pdf_with_aaa(pdf_path, "filled_form.pdf")
