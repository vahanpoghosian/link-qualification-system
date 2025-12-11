from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class WebsiteBase(BaseModel):
    url: str
    email: str
    price: float

class WebsiteCreate(WebsiteBase):
    pass

class WebsiteResponse(WebsiteBase):
    id: int
    dr: Optional[int]
    traffic: Optional[int]
    keywords_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ImportStatus(BaseModel):
    id: int
    status: str
    total_websites: int
    processed_websites: int

class PageData(BaseModel):
    url: str
    keywords: List[str]
    vector_id: Optional[str]