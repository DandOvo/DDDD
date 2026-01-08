from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models import (
    NutritionCreate,
    NutritionUpdate,
    NutritionResponse,
    NutritionListResponse,
    NutritionStats
)
from auth import get_current_user_id
from database import cosmos_db
from analytics import calculate_nutrition_stats, get_date_range
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


@router.post("", response_model=NutritionResponse, status_code=status.HTTP_201_CREATED)
async def create_nutrition(
    nutrition: NutritionCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new nutrition record
    """
    try:
        # Create nutrition document
        nutrition_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        nutrition_doc = {
            "id": nutrition_id,
            "userId": user_id,
            "mealType": nutrition.meal_type,
            "foodName": nutrition.food_name,
            "calories": nutrition.calories,
            "protein": nutrition.protein,
            "carbohydrates": nutrition.carbohydrates,
            "fat": nutrition.fat,
            "portion": nutrition.portion,
            "notes": nutrition.notes,
            "recordedAt": nutrition.recorded_at.isoformat() if isinstance(nutrition.recorded_at, datetime) else nutrition.recorded_at,
            "createdAt": now,
            "updatedAt": now,
        }

        # Save to database
        created_nutrition = cosmos_db.create_nutrition(nutrition_doc)

        return NutritionResponse(**created_nutrition)

    except Exception as e:
        logger.error(f"Failed to create nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create nutrition: {str(e)}",
        )


@router.get("", response_model=NutritionListResponse)
async def get_nutrition(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = Query(None, description="ISO format date"),
    end_date: Optional[str] = Query(None, description="ISO format date"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get paginated list of nutrition records with optional date filtering
    """
    try:
        items, total = cosmos_db.get_user_nutrition(
            user_id=user_id,
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date,
        )

        return NutritionListResponse(
            items=[NutritionResponse(**item) for item in items],
            total=total,
            page=page,
            pageSize=page_size,
        )

    except Exception as e:
        logger.error(f"Failed to get nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nutrition: {str(e)}",
        )


@router.get("/stats", response_model=NutritionStats)
async def get_nutrition_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get nutrition statistics over a specified period
    """
    try:
        # Get date range
        start_date, end_date = get_date_range(days)

        # Get all nutrition records in the period
        items, _ = cosmos_db.get_user_nutrition(
            user_id=user_id,
            page=1,
            page_size=1000,  # Get all records
            start_date=start_date,
            end_date=end_date,
        )

        # Calculate statistics
        stats = calculate_nutrition_stats(items)

        return NutritionStats(**stats)

    except Exception as e:
        logger.error(f"Failed to get nutrition stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nutrition stats: {str(e)}",
        )


@router.get("/{nutrition_id}", response_model=NutritionResponse)
async def get_nutrition_by_id(
    nutrition_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific nutrition record by ID
    """
    try:
        nutrition = cosmos_db.get_nutrition_by_id(nutrition_id, user_id)

        if not nutrition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition record not found",
            )

        return NutritionResponse(**nutrition)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get nutrition: {str(e)}",
        )


@router.put("/{nutrition_id}", response_model=NutritionResponse)
async def update_nutrition(
    nutrition_id: str,
    nutrition_update: NutritionUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Update a nutrition record
    """
    try:
        # Check if nutrition exists
        existing = cosmos_db.get_nutrition_by_id(nutrition_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition record not found",
            )

        # Prepare updates
        updates = {}
        if nutrition_update.meal_type is not None:
            updates["mealType"] = nutrition_update.meal_type
        if nutrition_update.food_name is not None:
            updates["foodName"] = nutrition_update.food_name
        if nutrition_update.calories is not None:
            updates["calories"] = nutrition_update.calories
        if nutrition_update.protein is not None:
            updates["protein"] = nutrition_update.protein
        if nutrition_update.carbohydrates is not None:
            updates["carbohydrates"] = nutrition_update.carbohydrates
        if nutrition_update.fat is not None:
            updates["fat"] = nutrition_update.fat
        if nutrition_update.portion is not None:
            updates["portion"] = nutrition_update.portion
        if nutrition_update.notes is not None:
            updates["notes"] = nutrition_update.notes
        if nutrition_update.recorded_at is not None:
            updates["recordedAt"] = nutrition_update.recorded_at.isoformat() if isinstance(nutrition_update.recorded_at, datetime) else nutrition_update.recorded_at

        updates["updatedAt"] = datetime.utcnow().isoformat()

        # Update in database
        updated_nutrition = cosmos_db.update_nutrition(nutrition_id, user_id, updates)

        return NutritionResponse(**updated_nutrition)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update nutrition: {str(e)}",
        )


@router.delete("/{nutrition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nutrition(
    nutrition_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a nutrition record
    """
    try:
        success = cosmos_db.delete_nutrition(nutrition_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition record not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete nutrition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete nutrition: {str(e)}",
        )
