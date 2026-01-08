import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Workout,
  WorkoutCreate,
  WorkoutUpdate,
  WorkoutListResponse,
  WorkoutStats
} from '../models/workout.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class WorkoutService {
  private apiUrl = `${environment.apiUrl}/workouts`;

  constructor(private http: HttpClient) {}

  getList(
    page: number = 1,
    pageSize: number = 20,
    workoutType?: string,
    startDate?: string,
    endDate?: string
  ): Observable<WorkoutListResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());

    if (workoutType) {
      params = params.set('workout_type', workoutType);
    }
    if (startDate) {
      params = params.set('start_date', startDate);
    }
    if (endDate) {
      params = params.set('end_date', endDate);
    }

    return this.http.get<WorkoutListResponse>(this.apiUrl, { params });
  }

  getById(id: string): Observable<Workout> {
    return this.http.get<Workout>(`${this.apiUrl}/${id}`);
  }

  create(data: WorkoutCreate): Observable<Workout> {
    return this.http.post<Workout>(this.apiUrl, data);
  }

  update(id: string, data: WorkoutUpdate): Observable<Workout> {
    return this.http.put<Workout>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  getStats(days: number = 30, workoutType?: string): Observable<WorkoutStats> {
    let params = new HttpParams().set('days', days.toString());

    if (workoutType) {
      params = params.set('workout_type', workoutType);
    }

    return this.http.get<WorkoutStats>(`${this.apiUrl}/stats`, { params });
  }
}
