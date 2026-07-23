from fastapi import APIRouter
from app.core.config import settings
from app.utils.helpers import cache

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check():
    redis_status = "connected" if cache.redis_client else "using_in_memory_fallback"
    
    # Check what key configurations are active
    active_integrations = {
        "groq": settings.GROQ_API_KEY is not None,
        "google_search": settings.GOOGLE_API_KEY is not None,
        "newsapi": settings.NEWS_API_KEY is not None,
        "mediastack": settings.MEDIASTACK_API_KEY is not None,
        "hive_deepfake": settings.HIVE_API_KEY is not None,
    }
    
    return {
        "status": "healthy",
        "cache": redis_status,
        "active_integrations": active_integrations
    }
