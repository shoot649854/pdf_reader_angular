import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-pdf-upload',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  templateUrl: './pdf-upload.component.html',
  styleUrls: ['./pdf-upload.component.scss'],
})
export class PdfUploadComponent {
  @Output() pdfUploaded = new EventEmitter<ArrayBuffer>();

  onFileSelected(event: any) {
    console.log('File selected: ', event.target.files[0]);
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        console.log('File content: ', reader.result);
        this.pdfUploaded.emit(reader.result as ArrayBuffer);
      };
      reader.readAsArrayBuffer(file);
    }
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    const file = event.dataTransfer?.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        console.log('File content: ', reader.result);
        this.pdfUploaded.emit(reader.result as ArrayBuffer);
      };
      reader.readAsArrayBuffer(file);
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }
}
