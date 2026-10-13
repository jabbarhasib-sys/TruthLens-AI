"""
TruthLens AI – Google Fact Check Service
"""
from __future__ import annotations

import asyncio
import copy
import logging
from typing import Any, Final

import httpx

from app.core.config import settings

logger = logging.getLogger("truthlens.factcheck")

_FACT_CHECK_URL: Final[str] = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
_TIMEOUT: Final[float] = 10.0
_LANGUAGE_CODE: Final[str] = "en"
_PAGE_SIZE: Final[int] = 10
_MAX_RETRIES: Final[int] = 2
_RETRY_STATUSES: Final[frozenset[int]] = frozenset([429, 500, 502, 503, 504])

# ---------------------------------------------------------------------------
# Mock data – stored as read-only templates; always deep-copied before return
# ---------------------------------------------------------------------------

# Each entry is (keyword_substrings, mock_data).
# Using substring matching (via `any(k in claim_lower for k in keywords)`)
# instead of word-split frozensets so multi-word phrases like "area 51" match.
_MOCK_RULES: list[tuple[tuple[str, ...], list[dict[str, Any]]]] = [
    (
        ("alien", "ufo", "area 51"),
        [
            {
                "claimText": "NASA confirmed alien spaceships have landed in Area 51.",
                "claimant": "Social Media Posts",
                "claimDate": "2026-05-15T00:00:00Z",
                "_mock": True,
                "_anomaly": "GOOGLE_API_KEY not configured — returned from keyword-matched sandbox data.",
                "claimReview": [
                    {
                        "publisher": {"name": "PolitiFact", "site": "politifact.com"},
                        "url": "https://www.politifact.com/factchecks/alien-landing-hoax/",
                        "textualRating": "False",
                        "languageCode": "en",
                    }
                ],
            }
        ],
    ),
    (
        ("vaccine", "covid", "magnetic"),
        [
            {
                "claimText": "Vaccines make you magnetic.",
                "claimant": "TikTok Video",
                "claimDate": "2026-06-01T00:00:00Z",
                "_mock": True,
                "_anomaly": "GOOGLE_API_KEY not configured — returned from keyword-matched sandbox data.",
                "claimReview": [
                    {
                        "publisher": {"name": "Snopes", "site": "snopes.com"},
                        "url": "https://www.snopes.com/factchecks/magnetic-vaccines/",
                        "textualRating": "False",
                        "languageCode": "en",
                    }
                ],
            }
        ],
    ),
]

# Generic structured fallback — used when no keyword matches
_GENERIC_MOCK: list[dict[str, Any]] = [
    {
        "claimText": "Claim could not be verified against the live Google Fact Check database.",
        "claimant": "TruthLens AI Sandbox",
        "claimDate": "2026-06-10T00:00:00Z",
        "_mock": True,
        "_anomaly": "GOOGLE_API_KEY not configured — configure it in .env to enable live fact checking.",
        "claimReview": [
            {
                "publisher": {"name": "TruthLens AI (Sandbox)", "site": "truthlens.ai"},
                "url": "#",
                "textualRating": "Unverified",
                "languageCode": "en",
            }
        ],
    }
]


class FactcheckService:
    def __init__(self) -> None:
        # Use a persistent async client – reuses underlying TCP connection pool.
        # Instantiated here; must be closed via aclose() in app lifespan.
        self._client = httpx.AsyncClient(timeout=_TIMEOUT)

    def _get_mock_response(self, claim: str) -> list[dict[str, Any]]:
        """Return a deep-copied relevant mock response based on substring matching."""
        claim_lower = claim.lower()
        for keywords, mock_data in _MOCK_RULES:
            if any(k in claim_lower for k in keywords):
                return copy.deepcopy(mock_data)
        return copy.deepcopy(_GENERIC_MOCK)

    async def check_claim(self, claim: str) -> list[dict[str, Any]]:
        # Read api_key at call time so hot-reloaded settings are picked up.
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set – Google Fact Check running in mock mode.")
            return self._get_mock_response(claim)

        params = {
            "query": claim,
            "key": api_key,
            "languageCode": _LANGUAGE_CODE,
            "pageSize": _PAGE_SIZE,
        }

        for attempt in range(_MAX_RETRIES + 1):
            try:
                response = await self._client.get(_FACT_CHECK_URL, params=params)

                if response.status_code == 200:
                    return response.json().get("claims", [])

                if response.status_code in _RETRY_STATUSES and attempt < _MAX_RETRIES:
                    wait = 2 ** attempt
                    logger.warning(
                        "Google Fact Check status=%d attempt=%d/%d – retrying in %ds",
                        response.status_code,
                        attempt + 1,
                        _MAX_RETRIES,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue

                logger.error(
                    "Google Fact Check API status=%d body=%s",
                    response.status_code,
                    response.text[:200],
                )
                return []

            except httpx.TimeoutException:
                logger.error("Google Fact Check request timed out attempt=%d", attempt + 1)
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return []
            except httpx.HTTPError as exc:
                logger.error("Google Fact Check HTTP error: %s", exc, exc_info=True)
                return []

        return []

    async def aclose(self) -> None:
        await self._client.aclose()


factcheck_service = FactcheckService()
