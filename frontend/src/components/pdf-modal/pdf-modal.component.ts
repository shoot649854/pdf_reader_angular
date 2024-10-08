import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { PdfViewerComponent } from '../pdf-viewer/pdf-viewer.component';
import { PdfEditorComponent } from '../pdf-editor/pdf-editor.component';

@Component({
  selector: 'app-pdf-modal',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    PdfViewerComponent,
    PdfEditorComponent,
  ],
  templateUrl: './pdf-modal.component.html',
  styleUrls: ['./pdf-modal.component.scss'],
})
export class PdfModalComponent {
  pdfBytes: Uint8Array;
  pdfSrc: string | Uint8Array | Blob | null = '';

  constructor(@Inject(MAT_DIALOG_DATA) public data: { pdfBytes: ArrayBuffer }) {
    this.pdfBytes = new Uint8Array(data.pdfBytes);
    this.pdfSrc = this.pdfBytes;
  }
}
