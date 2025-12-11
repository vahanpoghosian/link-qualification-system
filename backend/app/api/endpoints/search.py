from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import Website
from app.services.vector_service import vector_service
from app.schemas.search import SearchRequest, SearchResult

router = APIRouter()

@router.post("/", response_model=List[SearchResult])
def search_websites(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Public endpoint for searching websites by keyword and filters.
    Uses vector similarity search for relevance ranking.
    """

    # First, perform vector similarity search with the keyword
    vector_results = vector_service.search_similar(
        query=request.keyword,
        top_k=100  # Get more results initially for filtering
    )

    # Extract unique website URLs from vector results
    website_urls = list(set([r["website_url"] for r in vector_results]))

    # Build database query with filters
    query = db.query(Website).filter(Website.url.in_(website_urls))

    # Apply DR filter
    if request.min_dr is not None:
        query = query.filter(Website.dr >= request.min_dr)
    if request.max_dr is not None:
        query = query.filter(Website.dr <= request.max_dr)

    # Apply traffic filter
    if request.min_traffic is not None:
        query = query.filter(Website.traffic >= request.min_traffic)

    # Apply price filter
    if request.max_price is not None:
        query = query.filter(Website.price <= request.max_price)

    websites = query.all()

    # Create relevance score map from vector results
    relevance_scores = {}
    for result in vector_results:
        url = result["website_url"]
        if url not in relevance_scores:
            relevance_scores[url] = result["score"]

    # Build search results with relevance scores
    search_results = []
    for website in websites:
        search_results.append(SearchResult(
            id=website.id,
            url=website.url,
            email=website.email,
            price=website.price,
            dr=website.dr,
            traffic=website.traffic,
            relevance_score=relevance_scores.get(website.url, 0),
            matching_keywords=self._get_matching_keywords(
                website.url, vector_results
            )
        ))

    # Sort by relevance score
    search_results.sort(key=lambda x: x.relevance_score, reverse=True)

    # Limit results
    if request.limit:
        search_results = search_results[:request.limit]

    return search_results

def _get_matching_keywords(website_url: str, vector_results: List[dict]) -> List[str]:
    """Extract matching keywords for a specific website from vector results"""
    keywords = []
    for result in vector_results:
        if result["website_url"] == website_url:
            if result.get("keywords"):
                # Extract first few keywords
                kw_list = result["keywords"].split()[:5]
                keywords.extend(kw_list)

    return list(set(keywords))[:10]  # Return unique keywords, max 10

@router.get("/filters")
def get_search_filters(db: Session = Depends(get_db)):
    """Get available filter ranges based on existing data"""

    dr_min = db.query(Website.dr).filter(Website.dr.isnot(None)).order_by(Website.dr).first()
    dr_max = db.query(Website.dr).filter(Website.dr.isnot(None)).order_by(Website.dr.desc()).first()

    traffic_min = db.query(Website.traffic).filter(Website.traffic.isnot(None)).order_by(Website.traffic).first()
    traffic_max = db.query(Website.traffic).filter(Website.traffic.isnot(None)).order_by(Website.traffic.desc()).first()

    price_min = db.query(Website.price).order_by(Website.price).first()
    price_max = db.query(Website.price).order_by(Website.price.desc()).first()

    return {
        "dr_range": {
            "min": dr_min[0] if dr_min else 0,
            "max": dr_max[0] if dr_max else 100
        },
        "traffic_range": {
            "min": traffic_min[0] if traffic_min else 0,
            "max": traffic_max[0] if traffic_max else 1000000
        },
        "price_range": {
            "min": price_min[0] if price_min else 0,
            "max": price_max[0] if price_max else 10000
        }
    }