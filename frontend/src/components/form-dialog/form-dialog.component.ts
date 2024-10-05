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
  form!: FormGroup; // Declare form but do not initialize it here
  formFields: { key: string; label: string; type: string }[] = [];

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FormDialogComponent>,
    private http: HttpClient, // Inject HttpClient to fetch JSON data
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({});
    this.http.get('/assets/form_data.json').subscribe((data: any) => {
      this.generateForm(data);
    });
  }

  // Function to generate form dynamically based on the JSON
  generateForm(data: any) {
    const keys = Object.keys(data);
    for (const key of keys) {
      const fieldType = data[key].type;
      const fieldValue = data[key].value;

      // Add the form control based on the field type
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

  // Helper function to make the field name readable
  formatFieldName(fieldName: string): string {
    return fieldName.replace('[0]', '').replace(/_/g, ' ');
  }

  onSubmit() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }

  onClose() {
    this.dialogRef.close();
  }
}
