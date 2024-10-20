import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';

import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { PdfService } from '../../services/pdf.service';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Base_URL, GLOBAL_TEXTFIELD, DATA_PATH } from '../setting';
import { PDFFieldType } from './type';
import { createFormControl, formatFieldName, getFieldType } from './setting';
import { SuccessPopupComponent } from '../success-popup/success-popup.component';

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
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.initializeForm();
    this.loadFormData();
  }

  /**
   * Initializes an empty form group.
   */
  private initializeForm(): void {
    this.form = this.fb.group({});
  }

  /**
   * Loads form data from an external data source and generates the form.
   * Also sets up value change subscriptions for form controls.
   */
  private loadFormData(): void {
    this.http.get<PDFFieldType[]>(DATA_PATH).subscribe((data) => {
      this.originalFormData = data;
      this.totalPages = Math.ceil(data.length / this.pageSize);
      this.generateForm(data, this.currentPage);
      this.setupValueChangeSubscriptions(data);
    });
  }

  /**
   * Generates the form for a specific page using the loaded data.
   * @param data - The entire form data set.
   * @param page - The current page number.
   */
  private generateForm(data: PDFFieldType[], page: number): void {
    const pageData = this.getPageData(data, page);
    this.formFields = [];

    pageData.forEach((field) => this.addFieldToForm(field));
    this.toggleDependentFields();
  }

  /**
   * Extracts the data for a specific page from the entire form dataset.
   * @param data - The entire form data set.
   * @param page - The current page number.
   * @returns The form data for the specified page.
   */
  private getPageData(data: PDFFieldType[], page: number): PDFFieldType[] {
    const startIndex = (page - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    return data.slice(startIndex, endIndex);
  }

  /**
   * Adds a form control to the form if it should be displayed.
   * @param field - The field data containing information about the form control.
   */
  private addFieldToForm(field: PDFFieldType): void {
    if (!field.field_name) return;

    const shouldShow = !field.need || this.shouldShowField(field.need);
    if (!shouldShow) return;

    if (!this.form.contains(field.field_name)) {
      const control = createFormControl(field);
      this.form.addControl(field.field_name, control);
    }

    this.formFields.push(this.createFieldMeta(field));
  }

  /**
   * Sets up value change subscriptions for each form control.
   * @param data - The entire form data set.
   */
  private setupValueChangeSubscriptions(data: PDFFieldType[]): void {
    data.forEach((field) => {
      if (field.field_name) {
        const control = this.form.get([field.field_name]);
        if (control) {
          control.valueChanges.subscribe(() => {
            this.toggleDependentFields();
          });
        }
      }
    });
  }

  /**
   * Creates metadata for a form field.
   * @param field - The field data containing information about the form control.
   * @returns An object containing field metadata.
   */
  private createFieldMeta(field: PDFFieldType): any {
    return {
      name: field.field_name,
      description: field.description,
      label: formatFieldName(field.field_name),
      type: getFieldType(field.field_type),
      options: field.options ?? [],
    };
  }

  /**
   * Determines whether a field should be displayed based on dependencies.
   * @param fieldNeeds - The dependencies that determine if the field should be shown.
   * @returns A boolean indicating if the field should be displayed.
   */
  private shouldShowField(fieldNeeds: string[]): boolean {
    if (!fieldNeeds || !Array.isArray(fieldNeeds)) {
      return true;
    }
    return fieldNeeds.every((controlName) => {
      const control = this.form.get([controlName]);
      return control?.value === true || control?.value === '/Y';
    });
  }

  /**
   * Toggles the visibility of dependent form fields based on their conditions.
   */
  toggleDependentFields(): void {
    const pageData = this.getPageData(this.originalFormData, this.currentPage);
    this.formFields = pageData
      .map((field) => {
        const shouldShow = !field.need || this.shouldShowField(field.need);

        if (shouldShow) {
          this.addFieldToForm(field);
          return this.createFieldMeta(field);
        } else {
          if (this.form.contains(field.field_name)) {
            this.form.removeControl(field.field_name);
          }
          return null;
        }
      })
      .filter((field) => field !== null);
  }

  /**
   * Navigates to the previous page if available.
   */
  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.generateForm(this.originalFormData, this.currentPage);
    }
  }

  /**
   * Navigates to the next page if available and saves the current page data.
   */
  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      const currentPageData = this.form.value;
      this.saveFormData(currentPageData);
    }
  }

  /**
   * Saves the form data of the current page to an external service.
   * @param currentPageData - The form data to be saved.
   */
  private saveFormData(currentPageData: any): void {
    const formDataToSend = Object.keys(currentPageData).map((name) => {
      const originalField = this.originalFormData.find(
        (field) => field.field_name === name
      );
      return {
        field_name: name,
        field_type: originalField?.field_type ?? GLOBAL_TEXTFIELD,
        initial_value: currentPageData[name] as string,
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

  /**
   * Submits the form by validating it and generating a PDF if valid.
   */
  onSubmit(): void {
    // if (this.form.valid) {
    //   const formData = this.prepareFormData();
    //   this.generatePdf(formData);
    // } else {
    //   this.snackBar.open('Please fill all required fields.', 'Close', {
    //     duration: 3000,
    //   });
    // }
  }

  /**
   * Prepares form data for submission.
   * @returns An array containing the form data.
   */
  private prepareFormData() {
    const formData = this.form.value;
    return Object.keys(formData).map((name) => ({
      field_name: name,
      initial_value: formData[name],
      field_type: GLOBAL_TEXTFIELD,
      page_number: 1,
    }));
  }

  /**
   * Generates a PDF based on the provided form data.
   * @param formData - The form data to generate the PDF with.
   */
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

  /**
   * Downloads a PDF blob by creating a link and triggering a download.
   * @param blob - The PDF blob to be downloaded.
   */
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

  /**
   * Fills and downloads the PDF using the provided form data.
   * @param formData - The form data used to fill the PDF.
   */
  async fillAndDownloadPdf(formData: {
    [name: string]: string | boolean;
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

  /**
   * Closes the form dialog.
   */
  onClose(): void {
    console.log('FormDialogComponent: onClose called'); // Debug log

    // Open Success Popup
    const dialogRef = this.dialog.open(SuccessPopupComponent, {
      data: {
        message: 'Form closed successfully!',
      },
      width: '400px',
      height: 'auto',
      enterAnimationDuration: '300ms',
      exitAnimationDuration: '300ms',
      panelClass: 'custom-dialog-container',
    });

    dialogRef.afterOpened().subscribe(() => {
      console.log('SuccessPopupComponent is opened');
    });
    this.dialogRef.close();
  }
}
