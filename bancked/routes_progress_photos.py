from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form, Query
from typing import Optional
from models import ProgressPhotoResponse, ProgressPhotoListResponse
from auth import get_current_user_id
from database import cosmos_db
from storage import blob_storage
from utils import validate_file_type, validate_file_size, generate_thumbnail
from datetime import datetime
import uuid
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/progress-photos", tags=["Progress Photos"])


@router.post("", response_model=ProgressPhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_progress_photo(
    file: UploadFile = File(...),
    photo_type: str = Form(..., description="Photo type: front, side, or back"),
    recorded_at: str = Form(..., description="ISO format datetime when photo was taken"),
    notes: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user_id),
):
    """
    Upload a new progress photo
    """
    try:
        # Validate file type
        media_type = validate_file_type(file)

        # Only allow images for progress photos
        if media_type != "image":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed for progress photos",
            )

        # Validate file size
        file_size = validate_file_size(file)

        # Validate photo type
        if photo_type.lower() not in ["front", "side", "back"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Photo type must be one of: front, side, back",
            )

        # Read file content
        file_content = await file.read()
        await file.seek(0)

        # Generate file path with date folders
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        timestamp = now.strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = os.path.splitext(file.filename)[1]

        # Create blob name: {userId}/{year}/{month}/{timestamp}_{uuid}_{photoType}.ext
        blob_name = f"{user_id}/{year}/{month}/{timestamp}_{unique_id}_{photo_type.lower()}{file_extension}"

        # Upload to blob storage
        blob_url = blob_storage.upload_file(
            file.file, user_id, blob_name, file.content_type
        )[1]

        # Generate thumbnail
        thumbnail_url = None
        thumbnail_data = generate_thumbnail(file_content)
        if thumbnail_data:
            try:
                import io
                thumbnail_file = io.BytesIO(thumbnail_data)
                thumbnail_blob_name = f"{user_id}/{year}/{month}/thumb_{timestamp}_{unique_id}_{photo_type.lower()}.jpg"
                thumbnail_url = blob_storage.upload_file(
                    thumbnail_file,
                    user_id,
                    thumbnail_blob_name,
                    "image/jpeg",
                )[1]
            except Exception as e:
                logger.warning(f"Failed to upload thumbnail: {e}")

        # Create progress photo document
        photo_id = str(uuid.uuid4())
        now_iso = datetime.utcnow().isoformat()

        photo_doc = {
            "id": photo_id,
            "userId": user_id,
            "fileName": blob_name,
            "originalFileName": file.filename,
            "mediaType": media_type,
            "fileSize": file_size,
            "mimeType": file.content_type,
            "blobUrl": blob_url,
            "thumbnailUrl": thumbnail_url,
            "photoType": photo_type.lower(),
            "notes": notes,
            "recordedAt": recorded_at,
            "uploadedAt": now_iso,
            "updatedAt": now_iso,
        }

        # Save to database
        created_photo = cosmos_db.create_progress_photo(photo_doc)

        return ProgressPhotoResponse(**created_photo)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload progress photo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload progress photo: {str(e)}",
        )


@router.get("", response_model=ProgressPhotoListResponse)
async def get_progress_photos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    photo_type: Optional[str] = Query(None, description="Filter by photo type"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get paginated list of progress photos with optional filtering
    """
    try:
        items, total = cosmos_db.get_user_progress_photos(
            user_id=user_id,
            page=page,
            page_size=page_size,
            photo_type=photo_type,
        )

        return ProgressPhotoListResponse(
            items=[ProgressPhotoResponse(**item) for item in items],
            total=total,
            page=page,
            pageSize=page_size,
        )

    except Exception as e:
        logger.error(f"Failed to get progress photos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress photos: {str(e)}",
        )


@router.get("/{photo_id}", response_model=ProgressPhotoResponse)
async def get_progress_photo(
    photo_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific progress photo by ID
    """
    try:
        photo = cosmos_db.get_progress_photo_by_id(photo_id, user_id)

        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress photo not found",
            )

        return ProgressPhotoResponse(**photo)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get progress photo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress photo: {str(e)}",
        )


@router.put("/{photo_id}", response_model=ProgressPhotoResponse)
async def update_progress_photo(
    photo_id: str,
    photo_type: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    recorded_at: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update progress photo metadata
    """
    try:
        # Check if photo exists
        existing = cosmos_db.get_progress_photo_by_id(photo_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress photo not found",
            )

        # Prepare updates
        updates = {}
        if photo_type is not None:
            if photo_type.lower() not in ["front", "side", "back"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Photo type must be one of: front, side, back",
                )
            updates["photoType"] = photo_type.lower()

        if notes is not None:
            updates["notes"] = notes

        if recorded_at is not None:
            updates["recordedAt"] = recorded_at

        updates["updatedAt"] = datetime.utcnow().isoformat()

        # Update in database
        updated_photo = cosmos_db.update_progress_photo(photo_id, user_id, updates)

        return ProgressPhotoResponse(**updated_photo)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update progress photo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress photo: {str(e)}",
        )


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_progress_photo(
    photo_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a progress photo
    """
    try:
        # Get photo to retrieve file names
        photo = cosmos_db.get_progress_photo_by_id(photo_id, user_id)
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress photo not found",
            )

        # Delete from blob storage
        blob_name = photo.get("fileName")
        if blob_name:
            try:
                blob_storage.delete_file(blob_name)
            except Exception as e:
                logger.warning(f"Failed to delete blob file: {e}")

        # Delete thumbnail if exists
        thumbnail_blob = blob_name.replace(f"{user_id}/", f"{user_id}/thumb_") if blob_name else None
        if thumbnail_blob:
            try:
                blob_storage.delete_file(thumbnail_blob)
            except Exception as e:
                logger.warning(f"Failed to delete thumbnail: {e}")

        # Delete from database
        success = cosmos_db.delete_progress_photo(photo_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress photo not found",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete progress photo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete progress photo: {str(e)}",
        )
