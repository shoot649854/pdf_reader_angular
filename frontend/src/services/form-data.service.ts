import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import type { PDFFieldType } from '../components/form-dialog/type';
import { Base_URL } from '../components/setting';

@Injectable({
  providedIn: 'root',
})
export class FormDataService {
  private backendUrl = `${Base_URL}/form`;

  constructor(private http: HttpClient) {}

  // Update form data on the backend
  updateFormData(updatedData: PDFFieldType[]): Observable<any> {
    return this.http
      .post(`${this.backendUrl}/update-form-data`, updatedData)
      .pipe(catchError(this.handleError));
  }

  // Handle HTTP errors
  private handleError(error: HttpErrorResponse) {
    console.error('An error occurred:', error.error);
    return throwError('Something went wrong; please try again later.');
  }
}
