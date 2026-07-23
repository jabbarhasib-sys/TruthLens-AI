"""
TruthLens AI – Enhanced Image Metadata Extractor
Extracts EXIF, GPS coordinates, capture timestamp, device make/model,
and computed metadata from uploaded image bytes using Pillow.
"""
from __future__ import annotations

import io
import logging
import struct
from datetime import datetime
from typing import Any, Optional

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

logger = logging.getLogger("truthlens.exif")

# ── Human-readable tag groups ────────────────────────────────────────────────

_CAMERA_TAGS = frozenset(
    ["Make", "Model", "LensMake", "LensModel", "Software", "BodySerialNumber"]
)
_DATETIME_TAGS = frozenset(
    ["DateTime", "DateTimeOriginal", "DateTimeDigitized", "GPSDateStamp"]
)
_SETTINGS_TAGS = frozenset(
    ["ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength",
     "Flash", "WhiteBalance", "ExposureProgram", "MeteringMode",
     "ShutterSpeedValue", "ApertureValue", "BrightnessValue",
     "ExposureBiasValue", "MaxApertureValue", "DigitalZoomRatio"]
)


def _rational_to_float(value: Any) -> float:
    """Convert a PIL IFDRational or (num, denom) tuple to float."""
    try:
        if hasattr(value, 'numerator'):
            return float(value.numerator) / float(value.denominator or 1)
        if isinstance(value, tuple) and len(value) == 2:
            return float(value[0]) / float(value[1] or 1)
        return float(value)
    except Exception:
        return 0.0


def _dms_to_decimal(dms: tuple, ref: str) -> Optional[float]:
    """Convert GPS degrees-minutes-seconds tuple + hemisphere to decimal degrees."""
    try:
        degrees = _rational_to_float(dms[0])
        minutes = _rational_to_float(dms[1]) / 60.0
        seconds = _rational_to_float(dms[2]) / 3600.0
        decimal = degrees + minutes + seconds
        if ref in ("S", "W"):
            decimal = -decimal
        return round(decimal, 7)
    except Exception:
        return None


def _parse_gps(gps_info: dict) -> dict[str, Any]:
    """Decode raw GPS IFD tags into a structured geolocation dict."""
    decoded: dict[str, Any] = {}
    for tag_id, value in gps_info.items():
        tag_name = GPSTAGS.get(tag_id, tag_id)
        decoded[tag_name] = value

    lat = lon = None
    if "GPSLatitude" in decoded and "GPSLatitudeRef" in decoded:
        lat = _dms_to_decimal(decoded["GPSLatitude"], decoded["GPSLatitudeRef"])
    if "GPSLongitude" in decoded and "GPSLongitudeRef" in decoded:
        lon = _dms_to_decimal(decoded["GPSLongitude"], decoded["GPSLongitudeRef"])

    result: dict[str, Any] = {}
    if lat is not None:
        result["latitude"] = lat
    if lon is not None:
        result["longitude"] = lon
    if lat is not None and lon is not None:
        result["maps_url"] = f"https://www.google.com/maps?q={lat},{lon}"
    if "GPSAltitude" in decoded:
        result["altitude_m"] = round(_rational_to_float(decoded["GPSAltitude"]), 2)
    if "GPSDateStamp" in decoded:
        result["gps_date"] = str(decoded["GPSDateStamp"])
    if "GPSSpeedRef" in decoded and "GPSSpeed" in decoded:
        result["speed"] = f"{_rational_to_float(decoded['GPSSpeed'])} {decoded['GPSSpeedRef']}"
    return result


def extract_metadata(image_bytes: bytes) -> dict[str, Any]:
    """
    Full image metadata extraction pipeline.

    Returns a structured dict with:
    - `dimensions`: width × height, megapixels
    - `format`: file format and mode
    - `camera`: make, model, lens, software
    - `capture_time`: human-readable datetime, ISO 8601
    - `settings`: exposure, ISO, focal length, etc.
    - `gps`: latitude, longitude, altitude, Google Maps URL
    - `anomalies`: list of suspicious signals detected locally
    - `has_exif`: whether any EXIF data was present
    """
    result: dict[str, Any] = {
        "has_exif": False,
        "dimensions": {},
        "format": {},
        "camera": {},
        "capture_time": {},
        "settings": {},
        "gps": {},
        "anomalies": [],
    }

    try:
        img = Image.open(io.BytesIO(image_bytes))

        # Dimensions
        width, height = img.size
        result["dimensions"] = {
            "width": width,
            "height": height,
            "megapixels": round(width * height / 1_000_000, 2),
            "aspect_ratio": f"{width}:{height}",
        }

        # Format
        result["format"] = {
            "format": img.format or "unknown",
            "mode": img.mode,
        }

        # EXIF
        raw_exif = img._getexif()  # type: ignore[attr-defined]
        if not raw_exif:
            result["anomalies"].append(
                "No EXIF metadata detected — image may have been screenshot, stripped, or AI-generated."
            )
            return result

        result["has_exif"] = True

        camera: dict[str, str] = {}
        capture_time: dict[str, Any] = {}
        settings: dict[str, Any] = {}
        gps_raw: dict[int, Any] = {}

        for tag_id, value in raw_exif.items():
            tag_name = TAGS.get(tag_id, str(tag_id))

            # GPS sub-IFD
            if tag_name == "GPSInfo" and isinstance(value, dict):
                gps_raw = value
                continue

            # Stringify to avoid non-serializable types in JSON
            try:
                str_value = str(value) if not isinstance(value, (str, int, float)) else value
            except Exception:
                continue

            if tag_name in _CAMERA_TAGS:
                camera[tag_name] = str(str_value).strip()
            elif tag_name in _DATETIME_TAGS:
                capture_time[tag_name] = str(str_value).strip()
            elif tag_name in _SETTINGS_TAGS:
                settings[tag_name] = str_value

        result["camera"] = camera
        result["settings"] = settings

        # Structured capture time
        raw_ts = (
            capture_time.get("DateTimeOriginal")
            or capture_time.get("DateTime")
            or capture_time.get("DateTimeDigitized")
        )
        if raw_ts:
            try:
                dt = datetime.strptime(raw_ts, "%Y:%m:%d %H:%M:%S")
                capture_time["formatted"] = dt.strftime("%B %d, %Y at %H:%M:%S")
                capture_time["iso8601"] = dt.isoformat()
                capture_time["timestamp_unix"] = int(dt.timestamp())
            except ValueError:
                pass
        result["capture_time"] = capture_time

        # GPS
        if gps_raw:
            result["gps"] = _parse_gps(gps_raw)

        # ── Local anomaly detection ───────────────────────────────────────
        anomalies: list[str] = []

        # 1. Software watermark suggests post-processing
        sw = camera.get("Software", "")
        suspicious_sw = ["photoshop", "lightroom", "gimp", "affinity", "snapseed",
                         "facetune", "meitu", "stable diffusion", "midjourney", "dall-e"]
        for suspect in suspicious_sw:
            if suspect in sw.lower():
                anomalies.append(
                    f"Editing software detected in EXIF: '{sw}'. "
                    "Image may have been processed or altered after capture."
                )
                break

        # 2. Mismatched timestamp (very old date in recent image)
        ts_unix = capture_time.get("timestamp_unix")
        if ts_unix and ts_unix < 978_307_200:  # < year 2001
            anomalies.append(
                "Capture timestamp predates 2001 — potential metadata tampering or clock misconfiguration."
            )

        # 3. Missing camera make/model with existing EXIF
        if result["has_exif"] and not camera.get("Make") and not camera.get("Model"):
            anomalies.append(
                "EXIF is present but camera make/model fields are absent — "
                "this is common in screenshots, AI-generated images, or stripped originals."
            )

        # 4. GPS present but indoor — heuristic (altitude near sea level)
        alt = result["gps"].get("altitude_m", None)
        if alt is not None and alt < 0:
            anomalies.append(
                f"GPS altitude is {alt}m (below sea level) — may indicate GPS spoofing or malformed data."
            )

        result["anomalies"] = anomalies

    except Exception as exc:
        logger.warning("Metadata extraction failed: %s", exc)
        result["anomalies"] = [f"Could not extract metadata: {exc}"]

    return result
