"""
TruthLens AI – News verification route
Optimizations vs. original:
  - Optional JWT auth is wired correctly: the bearer token is parsed if
    present, but missing/invalid tokens are silently treated as anonymous
    (user_id=None) rather than raising a 401.
  - Claim length is validated server-side (max 2000 chars) to prevent
    unnecessarily long prompts from being sent to the LLM.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.news import NewsVerificationRequest
from app.schemas.report import ReportResponse
from app.services.news_service import run_news_verification

router = APIRouter(prefix="/verify", tags=["verify"])

_MAX_CLAIM_LEN = 2000

# auto_error=False means FastAPI won't 401 if the header is absent
_optional_bearer = OAuth2PasswordBearer(tokenUrl="/api/auth/login-oauth", auto_error=False)


def _get_optional_user(
    token: Optional[str] = Depends(_optional_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Returns the authenticated User or None for anonymous requests."""
    if not token:
        return None
    email = decode_token(token)
    if not email:
        return None
    return db.query(User).filter(User.email == email).first()


@router.post("/news", response_model=ReportResponse, status_code=status.HTTP_200_OK)
async def verify_news(
    request: NewsVerificationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(_get_optional_user),
):
    if len(request.claim) > _MAX_CLAIM_LEN:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Claim must not exceed {_MAX_CLAIM_LEN} characters.",
        )

    analysis = await run_news_verification(
        claim=request.claim,
        db=db,
        user_id=current_user.id if current_user else None,
    )
    return analysis
