import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Nutrition,
  NutritionCreate,
  NutritionUpdate,
  NutritionListResponse,
  NutritionStats
} from '../models/nutrition.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NutritionService {
  private apiUrl = `${environment.apiUrl}/nutrition`;

  constructor(private http: HttpClient) {}

  getList(page: number = 1, pageSize: number = 20, startDate?: string, endDate?: string): Observable<NutritionListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());

    if (startDate) {
      params = params.set('start_date', startDate);
    }
    if (endDate) {
      params = params.set('end_date', endDate);
    }

    return this.http.get<NutritionListResponse>(this.apiUrl, { params });
  }

  getById(id: string): Observable<Nutrition> {
    return this.http.get<Nutrition>(`${this.apiUrl}/${id}`);
  }

  create(data: NutritionCreate): Observable<Nutrition> {
    return this.http.post<Nutrition>(this.apiUrl, data);
  }

  update(id: string, data: NutritionUpdate): Observable<Nutrition> {
    return this.http.put<Nutrition>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  getStats(days: number = 30): Observable<NutritionStats> {
    const params = new HttpParams().set('days', days.toString());
    return this.http.get<NutritionStats>(`${this.apiUrl}/stats`, { params });
  }
}
