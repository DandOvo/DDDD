from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from statistics import mean, median
import logging

logger = logging.getLogger(__name__)


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for a list of values

    Args:
        values: List of numeric values

    Returns:
        Dictionary with min, max, average, median
    """
    if not values:
        return {
            "min": 0.0,
            "max": 0.0,
            "average": 0.0,
            "median": 0.0
        }

    return {
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "average": round(mean(values), 2),
        "median": round(median(values), 2)
    }


def calculate_change(old_value: Optional[float], new_value: Optional[float]) -> Dict[str, Any]:
    """
    Calculate absolute and percentage change between two values

    Args:
        old_value: Previous value
        new_value: Current value

    Returns:
        Dictionary with absolute change and percentage change
    """
    if old_value is None or new_value is None or old_value == 0:
        return {
            "absolute": 0.0,
            "percentage": 0.0
        }

    absolute_change = new_value - old_value
    percentage_change = (absolute_change / old_value) * 100

    return {
        "absolute": round(absolute_change, 2),
        "percentage": round(percentage_change, 2)
    }


def aggregate_by_period(
    data: List[Dict[str, Any]],
    date_field: str,
    value_field: str,
    period: str = "day"
) -> List[Dict[str, Any]]:
    """
    Aggregate data by time period

    Args:
        data: List of data records
        date_field: Field name containing the date
        value_field: Field name containing the value to aggregate
        period: Aggregation period ('day', 'week', 'month')

    Returns:
        List of aggregated data points
    """
    if not data:
        return []

    aggregated = {}

    for record in data:
        date_str = record.get(date_field)
        value = record.get(value_field)

        if not date_str or value is None:
            continue

        # Parse date
        if isinstance(date_str, str):
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date = date_str

        # Get period key
        if period == "day":
            key = date.strftime("%Y-%m-%d")
        elif period == "week":
            key = date.strftime("%Y-W%W")
        elif period == "month":
            key = date.strftime("%Y-%m")
        else:
            key = date.strftime("%Y-%m-%d")

        # Aggregate
        if key not in aggregated:
            aggregated[key] = {
                "period": key,
                "values": [],
                "count": 0
            }

        aggregated[key]["values"].append(value)
        aggregated[key]["count"] += 1

    # Calculate averages
    result = []
    for key in sorted(aggregated.keys()):
        data_point = aggregated[key]
        result.append({
            "period": data_point["period"],
            "average": round(mean(data_point["values"]), 2),
            "count": data_point["count"]
        })

    return result


def calculate_body_metrics_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for body metrics

    Args:
        records: List of body metric records

    Returns:
        Dictionary with statistics
    """
    if not records:
        return {
            "latest_weight": None,
            "average_weight": None,
            "weight_change": None,
            "latest_bmi": None,
            "latest_body_fat": None
        }

    # Sort by recorded date
    sorted_records = sorted(
        records,
        key=lambda x: x.get("recordedAt", ""),
        reverse=True
    )

    latest = sorted_records[0] if sorted_records else {}

    # Calculate averages
    weights = [r.get("weight") for r in records if r.get("weight")]
    body_fats = [r.get("bodyFatPercentage") for r in records if r.get("bodyFatPercentage")]

    # Calculate weight change (latest vs oldest)
    weight_change = None
    if len(sorted_records) >= 2 and sorted_records[0].get("weight") and sorted_records[-1].get("weight"):
        weight_change = calculate_change(
            sorted_records[-1].get("weight"),
            sorted_records[0].get("weight")
        )["absolute"]

    return {
        "latest_weight": latest.get("weight"),
        "average_weight": round(mean(weights), 1) if weights else None,
        "weight_change": weight_change,
        "latest_bmi": latest.get("bmi"),
        "latest_body_fat": latest.get("bodyFatPercentage")
    }


def calculate_workout_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for workouts

    Args:
        records: List of workout records

    Returns:
        Dictionary with statistics
    """
    if not records:
        return {
            "total_workouts": 0,
            "total_duration": 0,
            "total_calories": 0,
            "total_distance": None
        }

    total_duration = sum(r.get("duration", 0) for r in records)
    total_calories = sum(r.get("caloriesBurned", 0) for r in records)

    distances = [r.get("distance") for r in records if r.get("distance")]
    total_distance = sum(distances) if distances else None

    return {
        "total_workouts": len(records),
        "total_duration": total_duration,
        "total_calories": total_calories,
        "total_distance": round(total_distance, 2) if total_distance else None
    }


def calculate_nutrition_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for nutrition records

    Args:
        records: List of nutrition records

    Returns:
        Dictionary with statistics
    """
    if not records:
        return {
            "total_calories": 0,
            "total_protein": 0.0,
            "total_carbohydrates": 0.0,
            "total_fat": 0.0
        }

    total_calories = sum(r.get("calories", 0) for r in records)
    total_protein = sum(r.get("protein", 0) for r in records)
    total_carbs = sum(r.get("carbohydrates", 0) for r in records)
    total_fat = sum(r.get("fat", 0) for r in records)

    return {
        "total_calories": total_calories,
        "total_protein": round(total_protein, 1),
        "total_carbohydrates": round(total_carbs, 1),
        "total_fat": round(total_fat, 1)
    }


def get_date_range(days: int = 30) -> tuple[str, str]:
    """
    Get ISO formatted date range for the last N days

    Args:
        days: Number of days to look back

    Returns:
        Tuple of (start_date, end_date) in ISO format
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    return (
        start_date.isoformat() + "Z",
        end_date.isoformat() + "Z"
    )


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1h 30m")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
