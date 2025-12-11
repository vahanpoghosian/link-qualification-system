from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ImportInfo(BaseModel):
    id: int
    filename: str
    status: str
    created_at: datetime

class DashboardStats(BaseModel):
    total_websites: int
    total_imports: int
    total_pages: int
    total_users: int
    avg_dr: float
    avg_traffic: float
    recent_imports: List[ImportInfo]

class PageInfo(BaseModel):
    url: str
    keywords: List[str]
    vector_id: str

class WebsiteDetail(BaseModel):
    id: int
    url: str
    email: str
    price: float
    dr: Optional[int]
    traffic: Optional[int]
    keywords_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    pages: List[PageInfo]

    class Config:
        from_attributes = True