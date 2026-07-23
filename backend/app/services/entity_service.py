"""
TruthLens AI – Named Entity Extractor
Extracts persons, organizations, locations, and dates from claim text
using regex heuristics (no heavy NLP dependency required).
Also validates whether quotes are correctly attributed to known entities.
"""
from __future__ import annotations

import re
from typing import Any

# ── Known major organizations we can validate against ───────────────────────
_KNOWN_ORGS: dict[str, str] = {
    "WHO": "World Health Organization",
    "CDC": "Centers for Disease Control and Prevention",
    "NASA": "National Aeronautics and Space Administration",
    "FBI": "Federal Bureau of Investigation",
    "CIA": "Central Intelligence Agency",
    "NSA": "National Security Agency",
    "NIH": "National Institutes of Health",
    "FDA": "Food and Drug Administration",
    "FEMA": "Federal Emergency Management Agency",
    "UN": "United Nations",
    "EU": "European Union",
    "NATO": "North Atlantic Treaty Organization",
    "IMF": "International Monetary Fund",
    "WTO": "World Trade Organization",
    "UNICEF": "United Nations Children's Fund",
    "Reuters": "Reuters News Agency",
    "AP": "Associated Press",
    "BBC": "British Broadcasting Corporation",
    "NYT": "New York Times",
    "CNN": "Cable News Network",
}

# Patterns for entity extraction
_QUOTED_SPEECH_RE = re.compile(
    r'(?:(?:says?|said|according to|confirms?|announces?|reports?|admits?|warns?|claims?)\s+)'
    r'([A-Z][a-zA-Z\s\-]{2,40}?)(?:\s*[,:]|\s+(?:has|have|is|are|will|would|said|says))',
    re.I,
)
_DIRECT_QUOTE_RE = re.compile(
    r'["\u201c\u201d](.*?)["\u201c\u201d]\s*[-–—]\s*([A-Z][a-zA-Z\s\-]{2,40})',
)
_ORG_MENTION_RE = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in _KNOWN_ORGS) + r')\b'
)
_YEAR_RE = re.compile(r'\b(19\d{2}|20\d{2})\b')
_DATE_RE = re.compile(
    r'\b(?:January|February|March|April|May|June|July|August|September|'
    r'October|November|December)\s+\d{1,2},?\s+(?:19|20)\d{2}\b',
    re.I,
)
_PERCENTAGE_RE = re.compile(r'\b(\d+(?:\.\d+)?)\s*(?:%|percent)(?:\b|\s|$)', re.I)
_STATISTIC_RE = re.compile(
    r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion|trillion|thousand|people|deaths|cases|patients)\b',
    re.I,
)


def extract_entities(claim: str) -> dict[str, Any]:
    """
    Extract named entities and key data points from a claim string.
    Returns a structured dict with lists of found entities.
    """
    entities: dict[str, Any] = {
        "organizations": [],
        "quoted_sources": [],
        "years": [],
        "dates": [],
        "statistics": [],
        "attribution_warnings": [],
    }

    # 1. Known organization mentions
    org_matches = _ORG_MENTION_RE.findall(claim)
    if org_matches:
        entities["organizations"] = [
            {"abbr": m, "full_name": _KNOWN_ORGS[m]} for m in set(org_matches)
        ]

    # 2. Attribution / quoted sources
    speech_matches = _QUOTED_SPEECH_RE.findall(claim)
    quote_matches = _DIRECT_QUOTE_RE.findall(claim)
    all_sources = set()
    for m in speech_matches:
        name = m.strip().title()
        if len(name) > 2 and name not in all_sources:
            all_sources.add(name)
            entities["quoted_sources"].append({"name": name, "verified": False})
    for _, speaker in quote_matches:
        name = speaker.strip().title()
        if len(name) > 2 and name not in all_sources:
            all_sources.add(name)
            entities["quoted_sources"].append({"name": name, "verified": False})

    # 3. Years and dates
    entities["years"] = sorted(set(_YEAR_RE.findall(claim)))
    entities["dates"] = _DATE_RE.findall(claim)

    # 4. Statistics / percentages
    for m in _PERCENTAGE_RE.finditer(claim):
        entities["statistics"].append(f"{m.group(1)}%")
    for m in _STATISTIC_RE.finditer(claim):
        entities["statistics"].append(m.group(0).strip())

    # 5. Attribution warnings — known orgs mentioned with "confirms/says" language
    if entities["organizations"]:
        org_names = [o["abbr"] for o in entities["organizations"]]
        warning_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(o) for o in org_names) + r')\b'
            r'.{0,80}?(?:confirms?|says?|announces?|admits?|proves?|reveals?)',
            re.I | re.S,
        )
        if warning_pattern.search(claim):
            entities["attribution_warnings"].append(
                "Claim attributes a statement to a major organization. "
                "Verify the original press release or official communication."
            )

    return entities


def get_entity_score_delta(entities: dict[str, Any]) -> tuple[float, list[dict]]:
    """
    Calculate a score delta and signal list based on extracted entities.
    Returns (delta, signals_list).
    """
    delta = 0.0
    signals = []

    # Attribution warnings = mild deduction (unverified)
    if entities.get("attribution_warnings"):
        delta -= 8.0
        signals.append({
            "text": entities["attribution_warnings"][0],
            "url": "",
            "source": "Entity Attribution Check",
        })

    # Statistics present = claim is more specific (slightly more credible if sourced)
    if entities.get("statistics"):
        delta += 3.0
        signals.append({
            "text": f"Claim contains {len(entities['statistics'])} specific statistic(s): "
                    f"{', '.join(entities['statistics'][:3])}.",
            "url": "",
            "source": "Entity Extractor",
        })

    # Organizations mentioned = claim is verifiable (neutral-to-positive)
    if entities.get("organizations"):
        org_list = ", ".join(o["full_name"] for o in entities["organizations"][:3])
        signals.append({
            "text": f"Recognized organization(s) cited: {org_list}. Cross-reference official sources.",
            "url": "",
            "source": "Entity Extractor",
        })

    return delta, signals
