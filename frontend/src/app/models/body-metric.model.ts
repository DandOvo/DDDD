export interface BodyMetric {
  id: string;
  userId: string;
  weight?: number;
  bodyFatPercentage?: number;
  muscleMass?: number;
  bmi?: number;
  notes?: string;
  recordedAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface BodyMetricCreate {
  weight?: number;
  bodyFatPercentage?: number;
  muscleMass?: number;
  notes?: string;
  recordedAt: Date;
}

export interface BodyMetricUpdate {
  weight?: number;
  bodyFatPercentage?: number;
  muscleMass?: number;
  notes?: string;
  recordedAt?: Date;
}

export interface BodyMetricListResponse {
  items: BodyMetric[];
  total: number;
  page: number;
  pageSize: number;
}

export interface BodyMetricStats {
  latestWeight?: number;
  averageWeight?: number;
  weightChange?: number;
  latestBmi?: number;
  latestBodyFat?: number;
}
