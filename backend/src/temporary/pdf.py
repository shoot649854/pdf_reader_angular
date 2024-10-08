import json

import pdfplumber
import PyPDF2


def list_pdf_fields(pdf_path):
    try:
        # Open the PDF file with PyPDF2
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)

            # Check for form fields
            if reader.pages[0].get("/AcroForm") and "/Fields" in reader.pages[0].get(
                "/AcroForm"
            ):
                fields = reader.pages[0]["/AcroForm"]["/Fields"]
                form_field_data = []

                print(f"Total fields found: {len(fields)}")
                for index, field in enumerate(fields):
                    field_object = field.getObject()
                    field_name = field_object.get("/T")  # Name of the field
                    field_type = field_object.get("/FT")  # Type of the field
                    field_value = field_object.get("/V")  # Current value of the field

                    print(
                        f"Field {index + 1} - Name: {field_name}, Type: {field_type}, Value: {field_value}"
                    )

                    form_field_data.append(
                        {
                            "fieldName": field_name if field_name else "",
                            "fieldType": field_type if field_type else "",
                            "value": field_value if field_value else "",
                        }
                    )

                # Write the form field data to a JSON file
                with open("form-fields.json", "w") as json_file:
                    json.dump(form_field_data, json_file, indent=2)

                print("Field data has been saved to form-fields.json")
            else:
                print(
                    "No form fields found using PyPDF2. Checking for annotations with pdfplumber..."
                )

                # Use pdfplumber to check for annotations or fields
                with pdfplumber.open(pdf_path) as pdf:
                    annotation_fields = []
                    for page_num, page in enumerate(pdf.pages):
                        annotations = page.annots
                        if annotations:
                            for annot in annotations:
                                annotation_fields.append(
                                    {
                                        "page": page_num + 1,
                                        "annotation_subtype": annot.get("Subtype"),
                                        "field_name": annot.get("T"),
                                        "contents": annot.get("Contents"),
                                    }
                                )

                    if annotation_fields:
                        print(
                            f"Found {len(annotation_fields)} annotations (possible form fields)."
                        )
                        for field in annotation_fields:
                            print(field)

                        # Write annotation data to a JSON file
                        with open("annotation-fields.json", "w") as json_file:
                            json.dump(annotation_fields, json_file, indent=2)
                        print("Annotation data saved to annotation-fields.json.")
                    else:
                        print("No annotations or form fields found in the PDF.")

    except Exception as e:
        print(f"Error occurred: {str(e)}")


# Path to your PDF file
pdf_path = "i-140.pdf"

# Call the function to list fields
list_pdf_fields(pdf_path)
