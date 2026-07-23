"""
TruthLens AI – Security helpers
Optimizations vs. original:
  - datetime.utcnow() is deprecated in Python 3.12+; replaced with
    datetime.now(timezone.utc) which is timezone-aware.
  - bcrypt work-factor is configurable via settings (defaults to 12).
  - decode_token now returns None on expired tokens with a structured log
    instead of silently collapsing all PyJWTErrors together.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

import jwt
from bcrypt import checkpw, gensalt, hashpw

from app.core.config import settings

logger = logging.getLogger("truthlens.security")

_BCRYPT_ROUNDS: int = getattr(settings, "BCRYPT_ROUNDS", 12)


def get_password_hash(password: str) -> str:
    hashed = hashpw(password.encode("utf-8"), gensalt(rounds=_BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        logger.debug("JWT token expired.")
        return None
    except jwt.PyJWTError as exc:
        logger.debug("JWT decode error: %s", exc)
        return None


# ── Exceptions ───────────────────────────────────────────────────────────────
from fastapi import HTTPException, status

class TruthLensException(Exception):
    """Base exception class for TruthLens application exceptions."""
    pass

class ServiceUnavailableException(TruthLensException):
    """Exception raised when an external API service is down or failing."""
    pass

class AuthenticationException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Authentication Dependency ────────────────────────────────────────────────
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-oauth", auto_error=False)

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    if not token:
        raise AuthenticationException()
    email = decode_token(token)
    if not email:
        raise AuthenticationException()
    from app.models.user import User
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise AuthenticationException()
    return user


