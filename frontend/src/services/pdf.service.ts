import { Injectable } from '@angular/core';
import { PDFDocument, PDFField, PDFCheckBox, PDFTextField, PDFRadioGroup, PDFDropdown, PDFOptionList } from 'pdf-lib';
import { HttpClient } from '@angular/common/http';
import { Observable, firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class PdfService {
  constructor(private http: HttpClient) {}

  async fillPdfForm(pdfUrl: string, formData: any | null = null): Promise<Uint8Array> {
    try {
      const pdfData = await this.fetchPdfBytes(pdfUrl);
      const pdfDoc = await PDFDocument.load(pdfData);
      const form = pdfDoc.getForm();
      const fields = form.getFields();

      console.log('Available PDF Fields:');
      fields.forEach((field) => {
        const fieldName = field.getName();
        const fieldType = field.constructor.name;
        console.log(`Field Name: ${fieldName}, Field Type: ${fieldType}`);
      });

      if (formData) {
        Object.keys(formData).forEach((key) => {
          try {
            const field: PDFField | undefined = form.getField(key);
            if (!field) {
              console.warn(`Field with key '${key}' not found in the PDF.`);
              return;
            }

            const fieldValue = formData[key];

            if (field instanceof PDFTextField) {
              field.setText(fieldValue);
            } else if (field instanceof PDFCheckBox) {
              if (fieldValue === true || fieldValue === 'Yes' || fieldValue === 'On') {
                field.check();
              } else {
                field.uncheck();
              }
            } else if (field instanceof PDFRadioGroup) {
              field.select(fieldValue);
            } else if (field instanceof PDFDropdown || field instanceof PDFOptionList) {
              field.select(fieldValue);
            } else {
              console.warn(`Unsupported field type for key '${key}': ${field.constructor.name}`);
            }
          } catch (err) {
            console.error(`Error setting field with key '${key}':`, err);
          }
        });
      }

      form.flatten();
      const pdfBytes = await pdfDoc.save();
      return pdfBytes;
    } catch (error: unknown) {
      return this.handlePdfError(error, pdfUrl, formData);
    }
  }


  // New method to fill the PDF on the backend
  fillPdfFormOnBackend(formData: any): Observable<Blob> {
    return this.http.post('/api/fill-pdf', { formData }, { responseType: 'blob' });
  }

  downloadPdf(pdfBytes: Uint8Array, fileName: string) {
    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  uploadFilledPdf(file: Blob, filename: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file, filename);
    return this.http.post('/api/upload-pdf', formData);
  }

  private async fetchPdfBytes(pdfUrl: string): Promise<ArrayBuffer> {
    const response = await firstValueFrom(this.http.get(pdfUrl, { responseType: 'arraybuffer' }));
    return response;
  }

  private async handlePdfError(
    error: unknown,
    pdfUrl: string,
    formData: any | null,
  ): Promise<Uint8Array> {
    if (error instanceof Error) {
      console.error('Error filling PDF:', error);

      if (error.message.includes('encrypted')) {
        const userProvidedPassword = prompt('This PDF is encrypted. Please provide the password:');
        if (userProvidedPassword) {
          try {
            const existingPdfBytes = await this.fetchPdfBytes(pdfUrl);
            const pdfDoc = await PDFDocument.load(existingPdfBytes, {});

            // Retry filling the form with the password-protected document
            return await this.fillPdfForm(pdfUrl, formData);
          } catch (err) {
            console.error('Failed to load encrypted PDF:', err);
            throw new Error('Failed to decrypt the PDF.');
          }
        } else {
          throw new Error('Password is required to process the PDF.');
        }
      }
    } else {
      console.error('An unknown error occurred while filling the PDF.');
    }
    throw error;
  }
}