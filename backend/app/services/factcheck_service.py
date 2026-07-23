"""
TruthLens AI – Google Fact Check Service
"""
from __future__ import annotations

import logging
from typing import Any, Final

import httpx

from app.core.config import settings

logger = logging.getLogger("truthlens.factcheck")

_FACT_CHECK_URL: Final[str] = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
_TIMEOUT: Final[float] = 10.0

# Pre-built mock responses keyed by keyword frozenset
_MOCK_RULES: list[tuple[frozenset[str], list[dict[str, Any]]]] = [
    (
        frozenset(["alien", "ufo", "area 51"]),
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
        frozenset(["vaccine", "health", "covid", "magnetic"]),
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
        self.api_key = settings.GOOGLE_API_KEY
        self._client = httpx.AsyncClient(timeout=_TIMEOUT)

    def _get_mock_response(self, claim: str) -> list[dict[str, Any]]:
        """Return a relevant mock response based on keyword matching."""
        claim_words = frozenset(claim.lower().split())
        for keywords, mock_data in _MOCK_RULES:
            if keywords & claim_words:  # frozenset intersection
                return mock_data
        # No keyword match — return the generic structured sandbox response
        return _GENERIC_MOCK

    async def check_claim(self, claim: str) -> list[dict[str, Any]]:
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set – Google Fact Check running in mock mode.")
            return self._get_mock_response(claim)

        try:
            response = await self._client.get(
                _FACT_CHECK_URL,
                params={"query": claim, "key": self.api_key, "languageCode": "en"},
            )
            if response.status_code == 200:
                return response.json().get("claims", [])
            logger.error(
                "Google Fact Check API status=%d body=%s",
                response.status_code,
                response.text[:200],
            )
            return []
        except Exception as exc:
            logger.error("Google Fact Check API error: %s", exc, exc_info=True)
            return []

    async def aclose(self) -> None:
        await self._client.aclose()


factcheck_service = FactcheckService()
