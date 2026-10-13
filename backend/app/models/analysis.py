import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.config import Base


class Analysis(Base):
    """
    Stores the result of a TruthLens AI verification run.

    Columns
    -------
    id          : UUID string primary key, auto-generated on insert.
    analysis_type : "news" or "image" (renamed from `type` to avoid shadowing built-in).
    query       : Claim text or image filename / URL submitted for analysis.
    status      : Lifecycle state – "processing" | "completed" | "failed".
    trust_score : 0.0–100.0 confidence score produced by the trust engine.
    risk_level  : Enum-constrained severity – "LOW" | "MEDIUM" | "HIGH" | "CRITICAL".
    details     : Arbitrary JSON payload (fact-checks, LLM reasoning, scoring breakdown, …).
    image_hash  : Perceptual image hash for viral deepfake caching (nullable).
    created_at  : UTC timestamp of record creation.
    updated_at  : UTC timestamp of last status change (auto-updated on every write).
    user_id     : FK to users.id (nullable – anonymous analyses allowed).
    """

    __tablename__ = "analyses"

    id = Column(
        String,
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID primary key for shareable report links",
    )

    # Renamed from `type` to avoid shadowing Python's built-in `type`.
    # The column name in the DB stays `analysis_type`; update any raw SQL accordingly.
    analysis_type = Column(
        String,
        nullable=False,
        comment='"news" or "image"',
    )

    query = Column(String, nullable=False, comment="Claim text or image filename/URL")

    status = Column(
        sa.Enum("processing", "completed", "failed", name="analysis_status_enum"),
        nullable=False,
        default="processing",
        comment='"processing" | "completed" | "failed"',
    )

    trust_score = Column(Float, nullable=True, comment="0.0 to 100.0")

    risk_level = Column(
        sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="risk_level_enum"),
        nullable=True,
        index=True,
        comment='"LOW" | "MEDIUM" | "HIGH" | "CRITICAL"',
    )

    # All source payloads, fact-check ratings, LLM reasoning, etc.
    details = Column(JSON, nullable=True)

    # Perceptual image hash for viral deepfake result caching
    image_hash = Column(String, index=True, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user = relationship("User", back_populates="analyses")

    def __repr__(self) -> str:
        return (
            f"<Analysis id={self.id!r} type={self.analysis_type!r} "
            f"status={self.status!r} trust={self.trust_score}>"
        )
