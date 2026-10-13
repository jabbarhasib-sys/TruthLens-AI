from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.utils.helpers import cache

router = APIRouter(prefix="/health", tags=["health"])


# ── Response schema ───────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    cache: str
    active_integrations: dict[str, bool]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _check_redis() -> str:
    """
    Return a human-readable Redis status string.
    Performs an actual PING so we know the server is reachable,
    not just that a client object was constructed.
    """
    if cache.redis_client is None:
        return "using_in_memory_fallback"
    try:
        cache.redis_client.ping()
        return "connected"
    except Exception:
        return "unreachable"


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("", response_model=HealthResponse)
async def health_check() -> JSONResponse:
    """
    Liveness probe.

    Returns 200 when the process is up and all critical checks pass.
    Returns 503 when a critical dependency (e.g. Redis, if configured) is unreachable.

    For a Kubernetes-style readiness probe that also verifies DB connectivity,
    add a separate /health/ready endpoint.
    """
    redis_status = _check_redis()

    # Use bool() so an empty string is treated as unconfigured
    active_integrations = {
        "groq": bool(settings.GROQ_API_KEY),
        "google_search": bool(settings.GOOGLE_API_KEY),
        "newsapi": bool(settings.NEWS_API_KEY),
        "mediastack": bool(settings.MEDIASTACK_API_KEY),
        "hive_deepfake": bool(settings.HIVE_API_KEY),
    }

    payload = HealthResponse(
        status="healthy",
        version="1.0.0",
        cache=redis_status,
        active_integrations=active_integrations,
    )

    # Return 503 if Redis was explicitly configured but is now unreachable
    http_status = 503 if (settings.REDIS_URL and redis_status == "unreachable") else 200

    return JSONResponse(content=payload.model_dump(), status_code=http_status)
