from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import User, Website, Import, Page
from app.api.endpoints.auth import get_current_user
from app.schemas.admin import DashboardStats, WebsiteDetail

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for admin"""

    total_websites = db.query(Website).count()
    total_imports = db.query(Import).count()
    total_pages = db.query(Page).count()
    total_users = db.query(User).count()

    # Get average metrics
    avg_dr = db.query(Website.dr).filter(Website.dr.isnot(None)).scalar() or 0
    avg_traffic = db.query(Website.traffic).filter(Website.traffic.isnot(None)).scalar() or 0

    # Recent imports
    recent_imports = db.query(Import).order_by(Import.created_at.desc()).limit(5).all()

    return DashboardStats(
        total_websites=total_websites,
        total_imports=total_imports,
        total_pages=total_pages,
        total_users=total_users,
        avg_dr=avg_dr,
        avg_traffic=avg_traffic,
        recent_imports=[
            {
                "id": imp.id,
                "filename": imp.filename,
                "status": imp.status,
                "created_at": imp.created_at
            }
            for imp in recent_imports
        ]
    )

@router.get("/websites/{website_id}", response_model=WebsiteDetail)
def get_website_detail(
    website_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a website"""

    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    pages = db.query(Page).filter(Page.website_id == website_id).limit(100).all()

    return WebsiteDetail(
        id=website.id,
        url=website.url,
        email=website.email,
        price=website.price,
        dr=website.dr,
        traffic=website.traffic,
        keywords_data=website.keywords_data,
        created_at=website.created_at,
        updated_at=website.updated_at,
        pages=[
            {
                "url": page.url,
                "keywords": page.keywords,
                "vector_id": page.vector_id
            }
            for page in pages
        ]
    )

@router.delete("/websites/{website_id}")
def delete_website(
    website_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a website and all its data"""

    website = db.query(Website).filter(Website.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    # Delete pages first
    db.query(Page).filter(Page.website_id == website_id).delete()

    # Delete website
    db.delete(website)
    db.commit()

    return {"message": "Website deleted successfully"}