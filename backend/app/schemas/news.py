from pydantic import BaseModel, HttpUrl
from typing import Optional

class NewsVerificationRequest(BaseModel):
    claim: str
