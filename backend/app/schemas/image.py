from pydantic import BaseModel
from typing import Optional

class ImageVerificationRequest(BaseModel):
    image_url: str
