from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models import (
    BodyMetricCreate,
    BodyMetricUpdate,
    BodyMetricResponse,
    BodyMetricListResponse,
    BodyMetricStats
)
from auth import get_current_user_id
from database import cosmos_db
from utils import calculate_bmi
from analytics import calculate_body_metrics_stats, get_date_range
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/body-metrics", tags=["Body Metrics"])


@router.post("", response_model=BodyMetricResponse, status_code=status.HTTP_201_CREATED)
async def create_body_metric(
    metric: BodyMetricCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new body metric record
    """
    try:
        # Get user to retrieve height for BMI calculation
        user = cosmos_db.get_user_by_id(user_id)
        height_cm = user.get("profile", {}).get("height") if user else None

        # Calculate BMI if weight is provided and height is available
        bmi = None
        if metric.weight and height_cm:
            bmi = calculate_bmi(metric.weight, height_cm)

        # Create metric document
        metric_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        metric_doc = {
            "id": metric_id,
            "userId": user_id,
            "weight": metric.weight,
            "bodyFatPercentage": metric.body_fat_percentage,
            "muscleMass": metric.muscle_mass,
            "bmi": bmi,
            "notes": metric.notes,
            "recordedAt": metric.recorded_at.isoformat() if isinstance(metric.recorded_at, datetime) else metric.recorded_at,
            "createdAt": now,
            "updatedAt": now,
        }

        # Save to database
        created_metric = cosmos_db.create_body_metric(metric_doc)

        return BodyMetricResponse(**created_metric)

    except Exception as e:
        logger.error(f"Failed to create body metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create body metric: {str(e)}",
        )


@router.get("", response_model=BodyMetricListResponse)
async def get_body_metrics(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = Query(None, description="ISO format date"),
    end_date: Optional[str] = Query(None, description="ISO format date"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get paginated list of body metrics with optional date filtering
    """
    try:
        items, total = cosmos_db.get_user_body_metrics(
            user_id=user_id,
            page=page,
            page_size=page_size,
            start_date=start_date,
            end_date=end_date,
        )

        return BodyMetricListResponse(
            items=[BodyMetricResponse(**item) for item in items],
            total=total,
            page=page,
            pageSize=page_size,
        )

    except Exception as e:
        logger.error(f"Failed to get body metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get body metrics: {str(e)}",
        )


@router.get("/stats", response_model=BodyMetricStats)
async def get_body_metrics_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get statistics for body metrics over a specified period
    """
    try:
        # Get date range
        start_date, end_date = get_date_range(days)

        # Get all metrics in the period
        items, _ = cosmos_db.get_user_body_metrics(
            user_id=user_id,
            page=1,
            page_size=1000,  # Get all records
            start_date=start_date,
            end_date=end_date,
        )

        # Calculate statistics
        stats = calculate_body_metrics_stats(items)

        return BodyMetricStats(**stats)

    except Exception as e:
        logger.error(f"Failed to get body metrics stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get body metrics stats: {str(e)}",
        )


@router.get("/{metric_id}", response_model=BodyMetricResponse)
async def get_body_metric(
    metric_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific body metric by ID
    """
    try:
        metric = cosmos_db.get_body_metric_by_id(metric_id, user_id)

        if not metric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Body metric not found",
            )

        return BodyMetricResponse(**metric)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get body metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get body metric: {str(e)}",
        )


@router.put("/{metric_id}", response_model=BodyMetricResponse)
async def update_body_metric(
    metric_id: str,
    metric_update: BodyMetricUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Update a body metric record
    """
    try:
        # Check if metric exists
        existing = cosmos_db.get_body_metric_by_id(metric_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Body metric not found",
            )

        # Prepare updates
        updates = {}
        if metric_update.weight is not None:
            updates["weight"] = metric_update.weight
        if metric_update.body_fat_percentage is not None:
            updates["bodyFatPercentage"] = metric_update.body_fat_percentage
        if metric_update.muscle_mass is not None:
            updates["muscleMass"] = metric_update.muscle_mass
        if metric_update.notes is not None:
            updates["notes"] = metric_update.notes
        if metric_update.recorded_at is not None:
            updates["recordedAt"] = metric_update.recorded_at.isoformat() if isinstance(metric_update.recorded_at, datetime) else metric_update.recorded_at

        # Recalculate BMI if weight was updated
        if metric_update.weight is not None:
            user = cosmos_db.get_user_by_id(user_id)
            height_cm = user.get("profile", {}).get("height") if user else None
            if height_cm:
                updates["bmi"] = calculate_bmi(metric_update.weight, height_cm)

        updates["updatedAt"] = datetime.utcnow().isoformat()

        # Update in database
        updated_metric = cosmos_db.update_body_metric(metric_id, user_id, updates)

        return BodyMetricResponse(**updated_metric)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update body metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update body metric: {str(e)}",
        )


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_body_metric(
    metric_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a body metric record
    """
    try:
        success = cosmos_db.delete_body_metric(metric_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Body metric not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete body metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete body metric: {str(e)}",
        )
