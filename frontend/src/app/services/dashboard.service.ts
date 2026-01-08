import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DashboardOverview } from '../models/dashboard.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = `${environment.apiUrl}/dashboard`;

  constructor(private http: HttpClient) {}

  getOverview(days: number = 30): Observable<DashboardOverview> {
    const params = new HttpParams().set('days', days.toString());
    return this.http.get<DashboardOverview>(`${this.apiUrl}/overview`, { params });
  }
}
