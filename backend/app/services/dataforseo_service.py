import requests
import base64
from typing import List, Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DataForSEOService:
    def __init__(self):
        self.login = settings.DATAFORSEO_LOGIN
        self.password = settings.DATAFORSEO_PASSWORD
        self.base_url = "https://api.dataforseo.com/v3"

    def _get_auth_header(self):
        if not self.login or not self.password:
            return None
        credentials = f"{self.login}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def get_website_pages_keywords(self, domain: str, limit: int = 1000) -> List[Dict[str, any]]:
        """
        Extract up to 1000 pages and their keywords from DataForSEO
        """
        headers = self._get_auth_header()
        if not headers:
            logger.warning("DataForSEO credentials not configured")
            return []

        try:
            # Get pages ranking data
            endpoint = f"{self.base_url}/serp/google/organic/live/regular"

            payload = [{
                "domain": domain,
                "limit": limit,
                "include_subdomains": True,
                "load_rank_absolute": True,
                "filters": ["rank_absolute", "<=", 100]
            }]

            response = requests.post(
                endpoint,
                json=payload,
                headers=headers
            )

            if response.status_code != 200:
                logger.error(f"DataForSEO API error: {response.status_code}")
                return []

            data = response.json()
            pages_data = []

            if data.get("tasks") and len(data["tasks"]) > 0:
                task = data["tasks"][0]
                if task.get("result") and len(task["result"]) > 0:
                    items = task["result"][0].get("items", [])

                    for item in items[:limit]:
                        page_info = {
                            "url": item.get("url"),
                            "keywords": self._extract_keywords(item),
                            "position": item.get("rank_absolute"),
                            "search_volume": item.get("keyword_data", {}).get("search_volume")
                        }
                        pages_data.append(page_info)

            return pages_data

        except Exception as e:
            logger.error(f"Error fetching DataForSEO data for {domain}: {e}")
            return []

    def _extract_keywords(self, item: Dict) -> List[str]:
        """
        Extract keywords from DataForSEO response item
        """
        keywords = []

        # Get main keyword
        if item.get("keyword"):
            keywords.append(item["keyword"])

        # Get related keywords if available
        if item.get("keyword_data", {}).get("keyword_info", {}).get("related_keywords"):
            related = item["keyword_data"]["keyword_info"]["related_keywords"]
            keywords.extend(related[:10])  # Limit to top 10 related keywords

        return keywords

dataforseo_service = DataForSEOService()