import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GoogleAdsAPIClient:
    def __init__(self, developer_token: str):
        self.developer_token = developer_token
        # Google Ads webhook authorization key verification logic usually happens at the API gateway
        # This service handles the explicit parsing of the payload structure.

    def verify_google_key(self, provided_key: str, expected_key: str) -> bool:
        """
        Google validates webhooks by sending a Google-Key parameter in the header or query.
        """
        return provided_key == expected_key

    def parse_webhook_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses the specific structure of a Google Ads Lead Form webhook payload.
        Google sends user column data in an array of dictionaries.
        """
        try:
            user_data = payload.get("user_column_data", [])
            lead_info = {"raw": payload}
            
            for field in user_data:
                col_name = field.get("column_id", "").lower()
                val = field.get("string_value")
                
                # Map Google's specific column IDs to our internal schema
                if "name" in col_name or col_name == "full_name":
                    lead_info["full_name"] = val
                elif "phone" in col_name or col_name == "phone_number":
                    lead_info["phone_number"] = val
                elif "email" in col_name:
                    lead_info["email"] = val
            
            return lead_info
        except Exception as e:
            logger.error(f"Failed to parse Google Ads webhook payload: {str(e)}")
            return {}
