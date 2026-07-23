"""
TruthLens AI – Reports and History routes
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.security import get_current_user
from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.report import ReportResponse, HistoryResponse

router = APIRouter(tags=["reports"])

_TERMINAL_STATUSES = ("completed", "failed")


@router.get("/report/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == report_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification report not found."
        )
    return analysis


@router.get("/history", response_model=List[HistoryResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(default=0, ge=0, description="Records to skip"),
):
    analyses = (
        db.query(Analysis)
        .filter(
            Analysis.user_id == current_user.id,
            Analysis.status.in_(_TERMINAL_STATUSES),
        )
        .order_by(Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return analyses
