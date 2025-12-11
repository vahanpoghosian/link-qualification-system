import requests
from typing import Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AhrefsService:
    def __init__(self):
        self.api_key = settings.AHREFS_API_KEY
        self.base_url = "https://api.ahrefs.com/v2"

    def get_domain_metrics(self, domain: str) -> Dict[str, Optional[int]]:
        """
        Get DR (Domain Rating) and traffic data from Ahrefs API
        """
        if not self.api_key:
            logger.warning("Ahrefs API key not configured")
            return {"dr": None, "traffic": None}

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }

            # Get domain rating
            dr_response = requests.get(
                f"{self.base_url}/domain-rating",
                params={"target": domain},
                headers=headers
            )

            # Get organic traffic
            traffic_response = requests.get(
                f"{self.base_url}/organic-traffic",
                params={"target": domain},
                headers=headers
            )

            dr = None
            traffic = None

            if dr_response.status_code == 200:
                dr_data = dr_response.json()
                dr = int(dr_data.get("domain_rating", 0))

            if traffic_response.status_code == 200:
                traffic_data = traffic_response.json()
                traffic = int(traffic_data.get("traffic", 0))

            return {"dr": dr, "traffic": traffic}

        except Exception as e:
            logger.error(f"Error fetching Ahrefs data for {domain}: {e}")
            return {"dr": None, "traffic": None}

ahrefs_service = AhrefsService()