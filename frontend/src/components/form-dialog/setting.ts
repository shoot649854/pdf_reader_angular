import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { FormControl } from '@angular/forms';
import {
  GLOBAL_TEXTFIELD,
  GLOBAL_BUTTON,
  GLOBAL_CHOICE,
  GLOBAL_NUMBER,
} from '../setting';
import { PDFFieldType } from './type';

export function createFormControl(field: PDFFieldType): FormControl {
  const initialValue = field.initial_value;
  switch (field.field_type) {
    case GLOBAL_TEXTFIELD:
      return new FormControl(initialValue, Validators.required);
    case GLOBAL_CHOICE:
      return new FormControl(initialValue, Validators.required);
    case GLOBAL_BUTTON:
      return new FormControl(initialValue === 'true');
    case GLOBAL_NUMBER:
      return new FormControl(initialValue, [
        Validators.required,
        Validators.pattern('^[0-9]*$'),
      ]);
    default:
      return new FormControl(initialValue, Validators.required);
  }
}

export function formatFieldName(fieldName: string): string {
  return fieldName.replace('[0]', '').replace(/_/g, ' ');
}

export function getFieldType(fieldType: string): string {
  switch (fieldType) {
    case GLOBAL_TEXTFIELD:
      return 'text';
    case GLOBAL_NUMBER:
      return 'number';
    case GLOBAL_CHOICE:
      return 'select';
    case GLOBAL_BUTTON:
      return 'checkbox';
    default:
      return 'text';
  }
}
