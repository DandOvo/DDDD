import { BodyMetricStats } from './body-metric.model';
import { WorkoutStats } from './workout.model';
import { NutritionStats } from './nutrition.model';

export interface DashboardOverview {
  bodyMetrics?: BodyMetricStats;
  workoutStats?: WorkoutStats;
  nutritionStats?: NutritionStats;
  totalProgressPhotos: number;
}
