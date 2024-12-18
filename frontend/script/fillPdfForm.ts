import { PDFDocument } from 'pdf-lib';
import * as fs from 'fs';

async function fillPdfForm() {
  try {
    const formUrl = 'src/assets/forms/i-140copy-decrypted.pdf';
    const formPdfBytes = fs.readFileSync(formUrl);

    const pdfDoc = await PDFDocument.load(formPdfBytes, {
      ignoreEncryption: true,
      throwOnInvalidObject: false,
    });

    const form = pdfDoc.getForm();
    const fields = form.getFields();

    // Log the total number of fields
    console.log(`Total fields found: ${fields.length}`);

    const formFieldData: {
      fieldName: string;
      fieldType: string;
      value: string;
    }[] = [];

    fields.forEach((field, index) => {
      const fieldName = field.getName();
      const fieldType = field.constructor.name;

      // Log each field with its index
      console.log(
        `Field ${index + 1} - Name: ${fieldName}, Type: ${fieldType}`
      );

      formFieldData.push({
        fieldName: fieldName,
        fieldType: fieldType,
        value: '', // Placeholder for the value (can be modified)
      });
    });

    // Write all form field data to a JSON file
    const jsonData = JSON.stringify(formFieldData, null, 2);
    fs.writeFileSync('form-fields.json', jsonData);

    // Optional: fill the form fields with sample data
    fields.forEach((field) => {
      const fieldName = field.getName();
      const fieldType = field.constructor.name;

      if (fieldType === 'PDFTextField') {
        const textField = form.getTextField(fieldName);
        textField.setText('Sample Text');
        console.log(`Filled text field: ${fieldName}`);
      } else if (fieldType === 'PDFCheckBox') {
        const checkBox = form.getCheckBox(fieldName);
        checkBox.check();
        console.log(`Checked checkbox: ${fieldName}`);
      } else {
        console.log(
          `Unsupported field type: ${fieldType} for field: ${fieldName}`
        );
      }
    });

    // Flatten the form and save the modified PDF
    form.flatten();
    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('filled-form.pdf', pdfBytes);
    console.log('PDF form filled and saved successfully.');
  } catch (error: any) {
    console.error('Error in fillPdfForm:', error);
    if (error.message.includes('has no form field')) {
      console.error(
        'The specified form field was not found. Please check the available fields in the console output above.'
      );
    }
  }
}

fillPdfForm().catch((error) => {
  console.error('Top-level error:', error);
});
