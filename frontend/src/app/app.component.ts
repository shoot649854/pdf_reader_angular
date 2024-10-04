import { Component } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { BackendService } from './services/backend.service';
import { PdfService } from './services/pdf.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { PdfModalComponent } from './components/pdf-modal/pdf-modal.component';
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
    MatDialogModule,
    PdfViewerComponent,
    PdfEditorComponent,
    NgxExtendedPdfViewerModule,
    HttpClientModule,
  ],
})
export class AppComponent {
  title = 'pdf editor';
  pdfSrc: string | ArrayBuffer | null = null;
  pdfBytes: Uint8Array | undefined;
  isLoading = false;
  processedChunks: Uint8Array[] = [];

  constructor(
    private backendService: BackendService,
    private pdfService: PdfService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
  ) {}

  async onPdfUploaded(pdfBytes: ArrayBuffer) {
    this.isLoading = true;

    try {
      const fillable_pdf = await this.pdfService.addFillableFieldsToPdf(new Uint8Array(pdfBytes));
      if (fillable_pdf && fillable_pdf.length > 0) {
        this.pdfBytes = fillable_pdf;
        this.pdfSrc = fillable_pdf;

        const dialogRef = this.dialog.open(PdfModalComponent, {
          data: { pdfBytes: fillable_pdf },
          width: '90%',
          height: '90%',
          maxWidth: '100vw',
          maxHeight: '100vh',
          panelClass: 'custom-modalbox',
          hasBackdrop: true,
          disableClose: false,
        });

        dialogRef.afterClosed().subscribe(() => {
          this.isLoading = false;
        });
      } else {
        console.error('Failed to generate modified PDF bytes.');
      }
    } catch (error) {
      console.error('Error processing PDF to fillable form: ', error);
      this.isLoading = false;
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
            },
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
