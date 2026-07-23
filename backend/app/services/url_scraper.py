"""
TruthLens AI – URL Article Scraper
Extracts article metadata (title, author, domain, publish date) from a URL
and checks the domain against a known fake-news/low-credibility domain list.
Uses only the stdlib + httpx (already a project dependency).
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

logger = logging.getLogger("truthlens.url_scraper")

_TIMEOUT: float = 10.0

# ── Known low-credibility / fake-news domains (partial list) ─────────────────
# Source: Media Bias/Fact Check, NewsGuard, MIT Media Lab
_FAKE_NEWS_DOMAINS: frozenset[str] = frozenset([
    "infowars.com", "naturalnews.com", "beforeitsnews.com", "yournewswire.com",
    "newspunch.com", "worldnewsdailyreport.com", "empirenews.net", "abcnews.com.co",
    "nationalreport.net", "theonion.com", "clickhole.com", "babylonbee.com",
    "thelastlineofdefense.org", "americasfreedomfighters.com",
    "conservativedailypost.com", "thedailyfeed.co", "usapoliticstoday.com",
    "breakingburgh.com", "denverguardian.com", "bostonleader.com",
    "proudcons.com", "patriotpost.us", "100percentfedup.com",
    "pamelageller.com", "wnd.com", "dcclothesline.com", "gellerreport.com",
    "freedomoutpost.com", "redflagnews.com", "veteranstoday.com",
    "21stcenturywire.com", "globalresearch.ca", "activistpost.com",
    "zerohedge.com", "breitbart.com", "thegatewaypundit.com",
])

# High-credibility domains
_TRUSTED_DOMAINS: frozenset[str] = frozenset([
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    "economist.com", "ft.com", "wsj.com", "bloomberg.com",
    "npr.org", "pbs.org", "cnn.com", "nbcnews.com", "cbsnews.com",
    "abcnews.go.com", "time.com", "wired.com", "scientificamerican.com",
    "nature.com", "science.org", "who.int", "cdc.gov", "nasa.gov",
    "snopes.com", "factcheck.org", "politifact.com", "fullfact.org",
])

# HTML tag stripper
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Meta tag patterns (order matters — more specific first)
_TITLE_PATTERNS: list[re.Pattern] = [
    re.compile(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', re.I | re.S),
    re.compile(r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:title["\']', re.I | re.S),
    re.compile(r'<meta\s+name=["\']twitter:title["\']\s+content=["\'](.*?)["\']', re.I | re.S),
    re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S),
]
_DESC_PATTERNS: list[re.Pattern] = [
    re.compile(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', re.I | re.S),
    re.compile(r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:description["\']', re.I | re.S),
    re.compile(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', re.I | re.S),
]
_AUTHOR_PATTERNS: list[re.Pattern] = [
    re.compile(r'<meta\s+name=["\']author["\']\s+content=["\'](.*?)["\']', re.I | re.S),
    re.compile(r'"author"\s*:\s*\{[^}]*"name"\s*:\s*["\'](.*?)["\']', re.I | re.S),
    re.compile(r'<meta\s+property=["\']article:author["\']\s+content=["\'](.*?)["\']', re.I | re.S),
    re.compile(r'rel=["\']author["\'][^>]*>\s*(.*?)\s*</', re.I | re.S),
]
_DATE_PATTERNS: list[re.Pattern] = [
    re.compile(r'<meta\s+property=["\']article:published_time["\']\s+content=["\'](.*?)["\']', re.I | re.S),
    re.compile(r'<meta\s+name=["\']publish[_-]?date["\']\s+content=["\'](.*?)["\']', re.I | re.S),
    re.compile(r'"datePublished"\s*:\s*["\'](.*?)["\']', re.I | re.S),
    re.compile(r'"publishedAt"\s*:\s*["\'](.*?)["\']', re.I | re.S),
]


def _first_match(patterns: list[re.Pattern], html: str) -> str:
    for pat in patterns:
        m = pat.search(html)
        if m:
            raw = m.group(1).strip()
            # Strip HTML tags and collapse whitespace
            clean = _WS_RE.sub(" ", _TAG_RE.sub("", raw)).strip()
            if clean:
                return clean[:500]
    return ""


def _get_domain_credibility(domain: str) -> dict[str, Any]:
    """Score domain credibility and return a structured assessment."""
    # Normalize: strip www.
    clean = domain.lower().removeprefix("www.")

    if clean in _FAKE_NEWS_DOMAINS:
        return {
            "rating": "LOW",
            "label": "Known Low-Credibility Source",
            "score_delta": -25,
            "color": "red",
        }
    if clean in _TRUSTED_DOMAINS:
        return {
            "rating": "HIGH",
            "label": "Established Trusted Outlet",
            "score_delta": +12,
            "color": "green",
        }
    # Unknown domain — check for red-flag TLD patterns
    if any(clean.endswith(tld) for tld in (".ru", ".cn", ".info", ".biz")):
        return {
            "rating": "UNKNOWN",
            "label": "Unverified Domain (Suspicious TLD)",
            "score_delta": -8,
            "color": "orange",
        }
    return {
        "rating": "UNKNOWN",
        "label": "Unverified Independent Source",
        "score_delta": -3,
        "color": "yellow",
    }


def is_url(text: str) -> bool:
    """Return True if text looks like a URL rather than a plain claim."""
    text = text.strip()
    try:
        result = urlparse(text)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


async def scrape_article(url: str) -> dict[str, Any]:
    """
    Fetch and parse an article URL.
    Returns structured metadata: title, description, author, published_at,
    domain, domain_credibility, and the extracted claim text.
    """
    parsed = urlparse(url)
    domain = parsed.netloc or url

    result: dict[str, Any] = {
        "url": url,
        "domain": domain,
        "title": "",
        "description": "",
        "author": "",
        "published_at": "",
        "platform_type": None,
        "domain_credibility": _get_domain_credibility(domain),
        "scraped": False,
        "error": None,
    }

    try:
        # Detect Social Media platforms
        if "twitter.com" in domain or "x.com" in domain:
            result["platform_type"] = "twitter"
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                oembed_url = f"https://publish.twitter.com/oembed?url={url}"
                response = await client.get(oembed_url)
                if response.status_code == 200:
                    data = response.json()
                    result["author"] = data.get("author_name", "")
                    # Extract text from HTML
                    raw_html = data.get("html", "")
                    clean_text = _WS_RE.sub(" ", _TAG_RE.sub("", raw_html)).strip()
                    # Twitter oEmbed includes the date at the end of the text block usually
                    result["description"] = clean_text[:500]
                    result["scraped"] = True
                    return result
                else:
                    result["error"] = f"Twitter oEmbed failed HTTP {response.status_code}"
                    return result

        if "youtube.com" in domain or "youtu.be" in domain:
            result["platform_type"] = "youtube"

        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; TruthLensBot/1.0; "
                        "+https://truthlens.ai/bot)"
                    ),
                    "Accept": "text/html,application/xhtml+xml",
                },
            )

        if response.status_code != 200:
            result["error"] = f"HTTP {response.status_code} from {domain}"
            return result

        html = response.text

        result["title"] = _first_match(_TITLE_PATTERNS, html)
        result["description"] = _first_match(_DESC_PATTERNS, html)
        result["author"] = _first_match(_AUTHOR_PATTERNS, html)
        result["published_at"] = _first_match(_DATE_PATTERNS, html)
        result["scraped"] = True

        logger.info(
            "url_scraper success domain=%r title=%r",
            domain,
            result["title"][:60] if result["title"] else "",
        )

    except httpx.TimeoutException:
        result["error"] = f"Request timed out fetching {domain}"
        logger.warning("url_scraper timeout url=%r", url)
    except Exception as exc:
        result["error"] = str(exc)
        logger.error("url_scraper error url=%r: %s", url, exc, exc_info=True)

    return result


def build_claim_from_article(article: dict[str, Any]) -> str:
    """
    Build a rich claim string from a scraped article to feed into the
    verification pipeline. Combines title + description for best recall.
    """
    parts = []
    if article.get("title"):
        parts.append(article["title"])
    if article.get("description"):
        parts.append(article["description"][:300])
    return " — ".join(parts) if parts else article.get("url", "")
