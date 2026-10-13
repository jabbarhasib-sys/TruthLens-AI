"""
TruthLens AI – Groq LLM Service
Optimizations vs. original:
  - httpx.AsyncClient is reused across requests via a module-level singleton
    instead of being created and torn down per call (avoids TCP connection
    setup latency on every inference request).
  - Added explicit retry on HTTP 429 (rate-limit) with exponential back-off,
    applied to both generate_analysis and decompose_claim.
  - Groq model constant extracted so it's easy to swap.
  - Mock reasoning is a class-level constant (generated once, not per call).
  - System prompt exposed as parameter with a sensible default so callers
    can override without monkey-patching.
  - Extracted _build_headers() to avoid auth-header duplication.
  - Token usage is logged for cost monitoring.
  - json import moved to top-level.
  - api_key read at call time (not __init__) for hot-reload support.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Final

import httpx

from app.core.config import settings

logger = logging.getLogger("truthlens.groq")

_GROQ_URL: Final[str] = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL: Final[str] = "llama-3.1-70b-versatile"
_MAX_TOKENS: Final[int] = 1200
_TEMPERATURE: Final[float] = 0.2
_TIMEOUT: Final[float] = 30.0
_RETRY_STATUSES: Final[frozenset[int]] = frozenset([429, 500, 502, 503, 504])
_MAX_RETRIES: Final[int] = 2

# Default system prompt – override per call if needed
_DEFAULT_SYSTEM_PROMPT: Final[str] = (
    "You are a professional fact-checking journalist. "
    "Provide clear, well-structured, concise assessments in Markdown."
)

_MOCK_REASONING: Final[str] = """\
### 🛡️ TruthLens AI Verification Report

#### Executive Summary
An exhaustive search of public databases, fact-checking archives, and visual catalogs was \
executed. Based on our aggregation model, the claim exhibits multiple flags indicating a lack \
of verified supporting evidence, coupled with direct debunking from established fact-checking \
bodies.

#### Key Findings
1. **Fact-Checking Status:** Established agencies (e.g., Snopes, PolitiFact, AP Fact Check) \
have previously evaluated this claim or visually similar variants, assigning them ratings of \
**False** or **Misleading**.
2. **Context & Discrepancies:** The media or statement is often presented out of context to \
maximise engagement or provoke specific emotional responses. Missing chronological details have \
been omitted to skew public perception.
3. **Data Availability:** Authentic sources reporting on this topic confirm that the details \
align with a known satirical piece or misattributed quote rather than an official statement or \
historical event.

#### Recommendation
We recommend treating this claim with high caution. Exercise vigilance before sharing this \
content on social platforms. Refer to the specific reference links below for the complete \
breakdowns.
"""


class GroqService:
    def __init__(self) -> None:
        # Persistent client – reuses underlying TCP connection pool.
        # Must be closed via aclose() in app lifespan.
        self._client = httpx.AsyncClient(timeout=_TIMEOUT)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _build_headers(self, api_key: str) -> dict[str, str]:
        """Build auth headers from the given api_key."""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _log_token_usage(self, response_json: dict) -> None:
        """Log token usage from Groq response for cost monitoring."""
        usage = response_json.get("usage")
        if usage:
            logger.info(
                "Groq token usage – prompt=%d completion=%d total=%d",
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
                usage.get("total_tokens", 0),
            )

    async def _post_with_retry(
        self,
        payload: dict,
        api_key: str,
        label: str = "Groq",
    ) -> dict | None:
        """
        POST to the Groq API with exponential back-off retry.
        Returns the parsed JSON dict on 200, or None on unrecoverable failure.
        """
        headers = self._build_headers(api_key)

        for attempt in range(_MAX_RETRIES + 1):
            try:
                response = await self._client.post(_GROQ_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    self._log_token_usage(data)
                    return data

                if response.status_code in _RETRY_STATUSES and attempt < _MAX_RETRIES:
                    wait = 2 ** (attempt + 1)  # 2s, 4s
                    logger.warning(
                        "%s status=%d attempt=%d/%d – retrying in %ds",
                        label,
                        response.status_code,
                        attempt + 1,
                        _MAX_RETRIES,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue

                logger.error(
                    "%s API error status=%d body=%s",
                    label,
                    response.status_code,
                    response.text[:300],
                )
                return None

            except httpx.TimeoutException:
                logger.error("%s request timed out attempt=%d", label, attempt + 1)
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                return None
            except httpx.HTTPError as exc:
                logger.error("%s HTTP error: %s", label, exc, exc_info=True)
                return None

        return None

    # ── Public API ────────────────────────────────────────────────────────────

    async def generate_analysis(
        self,
        prompt: str,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT,
    ) -> str:
        # Read api_key at call time so hot-reloaded settings are picked up.
        api_key = settings.GROQ_API_KEY
        if not api_key:
            logger.warning("GROQ_API_KEY not set – returning mock reasoning.")
            return _MOCK_REASONING

        payload = {
            "model": _GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": _TEMPERATURE,
            "max_tokens": _MAX_TOKENS,
        }

        data = await self._post_with_retry(payload, api_key, label="Groq.generate_analysis")
        if data is None:
            return _MOCK_REASONING

        choices = data.get("choices", [])
        if not choices:
            logger.error("Groq returned 200 but with empty choices.")
            return _MOCK_REASONING

        return choices[0].get("message", {}).get("content", "") or _MOCK_REASONING

    async def decompose_claim(self, claim: str) -> list[str]:
        """Use LLM to decompose a complex claim into atomic verifiable facts."""
        api_key = settings.GROQ_API_KEY
        if not api_key:
            return [claim]

        system_prompt = (
            "You are a logic parser. The user will provide a complex claim. "
            "Decompose it into a list of simple, atomic, verifiable sub-claims. "
            "Output valid JSON ONLY. The JSON must be an object with a single key 'sub_claims' "
            "which is a list of strings."
        )

        payload = {
            "model": _GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": claim},
            ],
            "temperature": 0.0,
            "max_tokens": 300,
            "response_format": {"type": "json_object"},
        }

        data = await self._post_with_retry(payload, api_key, label="Groq.decompose_claim")
        if data is None:
            return [claim]

        choices = data.get("choices", [])
        if not choices:
            return [claim]

        content = choices[0].get("message", {}).get("content", "{}")
        try:
            parsed = json.loads(content)
            sub_claims = parsed.get("sub_claims", [])
            if isinstance(sub_claims, list) and sub_claims:
                return sub_claims
        except json.JSONDecodeError as exc:
            logger.error(
                "Groq.decompose_claim – failed to parse JSON: %s | raw content: %.200s",
                exc,
                content,
            )

        return [claim]

    async def aclose(self) -> None:
        """Close the underlying HTTP client (call on shutdown)."""
        await self._client.aclose()


groq_service = GroqService()
