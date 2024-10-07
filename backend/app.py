import io

from flask import Flask, jsonify, request, send_file
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)


@app.route("/api/fill-pdf", methods=["POST"])
def fill_pdf_form_api():
    try:
        form_data = request.json.get("formData")
        pdf_path = "path_to_your_i140_template.pdf"

        filled_pdf_stream = fill_pdf_form1(pdf_path, form_data)

        return send_file(
            filled_pdf_stream, as_attachment=True, download_name="filled_i140_form.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def fill_pdf_form1(pdf_path, data_dict):
    pdf_writer = PdfWriter()
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            if "/Annots" in page:
                fields = page["/Annots"]
                for field_ref in fields:
                    field_obj = field_ref.get_object()
                    if "/T" in field_obj:
                        field_name_str = field_obj["/T"][1:-1]
                        if field_name_str in data_dict:
                            field_obj.update(
                                {
                                    PyPDF2.generic.NameObject(
                                        "/V"
                                    ): PyPDF2.generic.create_string_object(
                                        data_dict[field_name_str]
                                    )
                                }
                            )

            pdf_writer.add_page(page)

    pdf_stream = io.BytesIO()
    pdf_writer.write(pdf_stream)
    pdf_stream.seek(0)
    return pdf_stream


if __name__ == "__main__":
    app.run(debug=True)
