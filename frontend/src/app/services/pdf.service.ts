import { Injectable } from '@angular/core';
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';

@Injectable({
  providedIn: 'root',
})
export class PdfService {
  async mergePdfChunks(chunks: Uint8Array[]): Promise<string> {
    const mergedPdf = await PDFDocument.create();
    for (const chunk of chunks) {
      const pdf = await PDFDocument.load(chunk);
      const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
      copiedPages.forEach((page) => mergedPdf.addPage(page));
    }
    const mergedBytes = await mergedPdf.save();
    return URL.createObjectURL(new Blob([mergedBytes], { type: 'application/pdf' }));
  }
  async splitPdf(pdfBytes: Uint8Array, chunkSize = 5): Promise<Uint8Array[]> {
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const totalPages = pdfDoc.getPageCount();
    const chunks: Uint8Array[] = [];

    for (let i = 0; i < totalPages; i += chunkSize) {
      const newPdf = await PDFDocument.create();
      const copiedPages = await newPdf.copyPages(
        pdfDoc,
        [...Array(chunkSize).keys()].map((j) => i + j),
      );
      copiedPages.forEach((page) => newPdf.addPage(page));
      chunks.push(await newPdf.save());
    }

    return chunks;
  }
  async addFillableFieldsToPdf(pdfBytes: Uint8Array): Promise<Uint8Array> {
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const form = pdfDoc.getForm();

    const firstPage = pdfDoc.getPages()[0];
    const textField = form.createTextField('NameField');

    textField.setText('Enter your name');
    textField.addToPage(firstPage, { x: 50, y: 500, width: 300, height: 25 });

    const checkboxField = form.createCheckBox('AgreeCheckbox');
    checkboxField.addToPage(firstPage, { x: 50, y: 450, width: 20, height: 20 });

    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
    textField.updateAppearances(font);
    checkboxField.updateAppearances();

    const modifiedPdfBytes = await pdfDoc.save();
    return modifiedPdfBytes;
  }
}
