from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


def validate_file_type(file: UploadFile) -> str:
    """
    Validate file type and return media type (image or video)
    """
    content_type = file.content_type.lower()

    if content_type in settings.allowed_image_types_list:
        return "image"
    elif content_type in settings.allowed_video_types_list:
        return "video"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{content_type}' is not allowed. Allowed types: {settings.allowed_image_types}, {settings.allowed_video_types}",
        )


def validate_file_size(file: UploadFile, max_size: int = None) -> int:
    """
    Validate file size and return size in bytes
    """
    if max_size is None:
        max_size = settings.max_file_size_bytes

    # Read file to get size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to beginning

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size ({max_size / (1024 * 1024):.0f} MB)",
        )

    return file_size


def generate_thumbnail(image_data: bytes, max_size: tuple = (300, 300)) -> Optional[bytes]:
    """
    Generate thumbnail from image data
    Returns thumbnail as bytes or None if failed
    """
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if necessary
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background

        # Generate thumbnail
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to bytes
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)

        return output.read()

    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


# Fitness calculation functions
def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate BMI (Body Mass Index)

    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters

    Returns:
        BMI value rounded to 1 decimal place
    """
    if weight_kg <= 0 or height_cm <= 0:
        return 0.0

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def calculate_calories_burned(
    workout_type: str,
    duration_minutes: int,
    weight_kg: float = 70.0
) -> int:
    """
    Estimate calories burned based on MET (Metabolic Equivalent of Task) values

    Args:
        workout_type: Type of workout (running, cycling, swimming, etc.)
        duration_minutes: Duration in minutes
        weight_kg: User weight in kilograms (default: 70)

    Returns:
        Estimated calories burned
    """
    # MET values for different workout types
    MET_VALUES = {
        'running': 9.8,
        'jogging': 7.0,
        'walking': 3.5,
        'cycling': 7.5,
        'swimming': 8.0,
        'strength_training': 6.0,
        'weightlifting': 6.0,
        'yoga': 3.0,
        'pilates': 3.5,
        'hiit': 10.0,
        'dancing': 5.0,
        'basketball': 6.5,
        'soccer': 7.0,
        'tennis': 7.3,
        'hiking': 6.0,
        'elliptical': 7.0,
        'rowing': 8.5,
        'climbing': 8.0,
    }

    # Get MET value for workout type (default to 5.0 if not found)
    met = MET_VALUES.get(workout_type.lower().replace(' ', '_'), 5.0)

    # Calories = MET * weight(kg) * time(hours)
    calories = met * weight_kg * (duration_minutes / 60)

    return int(round(calories))


def get_bmi_category(bmi: float) -> str:
    """
    Get BMI category based on WHO classification

    Args:
        bmi: BMI value

    Returns:
        Category string
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"
