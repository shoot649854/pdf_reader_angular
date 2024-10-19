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
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';

import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { PdfService } from '../../services/pdf.service';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Base_URL, GLOBAL_TEXTFIELD, DATA_PATH } from '../setting';
import { PDFFieldType } from './type';
import { createFormControl, formatFieldName, getFieldType } from './setting';

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
    MatSelectModule,
    MatOptionModule,
  ],
  templateUrl: './form-dialog.component.html',
  styleUrls: ['./form-dialog.component.scss'],
})
export class FormDialogComponent implements OnInit {
  form!: FormGroup;
  formFields: any[] = [];
  pdfUrl = '/assets/forms/i-140copy-decrypted.pdf';
  currentPage = 1;
  pageSize = 10;
  totalPages = 0;
  originalFormData: PDFFieldType[] = [];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FormDialogComponent>,
    private http: HttpClient,
    private pdfService: PdfService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.initializeForm();
    this.loadFormData();
  }

  fieldDescriptions: { [key: string]: string } = {
    TestCheckButton_FieldName: 'TestCheckButton_FieldName',
    G28CheckBox: 'form1[0].#subform[0].G28CheckBox[0]',
  };

  private initializeForm(): void {
    this.form = this.fb.group({
      TestCheckButton_FieldName: [false],
      G28CheckBox: [false],
    });

    this.form.get('TestCheckButton_FieldName')?.valueChanges.subscribe(() => {
      this.toggleDependentFields();
    });

    this.form.get('G28CheckBox')?.valueChanges.subscribe(() => {
      this.toggleDependentFields();
    });
  }

  private loadFormData(): void {
    this.http.get<PDFFieldType[]>(DATA_PATH).subscribe((data) => {
      this.originalFormData = data;
      this.totalPages = Math.ceil(data.length / this.pageSize);
      this.generateForm(data, this.currentPage);
    });
  }

  private generateForm(data: PDFFieldType[], page: number): void {
    const pageData = this.getPageData(data, page);
    this.formFields = [];

    pageData.forEach((field) => this.addFieldToForm(field));
    this.toggleDependentFields();
  }

  private getPageData(data: PDFFieldType[], page: number): PDFFieldType[] {
    const startIndex = (page - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    return data.slice(startIndex, endIndex);
  }

  private addFieldToForm(field: PDFFieldType): void {
    if (!field.field_name) return;

    const shouldShow = !field.need || this.shouldShowField(field.need);
    if (!shouldShow) return;

    const control = createFormControl(field);
    this.form.addControl(field.field_name, control);
    this.formFields.push(this.createFieldMeta(field));
  }

  private createFieldMeta(field: PDFFieldType): any {
    return {
      key: field.field_name,
      description: field.description,
      label: formatFieldName(field.field_name),
      type: getFieldType(field.field_type),
      options: field.options ?? [],
    };
  }

  private shouldShowField(fieldNeeds: string[]): boolean {
    if (!fieldNeeds || !Array.isArray(fieldNeeds)) {
      return true;
    }
    return fieldNeeds.every((controlName) => {
      const simpleName =
        controlName
          .split('.')
          .pop()
          ?.replace(/[\[\]0]/g, '') || controlName;
      const control = this.form.get(simpleName);
      return control?.value === true || control?.value === '/Y';
    });
  }

  toggleDependentFields(): void {
    const pageData = this.getPageData(this.originalFormData, this.currentPage);
    this.formFields = pageData
      .map((field) => {
        const shouldShow = !field.need || this.shouldShowField(field.need);
        if (shouldShow) {
          this.addFieldToForm(field);
          return this.createFieldMeta(field);
        } else {
          this.form.removeControl(field.field_name);
          return null;
        }
      })
      .filter((field) => field !== null);
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
      this.saveFormData(currentPageData);
    }
  }

  private saveFormData(currentPageData: any): void {
    const formDataToSend = Object.keys(currentPageData).map((key) => {
      const originalField = this.originalFormData.find(
        (field) => field.field_name === key
      );
      return {
        field_name: key,
        field_type: originalField?.field_type ?? GLOBAL_TEXTFIELD,
        initial_value: currentPageData[key] as string,
        page_number: this.currentPage,
      };
    });

    this.http
      .post(`/${Base_URL}/save_form_data_to_firestore`, formDataToSend)
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

  onSubmit(): void {
    if (this.form.valid) {
      const formData = this.prepareFormData();
      this.generatePdf(formData);
    } else {
      this.snackBar.open('Please fill all required fields.', 'Close', {
        duration: 3000,
      });
    }
  }

  private prepareFormData() {
    const formData = this.form.value;
    return Object.keys(formData).map((key) => ({
      field_name: key,
      initial_value: formData[key],
      field_type: GLOBAL_TEXTFIELD,
      page_number: 1,
    }));
  }

  private generatePdf(formData: any[]): void {
    this.http
      .post(`/${Base_URL}/generate_pdf`, formData, { responseType: 'blob' })
      .subscribe(
        (response: Blob) => {
          this.downloadPdf(response);
          this.snackBar.open(
            'PDF generated and downloaded successfully!',
            'Close',
            {
              duration: 3000,
            }
          );
        },
        (error) => {
          console.error('Error generating PDF:', error);
          this.snackBar.open(
            'Error generating PDF. Please try again.',
            'Close',
            {
              duration: 3000,
            }
          );
        }
      );
  }

  private downloadPdf(blob: Blob): void {
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = 'filled-form.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(blobUrl);
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

  onClose(): void {
    this.dialogRef.close();
  }
}
