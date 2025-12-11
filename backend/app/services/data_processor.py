from sqlalchemy.orm import Session
from app.models.models import Website, Page, Import
from app.services.ahrefs_service import ahrefs_service
from app.services.dataforseo_service import dataforseo_service
from app.services.vector_service import vector_service
import logging
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def process_website_data(websites_data: list, import_id: int, db: Session):
    """
    Background task to process imported websites:
    1. Get DR and traffic from Ahrefs
    2. Get keywords from DataForSEO
    3. Vectorize keywords with Pinecone
    4. Store everything in database
    """
    try:
        import_record = db.query(Import).filter(Import.id == import_id).first()

        for idx, website_data in enumerate(websites_data):
            try:
                # Clean URL
                url = website_data['url']
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"

                domain = urlparse(url).netloc

                # Check if website already exists
                existing = db.query(Website).filter(Website.url == url).first()
                if existing:
                    website = existing
                else:
                    website = Website(
                        url=url,
                        email=website_data['email'],
                        price=website_data['price']
                    )
                    db.add(website)
                    db.flush()

                # Step 1: Get Ahrefs metrics
                logger.info(f"Fetching Ahrefs data for {domain}")
                ahrefs_data = ahrefs_service.get_domain_metrics(domain)
                website.dr = ahrefs_data.get("dr")
                website.traffic = ahrefs_data.get("traffic")

                # Step 2: Get keywords from DataForSEO
                logger.info(f"Fetching DataForSEO data for {domain}")
                pages_data = dataforseo_service.get_website_pages_keywords(domain)

                if pages_data:
                    # Step 3: Vectorize and store in Pinecone
                    logger.info(f"Vectorizing keywords for {domain}")
                    vector_ids = vector_service.store_vectors(url, pages_data)

                    # Store pages in database
                    for page_data, vector_id in zip(pages_data[:len(vector_ids)], vector_ids):
                        page = Page(
                            website_id=website.id,
                            url=page_data["url"],
                            keywords=page_data["keywords"],
                            vector_id=vector_id
                        )
                        db.add(page)

                    website.keywords_data = {
                        "total_pages": len(pages_data),
                        "vectorized_pages": len(vector_ids)
                    }
                    website.vector_ids = vector_ids

                # Update import progress
                import_record.processed_websites = idx + 1
                db.commit()

                logger.info(f"Processed website {idx + 1}/{len(websites_data)}: {url}")

            except Exception as e:
                logger.error(f"Error processing website {website_data.get('url')}: {e}")
                db.rollback()
                continue

        # Mark import as completed
        import_record.status = "completed"
        import_record.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Import {import_id} completed successfully")

    except Exception as e:
        logger.error(f"Fatal error in process_website_data: {e}")
        if import_record:
            import_record.status = "failed"
            db.commit()