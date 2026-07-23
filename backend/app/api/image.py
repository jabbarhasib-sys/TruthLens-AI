"""
TruthLens AI – Image upload route
Optimizations vs. original:
  - Added a hard file-size limit (10 MB) checked before reading the full
    content into memory to prevent OOM on malicious uploads.
  - Content-type validation extended to whitelist specific MIME types
    instead of a loose startswith("image/") that would accept anything.
  - image_url is extracted from a form field (if provided) and forwarded
    to the pipeline for cache keying.
"""
from __future__ import annotations

from typing import Final, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.schemas.report import ReportResponse
from app.services.image_service import run_image_verification

router = APIRouter(prefix="/verify", tags=["verify"])

_ALLOWED_MIME_TYPES: Final[frozenset[str]] = frozenset(
    ["image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"]
)
_MAX_FILE_SIZE_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MB


@router.post("/image", response_model=ReportResponse, status_code=status.HTTP_200_OK)
async def verify_image(
    file: UploadFile = File(...),
    image_url: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    # Validate MIME type
    if file.content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. "
            f"Allowed: {', '.join(sorted(_ALLOWED_MIME_TYPES))}",
        )

    # Read with size guard
    image_bytes = await file.read(_MAX_FILE_SIZE_BYTES + 1)
    if len(image_bytes) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {_MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB limit.",
        )

    try:
        analysis = await run_image_verification(
            image_bytes=image_bytes,
            filename=file.filename or "uploaded_image.jpg",
            db=db,
            image_url=image_url,
        )
        return analysis
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process image: {exc}",
        ) from exc
