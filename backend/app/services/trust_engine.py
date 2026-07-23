"""
TruthLens AI – Trust Engine v3
Calculates weighted trust scores (0–100) and risk levels for news claims and images.

v3 Additions:
  - Emotional tone analysis: fear/outrage/propaganda language detection.
  - Confidence intervals: score ± margin based on API signal consistency.
  - Named entity integration: org citations, statistics, attribution warnings.
  - URL domain credibility signal integration.
  - All previous v2 features retained.
"""
from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger("truthlens.trust_engine")

# ── Base scores ─────────────────────────────────────────────────────────────
_BASE_NEWS_SCORE: float = 50.0   # Start neutral — earn trust through evidence
_BASE_IMAGE_SCORE: float = 60.0  # Start neutral — earn trust through signals

# ── Fact-check rating sets ──────────────────────────────────────────────────
_FALSE_RATING_TERMS: frozenset[str] = frozenset([
    "false", "fake", "misleading", "pants on fire", "incorrect",
    "debunked", "unsupported", "mostly false", "unverified", "fabricated",
    "no evidence", "lacks evidence", "not true", "wrong",
])
_TRUE_RATING_TERMS: frozenset[str] = frozenset([
    "true", "correct", "accurate", "mostly true", "verified",
    "confirmed", "supported", "credible", "legitimate",
])
_MIXED_RATING_TERMS: frozenset[str] = frozenset([
    "half true", "mixed", "partly true", "partially true",
    "needs context", "outdated", "misleading context",
])

# ── News linguistic red flags ───────────────────────────────────────────────
# Sensationalist / clickbait language
_SENSATIONAL_PHRASES: frozenset[str] = frozenset([
    "you won't believe", "shocking", "bombshell", "explosive", "breaking:",
    "secret", "they don't want you to know", "exclusive", "urgent",
    "must read", "share before deleted", "going viral", "mainstream media won't",
    "suppressed", "hidden truth", "wake up", "open your eyes",
])
# Absolute/unverifiable claim markers
_ABSOLUTE_CLAIM_WORDS: frozenset[str] = frozenset([
    "completely", "totally", "100%", "proven", "guaranteed", "definitely",
    "undeniable", "irrefutable", "everyone knows", "scientists confirm",
    "doctors hate", "cures", "eliminates", "destroys", "saves",
])
# Medical/health misinformation patterns
_MEDICAL_MISINFO_PATTERNS: list[str] = [
    r"\bcures?\s+(covid|cancer|diabetes|aids|hiv|autism)\b",
    r"\b(lemon|garlic|ginger|vinegar|bleach|miracle)\s+(cure|treatment|remedy|heals?)\b",
    r"\bvaccine\s+(kills?|harms?|causes?|dangerous|microchip)\b",
    r"\b5g\s+(causes?|spreads?|radiation)\b",
    r"\bhome\s+remedy\s+(for|cures?|treats?)\b",
]
# Political misinformation markers
_POLITICAL_MISINFO_PATTERNS: list[str] = [
    r"\bstolen\s+election\b",
    r"\bdeep\s+state\b",
    r"\bnew\s+world\s+order\b",
    r"\bplandemic\b",
    r"\bfalse\s+flag\b",
    r"\bcrisis\s+actors?\b",
]
# High-credibility source indicators in claims
_CREDIBLE_SOURCE_INDICATORS: frozenset[str] = frozenset([
    "according to nasa", "according to who", "according to cdc", "according to reuters",
    "bbc reports", "associated press", "peer-reviewed", "published in", "study shows",
    "university", "institute", "official statement", "press release",
])

# ── Image forensic red flags in filename ──────────────────────────────────
_IMAGE_DEEPFAKE_KEYWORDS: frozenset[str] = frozenset([
    "ai_generated", "deepfake", "fake", "edited", "manipulated", "photoshop",
    "faceswap", "synthetic", "generated", "render", "hoax", "fraud",
])
_IMAGE_SUSPICIOUS_KEYWORDS: frozenset[str] = frozenset([
    "leaked", "exclusive", "proof", "evidence", "exposed", "viral",
    "unedited", "raw", "original_source", "conspiracy",
])

# ── Scoring weights ─────────────────────────────────────────────────────────
# News
_W_FALSE_FACTCHECK: float = 45.0
_W_TRUE_FACTCHECK: float = 25.0
_W_MIXED_FACTCHECK: float = -8.0
_W_SENSATIONAL_PHRASE: float = -6.0      # per phrase (capped)
_W_ABSOLUTE_CLAIM: float = -4.0          # per word (capped)
_W_MEDICAL_MISINFO: float = -20.0        # per pattern match
_W_POLITICAL_MISINFO: float = -15.0      # per pattern match
_W_CREDIBLE_SOURCE: float = 8.0          # per indicator
_W_SOURCE_VARIETY_3: float = 12.0        # 3+ sources
_W_SOURCE_VARIETY_5: float = 8.0         # 5+ additional bonus
_W_NO_REPORTS: float = -20.0
_W_HOAX_HEADLINE: float = -14.0          # per hoax-titled article
_W_FACTCHECK_EXISTS: float = 5.0         # any fact check found = signal

# Image
_W_AI_GENERATED: float = -55.0           # per score point (multiplied)
_W_MANIPULATED: float = -45.0
_W_ORIGINAL: float = 15.0               # strong original signal
_W_ORIGINAL_WEAK: float = 8.0           # moderate original signal
_W_SPOOF_HIGH: float = -25.0
_W_SPOOF_POSSIBLE: float = -12.0
_W_DEBUNK_PAGE: float = -18.0
_W_CLEAN_WEB: float = 8.0
_W_FILENAME_DEEPFAKE: float = -15.0
_W_FILENAME_SUSPICIOUS: float = -7.0
# EXIF bonuses/deductions
_W_FULL_EXIF: float = 15.0              # Complete camera metadata
_W_HAS_GPS: float = 8.0                 # GPS data present
_W_HAS_TIMESTAMP: float = 5.0           # Capture timestamp
_W_EDITING_SOFTWARE: float = -20.0      # Photoshop/GIMP in software tag
_W_NO_EXIF: float = -12.0              # Missing EXIF (possible stripping)
_W_SCREENSHOT_SIGNAL: float = -8.0      # No camera make/model but has EXIF

# Thresholds
_DEEPFAKE_THRESHOLD: float = 0.30       # Lowered: catch 30%+ AI probability
_ORIGINAL_STRONG_THRESHOLD: float = 0.75
_ORIGINAL_WEAK_THRESHOLD: float = 0.50
_SPOOF_RATINGS_HIGH: frozenset[str] = frozenset(["LIKELY", "VERY_LIKELY"])
_SPOOF_RATINGS_POSSIBLE: frozenset[str] = frozenset(["POSSIBLE"])
_SOURCE_VARIETY_STRONG: int = 5
_SOURCE_VARIETY_MIN: int = 3
_MAX_SENSATIONAL_DEDUCTION: float = 24.0
_MAX_ABSOLUTE_DEDUCTION: float = 16.0
_MAX_MEDICAL_DEDUCTION: float = 40.0
_MAX_POLITICAL_DEDUCTION: float = 30.0

_HOAX_TITLE_KEYWORDS: frozenset[str] = frozenset([
    "hoax", "fake", "scam", "manipulated", "debunk", "false", "fabricated",
])
_DEBUNK_PAGE_TERMS: frozenset[str] = frozenset([
    "fake", "hoax", "debunk", "misleading", "fact check", "false claim",
])
_EDITING_SOFTWARE_PATTERNS: list[str] = [
    "photoshop", "gimp", "lightroom", "affinity", "pixlr", "canva",
    "paint.net", "adobe", "corel", "snapseed",
]

# ── Emotional Tone Analysis constants ────────────────────────────────
_FEAR_PHRASES: frozenset[str] = frozenset([
    "danger", "deadly", "catastrophic", "apocalyptic", "end of the world",
    "be afraid", "threat", "panic", "crisis", "emergency", "terror",
    "life-threatening", "beware", "alarm", "catastrophe", "imminent",
])
_OUTRAGE_PHRASES: frozenset[str] = frozenset([
    "outrageous", "unacceptable", "disgusting", "scandalous", "appalling",
    "infuriating", "they must be stopped", "enough is enough", "wake up",
    "demand answers", "hold them accountable", "corrupt", "criminal",
])
_PROPAGANDA_PHRASES: frozenset[str] = frozenset([
    "patriot", "traitor", "enemy of the people", "real american", "globalist",
    "elites", "they want to control", "mainstream media lies", "fake news media",
    "tyranny", "sheeple", "red pill", "black pill", "great reset",
])

# Caps and punctuation thresholds
_CAPS_RATIO_THRESHOLD: float = 0.25   # >25% uppercase letters = alarm
_EXCLAMATION_THRESHOLD: int = 2       # >2 exclamation marks in a claim
_W_FEAR_LANGUAGE: float = -5.0        # per fear phrase (capped at -15)
_W_OUTRAGE_LANGUAGE: float = -6.0     # per outrage phrase (capped at -18)
_W_PROPAGANDA: float = -8.0           # per propaganda phrase (capped at -20)
_W_CAPS_HEAVY: float = -10.0          # heavy ALL-CAPS usage
_W_EXCLAMATION: float = -5.0          # excessive exclamation marks
_MAX_FEAR_DEDUCTION: float = 15.0
_MAX_OUTRAGE_DEDUCTION: float = 18.0
_MAX_PROPAGANDA_DEDUCTION: float = 20.0

# ── Confidence interval constants ───────────────────────────────────
# Confidence narrows when more signals agree; widens when data is sparse.
_BASE_CONFIDENCE_MARGIN: float = 12.0  # default ±12 pts when only 1 API
_MIN_CONFIDENCE_MARGIN: float = 4.0    # tightest possible (all APIs agree)
_MAX_CONFIDENCE_MARGIN: float = 20.0   # widest (no real data, mock mode)



class TrustEngine:

    # ── Internal: Emotional tone analysis ────────────────────────────────

    def analyze_tone(self, claim: str) -> dict[str, Any]:
        """
        Analyse the emotional tone and propaganda signals in a claim.
        Returns a structured tone report and a score delta.
        """
        c = claim.lower()
        delta = 0.0
        signals = []
        tone_labels = []

        # Fear language
        fear_hits = [p for p in _FEAR_PHRASES if p in c]
        if fear_hits:
            deduction = max(len(fear_hits) * _W_FEAR_LANGUAGE, -_MAX_FEAR_DEDUCTION)
            delta += deduction
            tone_labels.append("Fear-Inducing")
            signals.append({
                "type": "fear",
                "label": "Fear-Inducing Language",
                "detail": f'Detected: {", ".join(fear_hits[:3])}',
                "score_delta": round(deduction, 1),
            })

        # Outrage language
        outrage_hits = [p for p in _OUTRAGE_PHRASES if p in c]
        if outrage_hits:
            deduction = max(len(outrage_hits) * _W_OUTRAGE_LANGUAGE, -_MAX_OUTRAGE_DEDUCTION)
            delta += deduction
            tone_labels.append("Outrage Bait")
            signals.append({
                "type": "outrage",
                "label": "Outrage / Emotional Manipulation",
                "detail": f'Detected: {", ".join(outrage_hits[:3])}',
                "score_delta": round(deduction, 1),
            })

        # Propaganda phrases
        prop_hits = [p for p in _PROPAGANDA_PHRASES if p in c]
        if prop_hits:
            deduction = max(len(prop_hits) * _W_PROPAGANDA, -_MAX_PROPAGANDA_DEDUCTION)
            delta += deduction
            tone_labels.append("Propaganda")
            signals.append({
                "type": "propaganda",
                "label": "Propaganda / Ideological Framing",
                "detail": f'Detected: {", ".join(prop_hits[:3])}',
                "score_delta": round(deduction, 1),
            })

        # ALL-CAPS ratio
        alpha = [ch for ch in claim if ch.isalpha()]
        caps_ratio = sum(1 for ch in alpha if ch.isupper()) / max(len(alpha), 1)
        if caps_ratio > _CAPS_RATIO_THRESHOLD and len(claim) > 30:
            delta += _W_CAPS_HEAVY
            tone_labels.append("Excessive Capitalization")
            signals.append({
                "type": "caps",
                "label": "Heavy ALL-CAPS Usage",
                "detail": f"{caps_ratio * 100:.0f}% of letters are uppercase — common in sensationalist content.",
                "score_delta": _W_CAPS_HEAVY,
            })

        # Exclamation marks
        exclamation_count = claim.count('!')
        if exclamation_count > _EXCLAMATION_THRESHOLD:
            delta += _W_EXCLAMATION
            tone_labels.append("Excessive Punctuation")
            signals.append({
                "type": "punctuation",
                "label": "Excessive Exclamation Marks",
                "detail": f"{exclamation_count} exclamation marks detected. Credible reporting uses measured language.",
                "score_delta": _W_EXCLAMATION,
            })

        overall_tone = "Neutral"
        if len(tone_labels) >= 3:
            overall_tone = "Highly Manipulative"
        elif len(tone_labels) == 2:
            overall_tone = "Emotionally Charged"
        elif len(tone_labels) == 1:
            overall_tone = tone_labels[0]

        return {
            "overall_tone": overall_tone,
            "tone_labels": tone_labels,
            "signals": signals,
            "score_delta": round(delta, 1),
            "caps_ratio": round(caps_ratio * 100, 1),
            "exclamation_count": exclamation_count,
        }

    # ── Confidence interval calculator ─────────────────────────────────

    @staticmethod
    def _calculate_confidence(
        score: float,
        n_fact_checks: int,
        n_news_reports: int,
        is_mock: bool = False,
    ) -> tuple[float, float]:
        """
        Calculate a confidence interval [low, high] around the trust score.
        Confidence tightens with more corroborating signals.
        """
        if is_mock:
            margin = _MAX_CONFIDENCE_MARGIN
        else:
            # Each additional data source reduces the margin
            signals = n_fact_checks + min(n_news_reports // 2, 5)
            margin = max(
                _BASE_CONFIDENCE_MARGIN - (signals * 1.5),
                _MIN_CONFIDENCE_MARGIN,
            )

        low = max(0.0, score - margin)
        high = min(100.0, score + margin)
        return round(low, 1), round(high, 1)

    # ── Internal: Linguistic analysis for news claims ────────────────────

    def _analyze_claim_text(
        self, claim: str, deductions: list, bonuses: list
    ) -> float:
        """
        Analyze the raw claim text for misinformation signals and credibility markers.
        Returns a net score delta (positive = more trustworthy, negative = suspicious).
        """
        delta: float = 0.0
        claim_lower = claim.lower()

        # 1. Sensationalist language
        found_sensational = [p for p in _SENSATIONAL_PHRASES if p in claim_lower]
        if found_sensational:
            deduction = min(len(found_sensational) * _W_SENSATIONAL_PHRASE, 0)
            deduction = max(deduction, -_MAX_SENSATIONAL_DEDUCTION)
            delta += deduction
            phrases_str = ", ".join(f'"{p}"' for p in found_sensational[:3])
            deductions.append({
                "text": f"Sensationalist language detected: {phrases_str}.",
                "url": "",
                "source": "Linguistic Heuristics",
            })

        # 2. Absolute claim markers
        found_absolute = [w for w in _ABSOLUTE_CLAIM_WORDS if w in claim_lower]
        if found_absolute:
            deduction = min(len(found_absolute) * _W_ABSOLUTE_CLAIM, 0)
            deduction = max(deduction, -_MAX_ABSOLUTE_DEDUCTION)
            delta += deduction
            words_str = ", ".join(f'"{w}"' for w in found_absolute[:3])
            deductions.append({
                "text": f"Unqualified absolute claim language detected: {words_str}.",
                "url": "",
                "source": "Linguistic Heuristics",
            })


        # 3. Medical misinformation patterns
        medical_hits = [
            p for p in _MEDICAL_MISINFO_PATTERNS
            if re.search(p, claim_lower)
        ]
        if medical_hits:
            deduction = max(len(medical_hits) * _W_MEDICAL_MISINFO, -_MAX_MEDICAL_DEDUCTION)
            delta += deduction
            deductions.append({
                "text": "Claim matches known medical misinformation pattern (unproven health remedy or cure).",
                "url": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters",
                "source": "WHO Myth Busters",
            })

        # 4. Political misinformation patterns
        political_hits = [
            p for p in _POLITICAL_MISINFO_PATTERNS
            if re.search(p, claim_lower)
        ]
        if political_hits:
            deduction = max(len(political_hits) * _W_POLITICAL_MISINFO, -_MAX_POLITICAL_DEDUCTION)
            delta += deduction
            deductions.append({
                "text": "Claim contains known political misinformation pattern.",
                "url": "",
                "source": "Misinformation Pattern Database",
            })

        # 5. Credible source indicators
        found_credible = [ind for ind in _CREDIBLE_SOURCE_INDICATORS if ind in claim_lower]
        if found_credible:
            bonus = min(len(found_credible) * _W_CREDIBLE_SOURCE, 20.0)
            delta += bonus
            bonuses.append({
                "text": f"Claim references credible sources: {', '.join(found_credible[:2])}.",
                "url": "",
                "source": "Source Credibility Analysis",
            })

        return delta

    # ── News scoring ─────────────────────────────────────────────────────────

    def calculate_news_score(
        self,
        fact_checks: list[dict[str, Any]],
        news_reports: list[dict[str, Any]],
        claim: str = "",
        url_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Calculate trust score (0–100), risk level, tone, entities and confidence for a news claim."""
        score: float = _BASE_NEWS_SCORE
        deductions: list[dict[str, Any]] = []
        bonuses: list[dict[str, Any]] = []

        # ── 1. Linguistic content analysis ─────────────────────────────────
        if claim:
            score += self._analyze_claim_text(claim, deductions, bonuses)

        # ── 1b. Emotional tone analysis ──────────────────────────────────
        tone_analysis: dict[str, Any] = {"overall_tone": "Neutral", "signals": []}
        if claim:
            tone_analysis = self.analyze_tone(claim)
            score += tone_analysis["score_delta"]
            if tone_analysis["signals"]:
                for sig in tone_analysis["signals"]:
                    deductions.append({
                        "text": f"{sig['label']}: {sig['detail']}",
                        "url": "",
                        "source": "Tone Analysis Engine",
                    })

        # ── 1c. Named entity extraction ──────────────────────────────────
        from app.services.entity_service import extract_entities, get_entity_score_delta
        entities: dict[str, Any] = {}
        if claim:
            entities = extract_entities(claim)
            entity_delta, entity_signals = get_entity_score_delta(entities)
            score += entity_delta
            deductions.extend(s for s in entity_signals if s["text"].startswith(("Claim attributes", "Claim references")))
            bonuses.extend(s for s in entity_signals if not s["text"].startswith(("Claim attributes", "Claim references")))

        # ── 1d. URL / domain credibility signal ────────────────────────
        if url_context and url_context.get("scraped"):
            domain_cred = url_context.get("domain_credibility", {})
            score_delta = domain_cred.get("score_delta", 0)
            score += score_delta
            if score_delta < 0:
                deductions.append({
                    "text": f"Source domain '{url_context.get('domain')}' rated: {domain_cred.get('label', 'Unknown')}.",
                    "url": url_context.get("url", ""),
                    "source": "Domain Reputation",
                })
            elif score_delta > 0:
                bonuses.append({
                    "text": f"Source domain '{url_context.get('domain')}' rated: {domain_cred.get('label', 'Trusted')}.",
                    "url": url_context.get("url", ""),
                    "source": "Domain Reputation",
                })

        # ── 2. Fact-check evaluation ──────────────────────────────────────────
        has_false = False
        has_true = False
        has_mixed = False

        if fact_checks:
            score += _W_FACTCHECK_EXISTS  # Having any fact check is informative

            for check in fact_checks:
                for review in check.get("claimReview", []):
                    rating_lower = review.get("textualRating", "").lower()
                    publisher = review.get("publisher", {}).get("name", "Fact-checker")
                    review_url = review.get("url", "")

                    if any(term in rating_lower for term in _FALSE_RATING_TERMS):
                        has_false = True
                        deductions.append({
                            "text": f"Fact check rating: '{review.get('textualRating')}' — rated by {publisher}.",
                            "url": review_url,
                            "source": publisher,
                        })
                    elif any(term in rating_lower for term in _MIXED_RATING_TERMS):
                        has_mixed = True
                        deductions.append({
                            "text": f"Fact check rating: '{review.get('textualRating')}' — partially accurate per {publisher}.",
                            "url": review_url,
                            "source": publisher,
                        })
                    elif any(term in rating_lower for term in _TRUE_RATING_TERMS):
                        if not has_false:
                            has_true = True
                            bonuses.append({
                                "text": f"Independently verified as accurate by {publisher}.",
                                "url": review_url,
                                "source": publisher,
                            })

            if has_false:
                score -= _W_FALSE_FACTCHECK
            elif has_true:
                score += _W_TRUE_FACTCHECK
            elif has_mixed:
                score += _W_MIXED_FACTCHECK

        # ── 3. News-report coverage ───────────────────────────────────────────
        if not news_reports:
            score += _W_NO_REPORTS
            deductions.append({
                "text": "No mainstream media reports found referencing this claim — potential echo-chamber rumor.",
                "url": "",
                "source": "",
            })
        else:
            # Unique source diversity
            sources = {art.get("source") for art in news_reports if art.get("source")}
            source_count = len(sources)

            if source_count >= _SOURCE_VARIETY_STRONG:
                score += _W_SOURCE_VARIETY_3 + _W_SOURCE_VARIETY_5
                first_url = next((a.get("url", "") for a in news_reports if a.get("url")), "")
                first_src = next((a.get("source", "") for a in news_reports if a.get("source")), "")
                bonuses.append({
                    "text": f"Widely corroborated — reported across {source_count} independent media publications.",
                    "url": first_url,
                    "source": first_src,
                })
            elif source_count >= _SOURCE_VARIETY_MIN:
                score += _W_SOURCE_VARIETY_3
                first_url = next((a.get("url", "") for a in news_reports if a.get("url")), "")
                first_src = next((a.get("source", "") for a in news_reports if a.get("source")), "")
                bonuses.append({
                    "text": f"Reported across {source_count} different media publications.",
                    "url": first_url,
                    "source": first_src,
                })
            elif source_count >= 1:
                # Only 1-2 sources — mild bonus but note limited coverage
                score += 4.0
                bonuses.append({
                    "text": f"Found {source_count} media report(s) — limited corroboration.",
                    "url": next((a.get("url", "") for a in news_reports if a.get("url")), ""),
                    "source": next((a.get("source", "") for a in news_reports if a.get("source")), ""),
                })

            # Hoax/debunking headlines
            hoax_articles = [
                art for art in news_reports
                if any(kw in art.get("title", "").lower() for kw in _HOAX_TITLE_KEYWORDS)
            ]
            hoax_count = len(hoax_articles)
            if hoax_count:
                deduction = min(hoax_count * _W_HOAX_HEADLINE, score)
                score -= deduction
                hoax_url = hoax_articles[0].get("url", "")
                hoax_source = hoax_articles[0].get("source", "")
                deductions.append({
                    "text": f"Found {hoax_count} article(s) with debunking/hoax language in headline.",
                    "url": hoax_url,
                    "source": hoax_source,
                })

        score = max(0.0, min(100.0, score))
        is_mock = len(fact_checks) == 0 and len(news_reports) <= 2
        conf_low, conf_high = self._calculate_confidence(
            score, len(fact_checks), len(news_reports), is_mock=is_mock
        )
        return {
            "trust_score": round(score, 1),
            "confidence_low": conf_low,
            "confidence_high": conf_high,
            "risk_level": self._get_risk_level(score),
            "deductions": deductions,
            "bonuses": bonuses,
            "tone_analysis": tone_analysis,
            "entities": entities,
        }


    # ── Image scoring ────────────────────────────────────────────────────────

    def calculate_image_score(
        self,
        hive_data: dict[str, Any],
        vision_data: dict[str, Any],
        image_metadata: dict[str, Any] | None = None,
        filename: str = "",
    ) -> dict[str, Any]:
        """Calculate trust score (0–100) and risk level for an image."""
        score: float = _BASE_IMAGE_SCORE
        deductions: list[dict[str, Any]] = []
        bonuses: list[dict[str, Any]] = []

        # ── 1. Filename heuristics ────────────────────────────────────────────
        fname_lower = filename.lower()
        found_deepfake_kw = [kw for kw in _IMAGE_DEEPFAKE_KEYWORDS if kw in fname_lower]
        found_suspicious_kw = [kw for kw in _IMAGE_SUSPICIOUS_KEYWORDS if kw in fname_lower]
        if found_deepfake_kw:
            score += _W_FILENAME_DEEPFAKE
            deductions.append({
                "text": f"Filename contains deepfake/manipulation indicators: {', '.join(found_deepfake_kw)}.",
                "url": "",
                "source": "Filename Analysis",
            })
        elif found_suspicious_kw:
            score += _W_FILENAME_SUSPICIOUS
            deductions.append({
                "text": f"Filename contains suspicious content markers: {', '.join(found_suspicious_kw)}.",
                "url": "",
                "source": "Filename Analysis",
            })

        # ── 2. EXIF metadata forensics ────────────────────────────────────────
        if image_metadata:
            has_exif = image_metadata.get("has_exif", False)
            camera = image_metadata.get("camera", {})
            gps = image_metadata.get("gps", {})
            capture_time = image_metadata.get("capture_time", {})
            settings_data = image_metadata.get("settings", {})

            if has_exif:
                camera_make = camera.get("Make", "")
                camera_model = camera.get("Model", "")
                software = camera.get("Software", "")

                # Check for editing software (strong manipulation signal)
                editing_detected = any(
                    sw in software.lower()
                    for sw in _EDITING_SOFTWARE_PATTERNS
                ) if software else False

                if editing_detected:
                    score += _W_EDITING_SOFTWARE
                    deductions.append({
                        "text": f"EXIF 'Software' tag reveals image was processed in: '{software}'. Indicates post-capture editing.",
                        "url": "",
                        "source": "EXIF Metadata",
                    })
                elif camera_make and camera_model:
                    # Full authentic camera metadata — strong trust signal
                    score += _W_FULL_EXIF
                    bonuses.append({
                        "text": f"Complete camera metadata: {camera_make} {camera_model}. Indicates authentic capture.",
                        "url": "",
                        "source": "EXIF Metadata",
                    })
                elif not camera_make and not camera_model and not software:
                    # Has EXIF but no camera — screenshot or stripped
                    score += _W_SCREENSHOT_SIGNAL
                    deductions.append({
                        "text": "EXIF present but no camera make/model — possible screenshot or metadata stripping.",
                        "url": "",
                        "source": "EXIF Metadata",
                    })

                # GPS data = strong authenticity signal
                if gps and gps.get("latitude") is not None:
                    score += _W_HAS_GPS
                    maps_url = gps.get("maps_url", "")
                    bonuses.append({
                        "text": f"GPS geolocation embedded: {gps.get('latitude'):.4f}°, {gps.get('longitude'):.4f}°.",
                        "url": maps_url,
                        "source": "EXIF GPS Data",
                    })

                # Capture timestamp
                if capture_time and capture_time.get("formatted"):
                    score += _W_HAS_TIMESTAMP
                    bonuses.append({
                        "text": f"Authentic capture timestamp: {capture_time['formatted']}.",
                        "url": "",
                        "source": "EXIF Metadata",
                    })

                # Exposure settings = camera authenticity (not AI generated)
                if settings_data.get("FNumber") and settings_data.get("ISOSpeedRatings"):
                    score += 5.0
                    bonuses.append({
                        "text": f"Camera exposure settings present (f/{settings_data.get('FNumber')}, ISO {settings_data.get('ISOSpeedRatings')}) — consistent with authentic capture.",
                        "url": "",
                        "source": "EXIF Camera Settings",
                    })

            else:
                # No EXIF at all — red flag
                score += _W_NO_EXIF
                deductions.append({
                    "text": "No EXIF metadata detected — image may be a screenshot, AI-generated, or metadata was stripped.",
                    "url": "",
                    "source": "EXIF Metadata",
                })

        # ── 3. Hive deepfake predictions ──────────────────────────────────────
        for pred in hive_data.get("predictions", []):
            pred_class: str = pred.get("class", "")
            pred_score: float = float(pred.get("score", 0.0))

            if pred_class == "ai_generated":
                if pred_score > _DEEPFAKE_THRESHOLD:
                    score += pred_score * _W_AI_GENERATED
                    deductions.append({
                        "text": f"Hive AI detection: {pred_score * 100:.1f}% probability this image is AI-generated.",
                        "url": "https://thehive.ai",
                        "source": "Hive Moderation AI",
                    })
                elif pred_score > 0.10:
                    # Low but nonzero AI signal — mild deduction
                    score -= pred_score * 15.0
                    deductions.append({
                        "text": f"Minor AI-generation signal detected: {pred_score * 100:.1f}% — insufficient to flag definitively.",
                        "url": "https://thehive.ai",
                        "source": "Hive Moderation AI",
                    })

            elif pred_class == "manipulated":
                if pred_score > _DEEPFAKE_THRESHOLD:
                    score += pred_score * _W_MANIPULATED
                    deductions.append({
                        "text": f"Hive AI detection: {pred_score * 100:.1f}% probability this image has been digitally manipulated.",
                        "url": "https://thehive.ai",
                        "source": "Hive Moderation AI",
                    })

            elif pred_class == "original":
                if pred_score > _ORIGINAL_STRONG_THRESHOLD:
                    score += _W_ORIGINAL
                    bonuses.append({
                        "text": f"Hive AI scan: {pred_score * 100:.1f}% confidence this is an original, unaltered image.",
                        "url": "https://thehive.ai",
                        "source": "Hive Moderation AI",
                    })
                elif pred_score > _ORIGINAL_WEAK_THRESHOLD:
                    score += _W_ORIGINAL_WEAK
                    bonuses.append({
                        "text": f"Hive AI scan: {pred_score * 100:.1f}% original probability — moderate authenticity confidence.",
                        "url": "https://thehive.ai",
                        "source": "Hive Moderation AI",
                    })

        # ── 4. Google Vision SafeSearch spoof flag ────────────────────────────
        safe_search: dict[str, str] = vision_data.get("safeSearchAnnotation", {})
        spoof_rating: str = safe_search.get("spoof", "UNKNOWN")
        if spoof_rating in _SPOOF_RATINGS_HIGH:
            score += _W_SPOOF_HIGH
            deductions.append({
                "text": f"Google Vision Spoof detection: '{spoof_rating}' — strong spoof/composite signal.",
                "url": "https://cloud.google.com/vision/docs/detecting-safe-search",
                "source": "Google Vision API",
            })
        elif spoof_rating in _SPOOF_RATINGS_POSSIBLE:
            score += _W_SPOOF_POSSIBLE
            deductions.append({
                "text": "Google Vision Spoof detection: 'POSSIBLE' — moderate spoof probability.",
                "url": "https://cloud.google.com/vision/docs/detecting-safe-search",
                "source": "Google Vision API",
            })

        # ── 5. Web-detection debunk context ──────────────────────────────────
        pages: list[dict] = vision_data.get("webDetection", {}).get("pagesWithMatchingImages", [])
        debunk_pages = [
            page for page in pages
            if any(term in page.get("pageTitle", "").lower() for term in _DEBUNK_PAGE_TERMS)
        ]
        if debunk_pages:
            score += len(debunk_pages) * _W_DEBUNK_PAGE
            deductions.append({
                "text": f"Image matches {len(debunk_pages)} web page(s) flagged as fact checks or debunks.",
                "url": debunk_pages[0].get("url", ""),
                "source": debunk_pages[0].get("pageTitle", "Web Source"),
            })
        elif pages:
            score += _W_CLEAN_WEB
            bonuses.append({
                "text": "Image is indexed on verified online sources with no debunking context.",
                "url": pages[0].get("url", ""),
                "source": pages[0].get("pageTitle", "Web Source"),
            })

        score = max(0.0, min(100.0, score))
        # Confidence for images: use hive + vision signal count
        n_signals = len(hive_data.get("predictions", []))
        n_vision = 1 if vision_data.get("safeSearchAnnotation") else 0
        is_mock_img = hive_data.get("mock", False)
        conf_low, conf_high = self._calculate_confidence(
            score, n_signals, n_vision, is_mock=is_mock_img
        )
        return {
            "trust_score": round(score, 1),
            "confidence_low": conf_low,
            "confidence_high": conf_high,
            "risk_level": self._get_risk_level(score),
            "deductions": deductions,
            "bonuses": bonuses,
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _get_risk_level(score: float) -> str:
        if score >= 75.0:
            return "LOW"
        if score >= 50.0:
            return "MEDIUM"
        if score >= 25.0:
            return "HIGH"
        return "CRITICAL"


trust_engine = TrustEngine()
