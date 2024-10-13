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

type PDFField = {
  field_name: string;
  description: string;
  fieldType: string;
  value: string;
  initial_value: string;
};

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
  formFields: {
    key: string;
    description: string;
    label: string;
    type: string;
  }[] = [];
  pdfUrl = '/assets/forms/i-140copy-decrypted.pdf';
  currentPage: number = 1;
  pageSize: number = 10;
  totalPages: number = 0;
  originalFormData: PDFField[] = []; // Store the original PDFField data here

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FormDialogComponent>,
    private http: HttpClient,
    private pdfService: PdfService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({});
    this.http
      .get<PDFField[]>('/assets/form_data.json')
      .subscribe((data: PDFField[]) => {
        this.originalFormData = data;
        this.totalPages = Math.ceil(data.length / this.pageSize);
        this.generateForm(data, this.currentPage);
      });
  }

  generateForm(data: PDFField[], page: number): void {
    const startIndex = (page - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    const pageData = data.slice(startIndex, endIndex);

    this.formFields = [];

    for (const field of pageData) {
      const key = field.field_name;
      const description = field.description ?? '';
      const fieldType = field.fieldType;
      const initialValue = field.initial_value;

      if (!key) {
        console.warn('Skipping field with missing fieldName:', field);
        continue;
      }

      let controlType: string;
      if (fieldType === '/Tx') {
        controlType = 'text';
      } else if (fieldType === 'checkbox') {
        controlType = 'checkbox';
      } else {
        controlType = 'text';
      }

      if (controlType === 'checkbox') {
        this.form.addControl(key, new FormControl(initialValue === 'true'));
      } else {
        this.form.addControl(
          key,
          new FormControl(initialValue, Validators.required)
        );
      }

      this.formFields.push({
        key,
        description,
        label: this.formatFieldName(key),
        type: controlType,
      });
    }
  }

  formatFieldName(fieldName: string): string {
    return fieldName.replace('[0]', '').replace(/_/g, ' ');
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.generateForm(this.originalFormData, this.currentPage);
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      const currentPageData = this.form.value;
      const formDataToSend = Object.keys(currentPageData).map((key) => {
        const originalField = this.originalFormData.find(
          (field) => field.field_name === key
        );
        return {
          field_name: key,
          field_type: originalField ? originalField.fieldType : '/Tx',
          initial_value: currentPageData[key] as string,
          page_number: this.currentPage,
        };
      });

      // Send the data to the API
      this.http
        .post(
          'http://localhost:5001/save_form_data_to_firestore',
          formDataToSend
        )
        .subscribe(
          (response) => {
            console.log('Form data saved successfully:', response);
            this.currentPage++;
            this.generateForm(this.originalFormData, this.currentPage);
          },
          (error) => {
            console.error('Error saving form data:', error);
          }
        );
    }
  }

  onSubmit() {
    if (this.form.valid) {
      const formData = this.form.value;
      console.log(formData);
      this.fillAndDownloadPdf(formData);
    } else {
      this.snackBar.open('Please fill all required fields.', 'Close', {
        duration: 3000,
      });
    }
  }

  async fillAndDownloadPdf(formData: {
    [key: string]: string | boolean;
  }): Promise<void> {
    try {
      const pdfBytes = await this.pdfService.fillPdfForm(this.pdfUrl, formData);
      this.pdfService.downloadPdf(pdfBytes, 'filled-form.pdf');
      this.snackBar.open('PDF filled and downloaded successfully!', 'Close', {
        duration: 3000,
      });
    } catch (error) {
      console.error('Error filling PDF:', error);
      this.snackBar.open('Error filling PDF. Please try again.', 'Close', {
        duration: 3000,
      });
    }
  }

  onClose() {
    this.dialogRef.close();
  }
}
