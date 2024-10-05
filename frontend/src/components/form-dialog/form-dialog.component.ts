import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormControl } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
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
    MatDialogModule
  ],
  templateUrl: './form-dialog.component.html',
  styleUrls: ['./form-dialog.component.scss'],
})
export class FormDialogComponent implements OnInit {
  form!: FormGroup;  // Declare form but do not initialize it here
  formFields: { key: string, label: string }[] = []; // Array to hold the dynamic fields with formatted labels

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<FormDialogComponent>,
    private http: HttpClient // Inject HttpClient to fetch JSON data
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
      this.form.addControl(key, new FormControl(data[key], Validators.required));

      // Push the field and its formatted label into the array
      this.formFields.push({ 
        key, 
        label: this.formatFieldName(key) 
      });
    }
  }

  // Helper function to make the field name readable
  formatFieldName(fieldName: string): string {
    return fieldName.replace('[0]', '').replace(/_/g, ' ');
  }

  onSubmit() {
    if (this.form.valid) {
      // Pass the form data to the calling component
      this.dialogRef.close(this.form.value);
    }
  }

  onClose() {
    this.dialogRef.close();
  }
}
