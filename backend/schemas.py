from pydantic import BaseModel
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: str

class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime

    class Config:
        from_attributes = True