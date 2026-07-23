"""
TruthLens AI – Users & Admin API endpoints
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.security import get_current_user, get_password_hash, verify_password
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.common import UserResponse, UserUpdate, AdminUserUpdate

router = APIRouter(tags=["users"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_admin(current_user: User) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


# ── User Profile Endpoints ────────────────────────────────────────────────────

@router.get("/users/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's own profile."""
    return current_user


@router.patch("/users/me", response_model=UserResponse)
def update_my_profile(
    updates: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the authenticated user's profile fields."""
    if updates.full_name is not None:
        current_user.full_name = updates.full_name

    if updates.email is not None and updates.email != current_user.email:
        exists = db.query(User.id).filter(User.email == updates.email).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use.",
            )
        current_user.email = updates.email

    if updates.new_password:
        if not updates.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="current_password is required to set a new password.",
            )
        if not verify_password(updates.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect.",
            )
        current_user.hashed_password = get_password_hash(updates.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user


# ── Admin Endpoints ───────────────────────────────────────────────────────────

@router.get("/admin/users", response_model=List[UserResponse])
def admin_list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    role: Optional[str] = Query(default=None, description="Filter by role: user | admin"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
):
    """[Admin] List all users with optional filtering."""
    _require_admin(current_user)
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    return q.order_by(User.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/admin/users/{user_id}", response_model=UserResponse)
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """[Admin] Get a specific user by ID."""
    _require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/admin/users/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: int,
    updates: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """[Admin] Update a user's role, active status or full name."""
    _require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if updates.full_name is not None:
        user.full_name = updates.full_name
    if updates.role is not None:
        if updates.role not in ("user", "admin"):
            raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'.")
        user.role = updates.role
    if updates.is_active is not None:
        user.is_active = updates.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """[Admin] Delete a user account (cannot delete yourself)."""
    _require_admin(current_user)
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()


@router.get("/admin/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """[Admin] System-wide statistics."""
    _require_admin(current_user)
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.role == "admin").count()
    total_analyses = db.query(Analysis).count()
    completed_analyses = db.query(Analysis).filter(Analysis.status == "completed").count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "admin_users": admin_users,
        "total_analyses": total_analyses,
        "completed_analyses": completed_analyses,
        "pending_analyses": total_analyses - completed_analyses,
    }


@router.post("/admin/users/{user_id}/reset-password", response_model=UserResponse)
def admin_reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """[Admin] Reset a user's password to the default (123456)."""
    _require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.hashed_password = get_password_hash("123456")
    db.commit()
    db.refresh(user)
    return user
