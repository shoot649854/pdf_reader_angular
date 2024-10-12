import { Component } from '@angular/core';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';

import { NgxExtendedPdfViewerModule } from 'ngx-extended-pdf-viewer';

import { FormDialogComponent } from '../components/form-dialog/form-dialog.component';

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
    MatDialogModule,
    NgxExtendedPdfViewerModule,
    MatButtonModule,
  ],
})
export class AppComponent {
  title = 'pdf editor';
  pdfSrc: string | ArrayBuffer | null = null;
  pdfBytes: Uint8Array | undefined;
  isLoading = false;
  processedChunks: Uint8Array[] = [];

  constructor(
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {}

  openFormDialog(): void {
    const dialogRef = this.dialog.open(FormDialogComponent, {
      minWidth: '400px',
      width: '100%',
      height: 'auto',
      maxWidth: '600px',
      disableClose: false,
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        console.log('Form Data:', result);
        this.saveResultAsJson(result);
      }
    });
  }

  saveResultAsJson(result: { [key: string]: string | boolean }): void {
    const jsonData = JSON.stringify(result, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'form-data.json';
    anchor.click();
    window.URL.revokeObjectURL(url);
  }

  showError(message: string) {
    this.snackBar.open(message, 'Close', { duration: 5000 });
  }
}
