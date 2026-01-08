export interface Workout {
  id: string;
  userId: string;
  workoutType: string;
  startTime: Date;
  endTime: Date;
  duration: number;
  distance?: number;
  caloriesBurned?: number;
  intensity?: string;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface WorkoutCreate {
  workoutType: string;
  startTime: Date;
  endTime: Date;
  duration: number;
  distance?: number;
  caloriesBurned?: number;
  intensity?: string;
  notes?: string;
}

export interface WorkoutUpdate {
  workoutType?: string;
  startTime?: Date;
  endTime?: Date;
  duration?: number;
  distance?: number;
  caloriesBurned?: number;
  intensity?: string;
  notes?: string;
}

export interface WorkoutListResponse {
  items: Workout[];
  total: number;
  page: number;
  pageSize: number;
}

export interface WorkoutStats {
  totalWorkouts: number;
  totalDuration: number;
  totalCalories: number;
  totalDistance?: number;
}
