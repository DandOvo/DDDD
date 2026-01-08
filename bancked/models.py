from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# User Models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: str
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True


class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime


# Auth Models
class Token(BaseModel):
    token: str
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Body Metrics Models
class BodyMetricBase(BaseModel):
    weight: Optional[float] = Field(None, gt=0, description="Weight in kg")
    body_fat_percentage: Optional[float] = Field(None, alias="bodyFatPercentage", ge=0, le=100)
    muscle_mass: Optional[float] = Field(None, alias="muscleMass", gt=0, description="Muscle mass in kg")
    notes: Optional[str] = Field(None, max_length=500)


class BodyMetricCreate(BodyMetricBase):
    recorded_at: datetime = Field(alias="recordedAt")


class BodyMetricUpdate(BodyMetricBase):
    recorded_at: Optional[datetime] = Field(None, alias="recordedAt")


class BodyMetricResponse(BodyMetricBase):
    id: str
    user_id: str = Field(alias="userId")
    bmi: Optional[float] = None
    recorded_at: datetime = Field(alias="recordedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class BodyMetricListResponse(BaseModel):
    items: List[BodyMetricResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


# Workout Models
class WorkoutBase(BaseModel):
    workout_type: str = Field(..., alias="workoutType", description="Type: running, cycling, swimming, strength_training, yoga, etc.")
    duration: int = Field(..., gt=0, description="Duration in seconds")
    distance: Optional[float] = Field(None, gt=0, description="Distance in kilometers")
    calories_burned: Optional[int] = Field(None, alias="caloriesBurned", ge=0)
    intensity: Optional[str] = Field(None, description="Intensity: low, moderate, high")
    notes: Optional[str] = Field(None, max_length=500)


class WorkoutCreate(WorkoutBase):
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")


class WorkoutUpdate(WorkoutBase):
    workout_type: Optional[str] = Field(None, alias="workoutType")
    duration: Optional[int] = Field(None, gt=0)
    start_time: Optional[datetime] = Field(None, alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")


class WorkoutResponse(WorkoutBase):
    id: str
    user_id: str = Field(alias="userId")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class WorkoutListResponse(BaseModel):
    items: List[WorkoutResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


# Nutrition Models
class NutritionBase(BaseModel):
    meal_type: str = Field(..., alias="mealType", description="Type: breakfast, lunch, dinner, snack")
    food_name: str = Field(..., alias="foodName", max_length=200)
    calories: int = Field(..., ge=0)
    protein: Optional[float] = Field(None, ge=0, description="Protein in grams")
    carbohydrates: Optional[float] = Field(None, ge=0, description="Carbohydrates in grams")
    fat: Optional[float] = Field(None, ge=0, description="Fat in grams")
    portion: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class NutritionCreate(NutritionBase):
    recorded_at: datetime = Field(alias="recordedAt")


class NutritionUpdate(NutritionBase):
    meal_type: Optional[str] = Field(None, alias="mealType")
    food_name: Optional[str] = Field(None, alias="foodName")
    calories: Optional[int] = Field(None, ge=0)
    recorded_at: Optional[datetime] = Field(None, alias="recordedAt")


class NutritionResponse(NutritionBase):
    id: str
    user_id: str = Field(alias="userId")
    recorded_at: datetime = Field(alias="recordedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class NutritionListResponse(BaseModel):
    items: List[NutritionResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


# Progress Photo Models
class ProgressPhotoBase(BaseModel):
    photo_type: str = Field(..., alias="photoType", description="Type: front, side, back")
    notes: Optional[str] = Field(None, max_length=500)


class ProgressPhotoResponse(ProgressPhotoBase):
    id: str
    user_id: str = Field(alias="userId")
    file_name: str = Field(alias="fileName")
    original_file_name: str = Field(alias="originalFileName")
    media_type: str = Field(alias="mediaType")
    file_size: int = Field(alias="fileSize")
    mime_type: str = Field(alias="mimeType")
    blob_url: str = Field(alias="blobUrl")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    recorded_at: datetime = Field(alias="recordedAt")
    uploaded_at: datetime = Field(alias="uploadedAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class ProgressPhotoListResponse(BaseModel):
    items: List[ProgressPhotoResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


# Dashboard and Stats Models
class BodyMetricStats(BaseModel):
    latest_weight: Optional[float] = Field(None, alias="latestWeight")
    average_weight: Optional[float] = Field(None, alias="averageWeight")
    weight_change: Optional[float] = Field(None, alias="weightChange")
    latest_bmi: Optional[float] = Field(None, alias="latestBmi")
    latest_body_fat: Optional[float] = Field(None, alias="latestBodyFat")

    class Config:
        populate_by_name = True


class WorkoutStats(BaseModel):
    total_workouts: int = Field(alias="totalWorkouts")
    total_duration: int = Field(alias="totalDuration", description="Total duration in seconds")
    total_calories: int = Field(alias="totalCalories")
    total_distance: Optional[float] = Field(None, alias="totalDistance")

    class Config:
        populate_by_name = True


class NutritionStats(BaseModel):
    total_calories: int = Field(alias="totalCalories")
    total_protein: float = Field(alias="totalProtein")
    total_carbohydrates: float = Field(alias="totalCarbohydrates")
    total_fat: float = Field(alias="totalFat")

    class Config:
        populate_by_name = True


class DashboardOverview(BaseModel):
    body_metrics: Optional[BodyMetricStats] = Field(None, alias="bodyMetrics")
    workout_stats: Optional[WorkoutStats] = Field(None, alias="workoutStats")
    nutrition_stats: Optional[NutritionStats] = Field(None, alias="nutritionStats")
    total_progress_photos: int = Field(alias="totalProgressPhotos")

    class Config:
        populate_by_name = True


# Error Models
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
