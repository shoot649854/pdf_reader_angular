import PyPDF2


def fill_pdf_form(pdf_path, output_path, field_values):
    try:
        # Open the PDF file
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            writer = PyPDF2.PdfWriter()

            # Check if the form has an AcroForm (form fields)
            if "/AcroForm" in reader.trailer["/Root"]:
                form = reader.trailer["/Root"]["/AcroForm"]
                fields = form["/Fields"]

                # Iterate over the fields and try to fill them
                for field in fields:
                    field_object = field.get_object()
                    field_name = field_object.get("/T")  # Field name
                    if field_name in field_values:
                        field_value = field_values[field_name]
                        field_object.update(
                            {
                                PyPDF2.generic.NameObject(
                                    "/V"
                                ): PyPDF2.generic.TextStringObject(field_value)
                            }
                        )
                        print(f"Filled field '{field_name}' with value '{field_value}'")
                    else:
                        print(f"Field '{field_name}' not found in provided values.")
            else:
                print("No AcroForm found in the PDF.")

            # Add the modified pages to the writer
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                writer.add_page(page)

            # Save the filled PDF to a new file
            with open(output_path, "wb") as output_pdf:
                writer.write(output_pdf)

            print(f"PDF form filled and saved as {output_path}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")


# Example of field names and values to fill in
field_values = {
    "FieldName1": "John Doe",
    "FieldName2": "1234 Main Street",
    "FieldName3": "Sample City",
}

# Path to the original and output PDF
pdf_path = "i-140.pdf"
output_path = "filled_form.pdf"

# Call the function to fill the form
fill_pdf_form(pdf_path, output_path, field_values)
