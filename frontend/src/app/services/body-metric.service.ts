import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  BodyMetric,
  BodyMetricCreate,
  BodyMetricUpdate,
  BodyMetricListResponse,
  BodyMetricStats
} from '../models/body-metric.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class BodyMetricService {
  private apiUrl = `${environment.apiUrl}/body-metrics`;

  constructor(private http: HttpClient) {}

  getList(page: number = 1, pageSize: number = 20, startDate?: string, endDate?: string): Observable<BodyMetricListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());

    if (startDate) {
      params = params.set('start_date', startDate);
    }
    if (endDate) {
      params = params.set('end_date', endDate);
    }

    return this.http.get<BodyMetricListResponse>(this.apiUrl, { params });
  }

  getById(id: string): Observable<BodyMetric> {
    return this.http.get<BodyMetric>(`${this.apiUrl}/${id}`);
  }

  create(data: BodyMetricCreate): Observable<BodyMetric> {
    return this.http.post<BodyMetric>(this.apiUrl, data);
  }

  update(id: string, data: BodyMetricUpdate): Observable<BodyMetric> {
    return this.http.put<BodyMetric>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  getStats(days: number = 30): Observable<BodyMetricStats> {
    const params = new HttpParams().set('days', days.toString());
    return this.http.get<BodyMetricStats>(`${this.apiUrl}/stats`, { params });
  }
}
