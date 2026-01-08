from fastapi import APIRouter, HTTPException, status, Depends, Query
from models import DashboardOverview
from auth import get_current_user_id
from database import cosmos_db
from analytics import (
    calculate_body_metrics_stats,
    calculate_workout_stats,
    calculate_nutrition_stats,
    get_date_range
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get dashboard overview with statistics from all modules
    """
    try:
        # Get date range
        start_date, end_date = get_date_range(days)

        # Get body metrics
        body_metrics_data, _ = cosmos_db.get_user_body_metrics(
            user_id=user_id,
            page=1,
            page_size=1000,
            start_date=start_date,
            end_date=end_date,
        )
        body_metrics_stats = calculate_body_metrics_stats(body_metrics_data)

        # Get workouts
        workouts_data, _ = cosmos_db.get_user_workouts(
            user_id=user_id,
            page=1,
            page_size=1000,
            start_date=start_date,
            end_date=end_date,
        )
        workout_stats = calculate_workout_stats(workouts_data)

        # Get nutrition
        nutrition_data, _ = cosmos_db.get_user_nutrition(
            user_id=user_id,
            page=1,
            page_size=1000,
            start_date=start_date,
            end_date=end_date,
        )
        nutrition_stats = calculate_nutrition_stats(nutrition_data)

        # Get total progress photos count
        _, total_photos = cosmos_db.get_user_progress_photos(
            user_id=user_id,
            page=1,
            page_size=1,
        )

        # Build overview response
        overview = {
            "bodyMetrics": body_metrics_stats,
            "workoutStats": workout_stats,
            "nutritionStats": nutrition_stats,
            "totalProgressPhotos": total_photos,
        }

        return DashboardOverview(**overview)

    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard overview: {str(e)}",
        )
