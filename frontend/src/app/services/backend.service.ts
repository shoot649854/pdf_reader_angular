import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class BackendService {
  private apiUrl = 'https://backend-api.com/process';

  constructor(private http: HttpClient) {}

  processPdfChunk(chunk: Uint8Array): Observable<any> {
    return this.http.post(this.apiUrl, { data: chunk });
  }
}
