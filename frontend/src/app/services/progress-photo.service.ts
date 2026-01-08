import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ProgressPhoto, ProgressPhotoListResponse } from '../models/progress-photo.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProgressPhotoService {
  private apiUrl = `${environment.apiUrl}/progress-photos`;

  constructor(private http: HttpClient) {}

  getList(page: number = 1, pageSize: number = 20, photoType?: string): Observable<ProgressPhotoListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());

    if (photoType) {
      params = params.set('photo_type', photoType);
    }

    return this.http.get<ProgressPhotoListResponse>(this.apiUrl, { params });
  }

  getById(id: string): Observable<ProgressPhoto> {
    return this.http.get<ProgressPhoto>(`${this.apiUrl}/${id}`);
  }

  upload(file: File, photoType: string, recordedAt: Date, notes?: string): Observable<HttpEvent<ProgressPhoto>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('photo_type', photoType);
    formData.append('recorded_at', recordedAt.toISOString());
    if (notes) {
      formData.append('notes', notes);
    }

    return this.http.post<ProgressPhoto>(this.apiUrl, formData, {
      reportProgress: true,
      observe: 'events'
    });
  }

  update(id: string, photoType?: string, notes?: string, recordedAt?: Date): Observable<ProgressPhoto> {
    const formData = new FormData();
    if (photoType) {
      formData.append('photo_type', photoType);
    }
    if (notes) {
      formData.append('notes', notes);
    }
    if (recordedAt) {
      formData.append('recorded_at', recordedAt.toISOString());
    }

    return this.http.put<ProgressPhoto>(`${this.apiUrl}/${id}`, formData);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
