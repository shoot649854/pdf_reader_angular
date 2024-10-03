import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { NgxExtendedPdfViewerModule } from 'ngx-extended-pdf-viewer';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-pdf-viewer',
  standalone: true,
  imports: [CommonModule, NgxExtendedPdfViewerModule],
  templateUrl: './pdf-viewer.component.html',
  styleUrls: ['./pdf-viewer.component.scss'],
})
export class PdfViewerComponent implements OnChanges {
  @Input() pdfSrc: string | ArrayBuffer | Uint8Array | Blob | null = '';
  pdfSource: string | Uint8Array | Blob | null = '';

  ngOnChanges(changes: SimpleChanges) {
    if (changes['pdfSrc']) {
      this.updatePdfSource();
    }
  }

  private updatePdfSource() {
    if (this.pdfSrc instanceof ArrayBuffer) {
      this.pdfSource = new Uint8Array(this.pdfSrc);
    } else {
      this.pdfSource = this.pdfSrc;
    }
  }
}
