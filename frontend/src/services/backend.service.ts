import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

type PdfResponse = {
  status: string;
  processedData: string;
};

@Injectable({
  providedIn: 'root',
})
export class BackendService {
  private apiUrl = 'https://backend-api.com/process';

  constructor(private http: HttpClient) {}

  processPdfChunk(chunk: Uint8Array): Observable<PdfResponse> {
    return this.http.post<PdfResponse>(this.apiUrl, { data: chunk });
  }
}
