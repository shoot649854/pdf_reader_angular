import PyPDF2
from PyPDF2.generic import NameObject, TextStringObject


def fill_pdf_form1(pdf_path, data_dict):
    """
    Fill the PDF form with the provided data and flatten the PDF.

    Args:
        pdf_path (str): Path to the PDF form.
        data_dict (dict): Dictionary containing the field names and values.
    """
    # Create a PDF writer object to store the modified PDF
    pdf_writer = PyPDF2.PdfWriter()

    # Open the original PDF
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Iterate through the pages of the PDF
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]

            # Check if the page contains form fields
            if "/Annots" in page:
                # Get the annotations (form fields) from the page
                fields = page["/Annots"]

                # Iterate through the form fields
                for field in fields:
                    field_obj = field.get_object()

                    # Check if the field has a name (key)
                    if "/T" in field_obj:
                        field_name = field_obj["/T"]
                        field_name_str = field_name[
                            1:-1
                        ]  # Remove leading and trailing slashes

                        # If the field name is in the data dictionary, fill the field
                        if field_name_str in data_dict:
                            print(
                                f"Filling field: {field_name_str} with value: {data_dict[field_name_str]}"
                            )
                            field_obj.update(
                                {
                                    NameObject("/V"): TextStringObject(
                                        data_dict[field_name_str]
                                    )  # Set the field value
                                }
                            )
                            field_obj.update(
                                {NameObject("/Ff"): NumberObject(1)}  # Flatten the form
                            )

            # Add the modified page to the writer
            pdf_writer.add_page(page)

    # Write the filled PDF form to a new file
    with open("i140-filled_form.pdf", "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    print("Form saved and flattened to i140-filled_form.pdf")


# Example usage
data_dict = {
    "form1[0].#subform[0].Pt1Line1a_FamilyName[0]": "Doe",
    "form1[0].#subform[0].Pt1Line1b_GivenName[0]": "John",
    "form1[0].#subform[0].Line2_CompanyName[0]": "Acme Corporation",
}

pdf_path = "i-140.pdf"
fill_pdf_form1(pdf_path, data_dict)
