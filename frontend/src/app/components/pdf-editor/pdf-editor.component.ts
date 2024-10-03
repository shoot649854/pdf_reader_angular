import { Component, Input } from '@angular/core';
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pdf-editor',
  standalone: true,
  imports: [FormsModule, MatButtonModule, CommonModule],
  templateUrl: './pdf-editor.component.html',
  styleUrls: ['./pdf-editor.component.scss']
})
export class PdfEditorComponent {
  @Input() pdfBytes: Uint8Array | undefined;
  text: string = '';

  async addText() {
    if (!this.pdfBytes) return;

    const pdfDoc = await PDFDocument.load(this.pdfBytes);
    const pages = pdfDoc.getPages();
    const firstPage = pages[0];
    const helveticaFont = await pdfDoc.embedFont(StandardFonts.Helvetica);
    firstPage.drawText(this.text, { x: 50, y: 750, size: 24, font: helveticaFont, color: rgb(0, 0, 0) });
    this.pdfBytes = await pdfDoc.save();
  }

  savePdf() {
    if (this.pdfBytes) {
      const blob = new Blob([this.pdfBytes], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'edited.pdf';
      link.click();
    }
  }
}
