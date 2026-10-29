"""
TruthLens AI – News Services and Verification Pipeline
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Final, Optional
from urllib.parse import urlparse

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.analysis import Analysis
from app.utils.helpers import cache
from app.services.trust_engine import trust_engine
from app.services.groq_service import groq_service
from app.services.url_scraper import is_url, scrape_article, build_claim_from_article

logger = logging.getLogger("truthlens.news_service")

# ── NewsAPI Configuration ──────────────────────────────────────────────────
_NEWS_API_URL: Final[str] = "https://newsapi.org/v2/everything"
_NEWS_PAGE_SIZE: Final[int] = 10
_NEWS_TIMEOUT: Final[float] = 8.0

# ── MediaStack Configuration ───────────────────────────────────────────────
_MEDIASTACK_URL: Final[str] = "http://api.mediastack.com/v1/news"
_MEDIASTACK_LIMIT: Final[int] = 5
_MEDIASTACK_TIMEOUT: Final[float] = 8.0

# ── GDELT Configuration ────────────────────────────────────────────────────
_GDELT_URL: Final[str] = "https://api.gdeltproject.org/api/v2/doc/doc"
_GDELT_MAX_RECORDS: Final[int] = 5
_GDELT_MAX_QUERY_LEN: Final[int] = 200
_GDELT_TIMEOUT: Final[float] = 8.0

_PROMPT_DESC_LIMIT = 120


# ── Helper function ────────────────────────────────────────────────────────
def _safe_truncate(text: str, max_len: int) -> str:
    """Truncate to max_len without breaking mid-word."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len].rsplit(" ", 1)[0]
    return truncated + "…"


def _extract_source(article: dict[str, Any]) -> str:
    """Return a non-empty source name, falling back to domain."""
    name = (article.get("source") or {}).get("name", "").strip()
    if name:
        return name
    url = article.get("url", "")
    try:
        return urlparse(url).hostname or "Unknown"
    except Exception:
        return "Unknown"


_MISINFO_KEYWORDS: frozenset[str] = frozenset([
    "cure", "cures", "hoax", "fake", "conspiracy", "secret", "hidden",
    "they don't want", "mainstream media", "suppressed", "banned",
    "miracle", "wake up", "deep state", "plandemic", "stolen",
    "chemtrail", "microchip", "5g", "poison", "toxic",
])
_CREDIBLE_KEYWORDS: frozenset[str] = frozenset([
    "nasa", "who", "cdc", "reuters", "bbc", "ap news", "published",
    "study", "research", "university", "official", "government",
    "peer-reviewed", "journal", "institute", "announced",
])


def _build_news_mock(query: str) -> list[dict[str, Any]]:
    """
    Content-aware mock news articles based on claim text analysis.
    Suspicious/misinformation claims → few articles with debunking titles.
    Credible claims → many corroborating sources.
    Ambiguous → small set with neutral framing.
    """
    q_lower = query.lower()
    misinfo_hits = sum(1 for kw in _MISINFO_KEYWORDS if kw in q_lower)
    credible_hits = sum(1 for kw in _CREDIBLE_KEYWORDS if kw in q_lower)

    # Strong misinformation signal
    if misinfo_hits >= 2:
        return [
            {
                "title": f"Fact Check FALSE: '{_safe_truncate(query, 60)}' — debunked by health experts",
                "source": "PolitiFact",
                "url": "https://www.politifact.com/factchecks/mock-debunk",
                "published_at": "2026-06-07T08:30:00Z",
                "description": "Verified health authorities and independent fact checkers have confirmed this claim is not supported by any clinical evidence.",
                "_mock": True,
            },
            {
                "title": "WHO warns: Viral claims circulating with no scientific basis",
                "source": "World Health Organization",
                "url": "https://www.who.int/emergencies/diseases/myth-busters",
                "published_at": "2026-06-06T12:00:00Z",
                "description": "The World Health Organization has issued a bulletin addressing viral misinformation spreading across social platforms.",
                "_mock": True,
            },
        ]

    # Strong credibility signal
    if credible_hits >= 2:
        return [
            {
                "title": f"Confirmed: {_safe_truncate(query, 60)}",
                "source": "Reuters",
                "url": "https://www.reuters.com/article/mock-confirmed",
                "published_at": "2026-06-08T10:00:00Z",
                "description": "Multiple independent outlets have corroborated this report with official documentation and expert commentary.",
                "_mock": True,
            },
            {
                "title": f"Experts verify accuracy of claim: '{_safe_truncate(query, 50)}'",
                "source": "AP News",
                "url": "https://apnews.com/article/mock-expert-verify",
                "published_at": "2026-06-07T14:00:00Z",
                "description": "Senior analysts and domain experts reviewed primary sources and found the claim to be well-supported.",
                "_mock": True,
            },
            {
                "title": "Independent analysis confirms authenticity of cited sources",
                "source": "BBC News",
                "url": "https://bbc.com/news/mock-confirmed",
                "published_at": "2026-06-06T09:00:00Z",
                "description": "BBC reporting teams have independently verified the key claims, matching with official records.",
                "_mock": True,
            },
            {
                "title": "Scientific community responds with supporting evidence",
                "source": "The Guardian",
                "url": "https://www.theguardian.com/science/mock-support",
                "published_at": "2026-06-05T16:00:00Z",
                "description": "Researchers have published supporting findings in peer-reviewed context, strengthening the credibility of this claim.",
                "_mock": True,
            },
        ]

    # Mild misinfo or ambiguous
    if misinfo_hits == 1:
        return [
            {
                "title": f"Questionable: Viral claim about '{_safe_truncate(query, 50)}' lacks evidence",
                "source": "Snopes",
                "url": "https://www.snopes.com/factchecks/mock",
                "published_at": "2026-06-07T11:00:00Z",
                "description": "Fact checkers found insufficient evidence to support this widely-shared claim. Context is missing.",
                "_mock": True,
            },
        ]

    # Neutral / default
    return [
        {
            "title": f"Reports emerging on: '{_safe_truncate(query, 55)}'",
            "source": "AP News",
            "url": "https://apnews.com/article/mock-general",
            "published_at": "2026-06-07T08:30:00Z",
            "description": f"Initial reports and analysis surrounding the topic: '{_safe_truncate(query, 80)}'.",
            "_mock": True,
            "_anomaly": "NEWS_API_KEY not configured — sandbox article.",
        },
        {
            "title": f"Analysis: Claims about '{_safe_truncate(query, 50)}' under review",
            "source": "Reuters",
            "url": "https://www.reuters.com/article/mock-review",
            "published_at": "2026-06-06T15:00:00Z",
            "description": "Media organizations are investigating and cross-referencing available source material on this topic.",
            "_mock": True,
        },
    ]


# ── Service Classes ─────────────────────────────────────────────────────────

class NewsApiService:
    def __init__(self) -> None:
        self.api_key = settings.NEWS_API_KEY
        self._client = httpx.AsyncClient(timeout=_NEWS_TIMEOUT)

    async def fetch_news(self, query: str) -> list[dict[str, Any]]:
        if not self.api_key:
            logger.warning("NEWS_API_KEY not set – NewsAPI running in content-aware mock mode.")
            return _build_news_mock(query)

        try:
            response = await self._client.get(
                _NEWS_API_URL,
                params={
                    "q": query,
                    "apiKey": self.api_key,
                    "pageSize": _NEWS_PAGE_SIZE,
                    "language": "en",
                    "sortBy": "relevancy",
                },
            )
            if response.status_code == 200:
                return [
                    {
                        "title": art.get("title", ""),
                        "source": _extract_source(art),
                        "url": art.get("url", ""),
                        "published_at": art.get("publishedAt", ""),
                        "description": art.get("description", ""),
                    }
                    for art in response.json().get("articles", [])
                ]

            logger.error(
                "NewsAPI status=%d body=%s", response.status_code, response.text[:200]
            )
            return []
        except Exception as exc:
            logger.error("NewsAPI error: %s", exc, exc_info=True)
            return []

    async def aclose(self) -> None:
        await self._client.aclose()


class MediaStackService:
    def __init__(self) -> None:
        self.api_key = settings.MEDIASTACK_API_KEY
        self._client = httpx.AsyncClient(timeout=_MEDIASTACK_TIMEOUT)

    async def fetch_news(self, query: str) -> list[dict[str, Any]]:
        if not self.api_key:
            logger.warning("MEDIASTACK_API_KEY not set – MediaStack running in mock mode.")
            return [
                {
                    "title": f"MediaStack Feed: Live reports on {query}",
                    "source": "BBC News",
                    "url": "https://www.bbc.com/news",
                    "published_at": "2026-06-08T09:15:00Z",
                    "description": (
                        "General reporting and media response surrounding public discussions "
                        "on this claim."
                    ),
                }
            ]

        try:
            response = await self._client.get(
                _MEDIASTACK_URL,
                params={
                    "access_key": self.api_key,
                    "keywords": query,
                    "limit": _MEDIASTACK_LIMIT,
                    "languages": "en",
                    "sort": "published_desc",
                },
            )
            if response.status_code == 200:
                return [
                    {
                        "title": art.get("title", ""),
                        "source": art.get("source", "") or "Unknown",
                        "url": art.get("url", ""),
                        "published_at": art.get("published_at", ""),
                        "description": art.get("description", ""),
                    }
                    for art in response.json().get("data", [])
                ]

            logger.error(
                "MediaStack API status=%d body=%s", response.status_code, response.text[:200]
            )
            return []
        except Exception as exc:
            logger.error("MediaStack API error: %s", exc, exc_info=True)
            return []

    async def aclose(self) -> None:
        await self._client.aclose()


class GdeltService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=_GDELT_TIMEOUT)

    async def search_articles(self, query: str) -> list[dict[str, Any]]:
        safe_query = _safe_truncate(query, _GDELT_MAX_QUERY_LEN)
        try:
            response = await self._client.get(
                _GDELT_URL,
                params={
                    "query": safe_query,
                    "mode": "artlist",
                    "format": "json",
                    "maxrecords": _GDELT_MAX_RECORDS,
                },
            )
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                return [
                    {
                        "title": art.get("title", ""),
                        "url": art.get("url", ""),
                        "source": art.get("source", ""),
                        "published_at": art.get("seendate", ""),
                        "description": art.get("language", ""),
                    }
                    for art in articles
                ]
            logger.warning("GDELT status=%d – using mock fallback.", response.status_code)
        except Exception as exc:
            logger.warning("GDELT error: %s – using mock fallback.", exc)

        return [
            {
                "title": f"Fact Check Analysis: Evaluating the claim '{_safe_truncate(query, 60)}'",
                "url": "https://example.org/gdelt-fact-report",
                "source": "Global Research Index",
                "published_at": "2026-06-08T12:00:00Z",
                "description": "English",
            }
        ]

    async def aclose(self) -> None:
        await self._client.aclose()


newsapi_service = NewsApiService()
mediastack_service = MediaStackService()
gdelt_service = GdeltService()


# ── Main Pipeline function ─────────────────────────────────────────────────

async def run_news_verification(
    claim: str, db: Session, user_id: Optional[int] = None
) -> Analysis:
    """Run the full news verification pipeline and persist results to DB."""

    cache_key = f"news_verify:{claim}"

    # ── 1. Cache check BEFORE creating a DB row ───────────────────────────────
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info("news_pipeline cache_hit claim=%r", claim[:60])
        analysis = Analysis(
            id=str(uuid.uuid4()),
            analysis_type="news",
            query=claim,
            status="completed",
            trust_score=cached_result["trust_score"],
            risk_level=cached_result["risk_level"],
            details=cached_result["details"],
            user_id=user_id,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    # ── 2. Create a "processing" DB row ───────────────────────────────────────
    analysis = Analysis(
        id=str(uuid.uuid4()),
        analysis_type="news",
        query=claim,
        status="processing",
        user_id=user_id,
    )
    db.add(analysis)
    db.commit()

    # Import locally to avoid circular dependency
    from app.services.factcheck_service import factcheck_service

    try:
        # ── 2b. URL detection + article scraping ────────────────────────
        url_context: dict | None = None
        effective_claim = claim
        if is_url(claim):
            logger.info("news_pipeline detected URL input, scraping article...")
            url_context = await scrape_article(claim)
            if url_context.get("scraped"):
                effective_claim = build_claim_from_article(url_context)
                logger.info("news_pipeline scraped title=%r", url_context.get("title", "")[:60])
            else:
                logger.warning("news_pipeline scrape failed: %s", url_context.get("error"))

        # ── 2c. Claim Decomposition (AI Upgrades Phase 6) ───────────────
        sub_claims = [effective_claim]
        if not url_context and len(effective_claim.split()) >= 8:
            logger.info("Complex claim detected, running AI decomposition...")
            decomposed = await groq_service.decompose_claim(effective_claim)
            if decomposed and isinstance(decomposed, list) and len(decomposed) > 0:
                sub_claims = decomposed
                logger.info("Decomposed into %d sub-claims", len(sub_claims))

        # ── 3. Parallel API fan-out ─────────────────────────────────────
        fact_check_tasks = [factcheck_service.check_claim(c) for c in sub_claims]
        
        results = await asyncio.gather(
            *fact_check_tasks,
            newsapi_service.fetch_news(effective_claim),
            mediastack_service.fetch_news(effective_claim),
            gdelt_service.search_articles(effective_claim),
        )
        
        fc_results = results[:len(sub_claims)]
        fact_checks = []
        for fc_list in fc_results:
            fact_checks.extend(fc_list)
            
        news_reports = results[-3]
        mediastack_reports = results[-2]
        gdelt_reports = results[-1]

        # Deduplicate by URL in O(n) using a set comprehension
        seen_urls: set[str] = set()
        all_news: list[dict] = []
        for art in (*news_reports, *mediastack_reports, *gdelt_reports):
            url = art.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_news.append(art)

        # ── 4. Trust scoring ─────────────────────────────────────────────
        scoring = trust_engine.calculate_news_score(
            fact_checks, all_news,
            claim=effective_claim,
            url_context=url_context,
        )

        # ── 5. LLM reasoning (Groq LLaMA) ─────────────────────────────────────
        prompt_articles = [
            {
                "title": art.get("title"),
                "source": art.get("source"),
                "desc": (art.get("description") or "")[:_PROMPT_DESC_LIMIT],
            }
            for art in all_news[:5]
        ]
        url_note = ""
        if url_context and url_context.get("scraped"):
            domain_label = url_context.get("domain_credibility", {}).get("label", "Unknown")
            url_note = (
                f"\nSOURCE ARTICLE: \"{url_context.get('title')}\"\n"
                f"Author: {url_context.get('author') or 'Not identified'} | "
                f"Domain: {url_context.get('domain')} ({domain_label})\n"
            )

        tone_note = ""
        tone = scoring.get("tone_analysis", {})
        if tone.get("overall_tone") and tone["overall_tone"] != "Neutral":
            tone_note = f"\nEMOTIONAL TONE ANALYSIS: {tone['overall_tone']} — {', '.join(tone.get('tone_labels', []))}\n"

        entities = scoring.get("entities", {})
        entity_note = ""
        if entities.get("organizations"):
            org_names = ", ".join(o["full_name"] for o in entities["organizations"][:3])
            entity_note = f"\nORGANIZATIONS CITED: {org_names}\n"

        conf_low = scoring.get("confidence_low", 0)
        conf_high = scoring.get("confidence_high", 100)

        prompt = (
            f'Claim to verify: "{effective_claim}"\n'
            f"{url_note}"
            f"{tone_note}"
            f"{entity_note}\n"
            f"FACT CHECK RECORDS FOUND:\n"
            f"{fact_checks if fact_checks else 'No direct fact checks found in Google database.'}\n\n"
            f"NEWS REPORTS FOUND:\n{prompt_articles}\n\n"
            f"TRUST METRICS:\n"
            f"Trust Score: {scoring['trust_score']}/100 (Confidence band: {conf_low}–{conf_high})\n"
            f"Risk Assessment Level: {scoring['risk_level']}\n"
            f"Detected anomalies: {scoring['deductions']}\n"
            f"Supporting findings: {scoring['bonuses']}\n\n"
            "Write a concise, professional fact-check assessment. Formulate clear bullet points "
            "outlining the truthfulness, context, and credibility. Keep it structured in markdown."
        )

        reasoning = await groq_service.generate_analysis(prompt)

        # ── 6. Build details payload ──────────────────────────────────────────
        details_payload = {
            "sub_claims": sub_claims if len(sub_claims) > 1 else None,
            "fact_checks": fact_checks,
            "news_reports": all_news,
            "url_context": url_context,
            "tone_analysis": scoring.get("tone_analysis"),
            "entities": scoring.get("entities"),
            "scoring_breakdown": {
                "deductions": scoring["deductions"],
                "bonuses": scoring["bonuses"],
            },
            "confidence": {
                "low": scoring.get("confidence_low"),
                "high": scoring.get("confidence_high"),
            },
            "ai_reasoning": reasoning,
            "is_mock": not (
                settings.GROQ_API_KEY and settings.GOOGLE_API_KEY and settings.NEWS_API_KEY
            ),
        }

        # ── 7. Persist & cache ────────────────────────────────────────────────
        analysis.status = "completed"
        analysis.trust_score = scoring["trust_score"]
        analysis.risk_level = scoring["risk_level"]
        analysis.details = details_payload
        db.commit()
        db.refresh(analysis)

        cache.set(
            cache_key,
            {
                "trust_score": analysis.trust_score,
                "risk_level": analysis.risk_level,
                "details": details_payload,
            },
            expire_seconds=3600 * 6,
        )

        logger.info(
            "news_pipeline completed claim=%r score=%.1f risk=%s",
            claim[:60],
            scoring["trust_score"],
            scoring["risk_level"],
        )
        return analysis

    except Exception as exc:
        logger.error("news_pipeline failed claim=%r error=%s", claim[:60], exc, exc_info=True)
        analysis.status = "failed"
        analysis.details = {"error": str(exc)}
        db.commit()
        return analysis
