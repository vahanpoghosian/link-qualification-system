from pydantic import BaseModel
from typing import Optional, List

class SearchRequest(BaseModel):
    keyword: str
    min_dr: Optional[int] = None
    max_dr: Optional[int] = None
    min_traffic: Optional[int] = None
    max_price: Optional[float] = None
    limit: Optional[int] = 20

class SearchResult(BaseModel):
    id: int
    url: str
    email: str
    price: float
    dr: Optional[int]
    traffic: Optional[int]
    relevance_score: float
    matching_keywords: List[str]

    class Config:
        from_attributes = True