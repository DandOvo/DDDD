from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models import (
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse,
    WorkoutListResponse,
    WorkoutStats
)
from auth import get_current_user_id
from database import cosmos_db
from utils import calculate_calories_burned
from analytics import calculate_workout_stats, get_date_range
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout: WorkoutCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new workout record
    """
    try:
        # Calculate calories if not provided
        calories_burned = workout.calories_burned
        if not calories_burned:
            # Get user weight for calculation
            user = cosmos_db.get_user_by_id(user_id)
            weight_kg = user.get("profile", {}).get("weight", 70) if user else 70

            # Calculate duration in minutes
            duration_minutes = workout.duration // 60

            calories_burned = calculate_calories_burned(
                workout.workout_type,
                duration_minutes,
                weight_kg
            )

        # Create workout document
        workout_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        workout_doc = {
            "id": workout_id,
            "userId": user_id,
            "workoutType": workout.workout_type,
            "startTime": workout.start_time.isoformat() if isinstance(workout.start_time, datetime) else workout.start_time,
            "endTime": workout.end_time.isoformat() if isinstance(workout.end_time, datetime) else workout.end_time,
            "duration": workout.duration,
            "distance": workout.distance,
            "caloriesBurned": calories_burned,
            "intensity": workout.intensity,
            "notes": workout.notes,
            "createdAt": now,
            "updatedAt": now,
        }

        # Save to database
        created_workout = cosmos_db.create_workout(workout_doc)

        return WorkoutResponse(**created_workout)

    except Exception as e:
        logger.error(f"Failed to create workout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workout: {str(e)}",
        )


@router.get("", response_model=WorkoutListResponse)
async def get_workouts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    workout_type: Optional[str] = Query(None, description="Filter by workout type"),
    start_date: Optional[str] = Query(None, description="ISO format date"),
    end_date: Optional[str] = Query(None, description="ISO format date"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get paginated list of workouts with optional filtering
    """
    try:
        items, total = cosmos_db.get_user_workouts(
            user_id=user_id,
            page=page,
            page_size=page_size,
            workout_type=workout_type,
            start_date=start_date,
            end_date=end_date,
        )

        return WorkoutListResponse(
            items=[WorkoutResponse(**item) for item in items],
            total=total,
            page=page,
            pageSize=page_size,
        )

    except Exception as e:
        logger.error(f"Failed to get workouts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workouts: {str(e)}",
        )


@router.get("/stats", response_model=WorkoutStats)
async def get_workout_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    workout_type: Optional[str] = Query(None, description="Filter by workout type"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get statistics for workouts over a specified period
    """
    try:
        # Get date range
        start_date, end_date = get_date_range(days)

        # Get all workouts in the period
        items, _ = cosmos_db.get_user_workouts(
            user_id=user_id,
            page=1,
            page_size=1000,  # Get all records
            workout_type=workout_type,
            start_date=start_date,
            end_date=end_date,
        )

        # Calculate statistics
        stats = calculate_workout_stats(items)

        return WorkoutStats(**stats)

    except Exception as e:
        logger.error(f"Failed to get workout stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workout stats: {str(e)}",
        )


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific workout by ID
    """
    try:
        workout = cosmos_db.get_workout_by_id(workout_id, user_id)

        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout not found",
            )

        return WorkoutResponse(**workout)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workout: {str(e)}",
        )


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: str,
    workout_update: WorkoutUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Update a workout record
    """
    try:
        # Check if workout exists
        existing = cosmos_db.get_workout_by_id(workout_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout not found",
            )

        # Prepare updates
        updates = {}
        if workout_update.workout_type is not None:
            updates["workoutType"] = workout_update.workout_type
        if workout_update.start_time is not None:
            updates["startTime"] = workout_update.start_time.isoformat() if isinstance(workout_update.start_time, datetime) else workout_update.start_time
        if workout_update.end_time is not None:
            updates["endTime"] = workout_update.end_time.isoformat() if isinstance(workout_update.end_time, datetime) else workout_update.end_time
        if workout_update.duration is not None:
            updates["duration"] = workout_update.duration
        if workout_update.distance is not None:
            updates["distance"] = workout_update.distance
        if workout_update.calories_burned is not None:
            updates["caloriesBurned"] = workout_update.calories_burned
        if workout_update.intensity is not None:
            updates["intensity"] = workout_update.intensity
        if workout_update.notes is not None:
            updates["notes"] = workout_update.notes

        updates["updatedAt"] = datetime.utcnow().isoformat()

        # Update in database
        updated_workout = cosmos_db.update_workout(workout_id, user_id, updates)

        return WorkoutResponse(**updated_workout)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workout: {str(e)}",
        )


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a workout record
    """
    try:
        success = cosmos_db.delete_workout(workout_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workout: {str(e)}",
        )
