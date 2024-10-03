import { Component } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { BackendService } from './services/backend.service';
import { PdfService } from './services/pdf.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { PdfUploadComponent } from './components/pdf-upload/pdf-upload.component';
import { PdfViewerComponent } from './components/pdf-viewer/pdf-viewer.component';
import { PdfEditorComponent } from './components/pdf-editor/pdf-editor.component';
import { NgxExtendedPdfViewerModule } from 'ngx-extended-pdf-viewer';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    MatToolbarModule,
    MatProgressBarModule,
    PdfUploadComponent,
    PdfViewerComponent,
    PdfEditorComponent,
    NgxExtendedPdfViewerModule,
    HttpClientModule
  ]
})
export class AppComponent {
  title = 'pdf editor';
  pdfSrc: string | ArrayBuffer | null = null;
  pdfBytes: Uint8Array | undefined;
  isLoading = false;
  processedChunks: Uint8Array[] = [];

  constructor(private backendService: BackendService, private pdfService: PdfService, private snackBar: MatSnackBar) {}

  onPdfUploaded(event: any) {
    const file = event.target?.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      this.pdfSrc = reader.result;
      this.pdfBytes = new Uint8Array(reader.result as ArrayBuffer);
    };
    if (file) {
      reader.readAsArrayBuffer(file);
    }
  }

  async processPdf() {
    if (this.pdfBytes) {
      this.isLoading = true;
      try {
        const chunks = await this.pdfService.splitPdf(this.pdfBytes);
        for (const chunk of chunks) {
          this.backendService.processPdfChunk(chunk).subscribe({
            next: (response) => {
              this.processedChunks.push(new Uint8Array(response.data));
            },
            error: (error) => {
              this.showError('Error processing PDF chunk.');
            },
            complete: () => {
              this.isLoading = false;
              this.mergeChunks();
            }
          });
        }
      } catch (error) {
        this.showError('Error splitting PDF.');
        this.isLoading = false;
      }
    }
  }

  async mergeChunks() {
    try {
      const mergedPdf = await this.pdfService.mergePdfChunks(this.processedChunks);
      this.pdfSrc = mergedPdf;
    } catch (error) {
      this.showError('Error merging PDF chunks.');
    }
  }

  showError(message: string) {
    this.snackBar.open(message, 'Close', { duration: 5000 });
  }
}
