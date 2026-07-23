"""
TruthLens AI – General Utility Helpers & Cache
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Final, Optional

import redis

from app.core.config import settings

logger = logging.getLogger("truthlens.cache")

_MAX_MEMORY_ENTRIES: Final[int] = 500
_EVICT_FRACTION: Final[float] = 0.20  # Evict 20 % of entries on overflow


class CacheService:
    def __init__(self) -> None:
        self.redis_client: Optional[redis.Redis] = None
        self._mem: dict[str, dict[str, Any]] = {}  # {key: {"value": ..., "expiry": float|None}}

        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    socket_timeout=2.0,
                    decode_responses=True,  # strings, not bytes
                )
                self.redis_client.ping()
                logger.info("Connected to Redis at %s", settings.REDIS_URL)
            except Exception as exc:
                logger.warning("Redis unavailable (%s) – falling back to in-memory cache.", exc)
                self.redis_client = None
        else:
            logger.info("No REDIS_URL configured – using in-memory cache.")

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, key: str) -> Optional[Any]:
        if self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val is not None:
                    return json.loads(val)
            except Exception as exc:
                logger.warning("Redis GET failed (%s) – trying in-memory.", exc)

        return self._mem_get(key)

    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        serialized = json.dumps(value)

        if self.redis_client:
            try:
                self.redis_client.set(key, serialized, ex=expire_seconds)
                return True
            except Exception as exc:
                logger.warning("Redis SET failed (%s) – falling back to in-memory.", exc)

        self._mem_set(key, value, expire_seconds)
        return True

    def delete(self, key: str) -> bool:
        deleted = False
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                deleted = True
            except Exception as exc:
                logger.warning("Redis DELETE failed: %s", exc)

        if key in self._mem:
            del self._mem[key]
            deleted = True
        return deleted

    # ── In-memory helpers ─────────────────────────────────────────────────────

    def _mem_get(self, key: str) -> Optional[Any]:
        entry = self._mem.get(key)
        if entry is None:
            return None
        if entry["expiry"] is not None and entry["expiry"] <= time.monotonic():
            del self._mem[key]
            return None
        return entry["value"]

    def _mem_set(self, key: str, value: Any, expire_seconds: int) -> None:
        # Evict oldest entries if over the soft limit
        if len(self._mem) >= _MAX_MEMORY_ENTRIES:
            self._evict()

        self._mem[key] = {
            "value": value,
            "expiry": time.monotonic() + expire_seconds if expire_seconds else None,
        }

    def _evict(self) -> None:
        """Remove the oldest 20 % of entries (by insertion order, Python 3.7+)."""
        now = time.monotonic()
        # First, try to remove already-expired keys
        expired = [k for k, v in self._mem.items() if v["expiry"] and v["expiry"] <= now]
        for k in expired:
            del self._mem[k]

        # If still over limit, remove oldest by insertion order
        if len(self._mem) >= _MAX_MEMORY_ENTRIES:
            evict_count = max(1, int(len(self._mem) * _EVICT_FRACTION))
            for k in list(self._mem.keys())[:evict_count]:
                del self._mem[k]


cache = CacheService()
