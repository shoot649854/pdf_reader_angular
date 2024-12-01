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
import { PDFQuestionType, PDFItemType } from './type';
import { createFormControl, formatFieldName, get_field_type } from './setting';
import { SuccessPopupComponent } from '../success-popup/success-popup.component';
import { FormDataService } from '../../services/form-data.service';

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
  originalFormData: PDFItemType[] = [];
  formSections: PDFItemType[] = [];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FormDialogComponent>,
    private http: HttpClient,
    private pdfService: PdfService,
    private snackBar: MatSnackBar,
    private formDataService: FormDataService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.initialize_form();
    console.log(DATA_PATH);
    this.load_form_data(DATA_PATH);
  }

  /**
   * Initializes an empty form group.
   */
  private initialize_form(): void {
    this.form = this.fb.group({});
  }

  /**
   * Loads form data from an external data source and generates the form.
   * Also sets up value change subscriptions for form controls.
   * @param dpath - path of data that is read
   */
  private load_form_data(dpath: string): void {
    this.http.get<PDFItemType[]>(dpath).subscribe((item) => {
      this.originalFormData = item;
      this.totalPages = Math.ceil(item.length / this.pageSize);

      const items = this._get_page_data(item, this.currentPage);
      this._generate_form(items);

      item.forEach((item) => {
        const questions = item.questions;
        this._setup_value_change_subscriptions(questions);
      });
    });
  }

  /**
   * Generates the form for a specific page using the loaded data.
   * @param item - The entire form data set.
   * @param page - The current page number.
   */
  private _generate_form(items: PDFItemType[]): void {
    this.formSections = items.map((item) => ({
      title: item.title,
      subtitle: item.subtitle,
      questions: item.questions,
      fields: [], // Always initialize fields as an empty array
    }));

    items.forEach((item, index) => {
      const questions = item.questions;
      this._add_field_to_form(questions);

      // Assign visible fields to the corresponding section
      const visibleFields = questions
        .filter((q) => !q.need || this._should_show_field(q.need))
        .map((q) => this._create_field_meta(q))
        .filter((field) => field !== null);

      this.formSections[index].fields = visibleFields as any[];
    });

    // Optionally, remove sections without fields
    this.formSections = this.formSections.filter(
      (section) => (section.fields ?? []).length > 0
    );
  }

  /**
   * Extracts the data for a specific page from the entire form dataset.
   * @param data - The entire form data set.
   * @param page - The current page number.
   * @returns The form data for the specified page.
   */
  private _get_page_data(data: PDFItemType[], page: number): PDFItemType[] {
    const startIndex = (page - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    return data.slice(startIndex, endIndex);
  }

  /**
   * Toggles the visibility of dependent form fields based on their conditions.
   */
  private _toggle_dependent_fields(): void {
    const pageData = this._get_page_data(
      this.originalFormData,
      this.currentPage
    ) as PDFItemType[];

    const updatedFormFields = pageData
      .flatMap((item) => {
        const questions = item.questions as PDFQuestionType[];
        return questions.map((question: PDFQuestionType) => {
          const shouldShow =
            !question.need || this._should_show_field(question.need);
          if (shouldShow) {
            if (!this.form.contains(question.field_name)) {
              this._add_field_to_form(questions);
            }
            return this._create_field_meta(question);
          } else {
            if (this.form.contains(question.field_name)) {
              this.form.removeControl(question.field_name);
            }
            return null;
          }
        });
      })
      .filter((VisibleQuestion) => VisibleQuestion !== null);

    if (JSON.stringify(this.formFields) !== JSON.stringify(updatedFormFields)) {
      this.formFields = updatedFormFields as any[];
    }
  }

  /**
   * Adds a form control to the form if it should be displayed.
   * @param field - The field data containing information about the form control.
   */
  private _add_field_to_form(questions: PDFQuestionType[]): void {
    questions.forEach((question) => {
      if (!question.field_name) return;

      const shouldShow =
        !question.need || this._should_show_field(question.need);
      if (!shouldShow) return;

      if (!this.form.contains(question.field_name)) {
        const control = createFormControl(question);
        this.form.addControl(question.field_name, control);
      }

      this.formFields.push(this._create_field_meta(question));
    });
  }

  /**
   * Sets up value change subscriptions for each form control.
   * @param data - The entire form data set.
   */
  private _setup_value_change_subscriptions(
    questions: PDFQuestionType[]
  ): void {
    questions.forEach((question) => {
      if (question.field_name) {
        const control = this.form.get([question.field_name]);
        if (control) {
          control.valueChanges.subscribe(() => {
            this._toggle_dependent_fields();
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
  private _create_field_meta(field: PDFQuestionType): any {
    return {
      name: field.field_name,
      description: field.description,
      label: formatFieldName(field.field_name),
      type: get_field_type(field.field_type),
      options: field.options ?? [],
    };
  }

  /**
   * Determines whether a field should be displayed based on dependencies.
   * @param fieldNeeds - The dependencies that determine if the field should be shown.
   * @returns A boolean indicating if the field should be displayed.
   */
  private _should_show_field(fieldNeeds: string[]): boolean {
    if (!fieldNeeds || !Array.isArray(fieldNeeds)) {
      return true;
    }
    return fieldNeeds.every((controlName) => {
      const control = this.form.get([controlName]);
      return control?.value === true || control?.value === '/Y';
    });
  }

  /**
   * Navigates to the previous page if available.
   */
  previous_page(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this._generate_form(this.originalFormData);
    }
  }

  /**
   * Navigates to the next page if available and saves the current page data.
   */
  next_page(): void {
    if (this.currentPage < this.totalPages) {
      const currentPageData = this.form.value;
      this._save_form_data_to_backend(currentPageData);
      this._save_form_data(currentPageData);
    }
  }

  /**
   * Saves data to the backend to update the JSON file.
   * @param currentPageData - The form data of the current page.
   */
  private _save_form_data_to_backend(currentPageData: any): void {
    // Update originalFormData with the currentPageData values
    // for (let key in currentPageData) {
    //   const field = this.originalFormData.find(
    //     (item: PDFQuestionType) => item.field_name === key
    //   );
    //   if (field) {
    //     field.initial_value = currentPageData[key];
    //   }
    // }
    // Use the service to send the updated form data to the backend
    // this.formDataService.updateFormData(this.originalFormData).subscribe(
    //   () => {
    //     this.snackBar.open('Form data saved successfully!', 'Close', {
    //       duration: 3000,
    //     });
    //   },
    //   (error) => {
    //     console.error('Error saving form data to the backend:', error);
    //     this.snackBar.open(
    //       'Error saving form data. Please try again.',
    //       'Close',
    //       {
    //         duration: 3000,
    //       }
    //     );
    //   }
    // );
  }

  /**
   * Saves the form data of the current page to an external service.
   * @param currentPageData - The form data to be saved.
   */
  private _save_form_data(currentPageData: any): void {
    const formDataToSend = Object.keys(currentPageData).map((name) => {
      //   const originalField = this.originalFormData.find(
      //     (field) => field.field_name === name
      //   );
      //   return {
      //     field_name: name,
      //     field_type: originalField?.field_type ?? GLOBAL_TEXTFIELD,
      //     initial_value: currentPageData[name] as string,
      //     page_number: this.currentPage,
      //   };
    });

    this.http
      .post(`${Base_URL}/firestore/save_form_data_to_firestore`, formDataToSend)
      .subscribe(
        (response) => {
          console.log('Form data saved successfully:', response);
          this.currentPage++;
          this._generate_form(this.originalFormData);
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
      .post(`${Base_URL}/generate_pdf`, formData, { responseType: 'blob' })
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
