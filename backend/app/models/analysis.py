from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.config import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True) # UUID or generated ID for shareable reports
    type = Column(String, nullable=False)             # "news" or "image"
    query = Column(String, nullable=False)            # claim text or image filename/URL
    status = Column(String, default="processing")     # "processing", "completed", "failed"
    trust_score = Column(Float, nullable=True)        # 0.0 to 100.0
    risk_level = Column(String, nullable=True)         # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    
    # Store all source payloads, fact-check ratings, LLM reasoning, etc. in JSON format
    details = Column(JSON, nullable=True)
    
    # Store perceptual image hash for viral deepfake caching
    image_hash = Column(String, index=True, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="analyses")
