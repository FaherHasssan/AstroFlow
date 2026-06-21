import httpx
import logging
import hashlib
import hmac
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetaAPIClient:
    def __init__(self, app_secret: str, access_token: str):
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v19.0"

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify the X-Hub-Signature-256 header sent by Meta to ensure the payload is authentic.
        """
        if not signature or not signature.startswith("sha256="):
            return False

        expected_signature = hmac.new(
            self.app_secret.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature.split("=")[1], expected_signature)

    async def fetch_lead_details(self, leadgen_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the actual lead details from Meta using the leadgen_id provided in the webhook.
        """
        url = f"{self.base_url}/{leadgen_id}"
        params = {
            "access_token": self.access_token,
            "fields": "created_time,id,ad_id,form_id,field_data"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Parse field_data cleanly
                lead_info = {"raw": data}
                for field in data.get("field_data", []):
                    lead_info[field["name"]] = field["values"][0] if field["values"] else None
                
                return lead_info
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch Meta lead {leadgen_id}: {e}")
                return None
