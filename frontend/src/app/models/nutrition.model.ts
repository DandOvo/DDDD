export interface Nutrition {
  id: string;
  userId: string;
  mealType: string;
  foodName: string;
  calories: number;
  protein?: number;
  carbohydrates?: number;
  fat?: number;
  portion?: string;
  notes?: string;
  recordedAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface NutritionCreate {
  mealType: string;
  foodName: string;
  calories: number;
  protein?: number;
  carbohydrates?: number;
  fat?: number;
  portion?: string;
  notes?: string;
  recordedAt: Date;
}

export interface NutritionUpdate {
  mealType?: string;
  foodName?: string;
  calories?: number;
  protein?: number;
  carbohydrates?: number;
  fat?: number;
  portion?: string;
  notes?: string;
  recordedAt?: Date;
}

export interface NutritionListResponse {
  items: Nutrition[];
  total: number;
  page: number;
  pageSize: number;
}

export interface NutritionStats {
  totalCalories: number;
  totalProtein: number;
  totalCarbohydrates: number;
  totalFat: number;
}
