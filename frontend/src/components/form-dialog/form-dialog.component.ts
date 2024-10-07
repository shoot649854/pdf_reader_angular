import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
  FormControl,
} from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';

import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { PdfService } from '../../services/pdf.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDialogModule,
    MatCheckboxModule,
  ],
  templateUrl: './form-dialog.component.html',
  styleUrls: ['./form-dialog.component.scss'],
})
export class FormDialogComponent implements OnInit {
  form!: FormGroup;
  formFields: { key: string; label: string; type: string }[] = [];
  pdfUrl = '/assets/forms/i-140copy-decrypted.pdf';

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FormDialogComponent>,
    private http: HttpClient,
    private pdfService: PdfService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({});
    this.http.get('/assets/form_data.json').subscribe((data: any) => {
      this.generateForm(data);
    });
  }

  generateForm(data: any) {
    const keys = Object.keys(data);
    for (const key of keys) {
      const fieldType = data[key].type;
      const fieldValue = data[key].value;

      if (fieldType === 'checkbox') {
        this.form.addControl(key, new FormControl(fieldValue));
      } else {
        this.form.addControl(key, new FormControl(fieldValue, Validators.required));
      }

      this.formFields.push({
        key,
        label: this.formatFieldName(key),
        type: fieldType,
      });
    }
  }

  formatFieldName(fieldName: string): string {
    return fieldName.replace('[0]', '').replace(/_/g, ' ');
  }

  onSubmit() {
    if (this.form.valid) {
      const formData = this.form.value;
      console.log(formData);
      this.fillAndDownloadPdf(formData);
    } else {
      this.snackBar.open('Please fill all required fields.', 'Close', { duration: 3000 });
    }
  }

  async fillAndDownloadPdf(formData: any) {
    try {
      const pdfBytes = await this.pdfService.fillPdfForm(this.pdfUrl, formData);
      this.pdfService.downloadPdf(pdfBytes, 'filled-form.pdf');
      this.snackBar.open('PDF filled and downloaded successfully!', 'Close', { duration: 3000 });
    } catch (error) {
      console.error('Error filling PDF:', error);
      this.snackBar.open('Error filling PDF. Please try again.', 'Close', { duration: 3000 });
    }
  }

  onClose() {
    this.dialogRef.close();
  }
}
