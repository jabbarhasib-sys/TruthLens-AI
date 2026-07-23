from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class ReportResponse(BaseModel):
    id: str
    type: str
    query: str
    status: str
    trust_score: Optional[float] = None
    risk_level: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
        
class HistoryResponse(BaseModel):
    id: str
    type: str
    query: str
    status: str
    trust_score: Optional[float] = None
    risk_level: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
