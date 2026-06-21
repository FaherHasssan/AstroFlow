import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WhatsAppAPIClient:
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    async def send_template_message(self, to_phone: str, template_name: str, language_code: str = "en", components: list = None) -> bool:
        """
        Sends an approved WhatsApp template message to the newly ingested lead.
        """
        # Ensure phone number formatting (E.164 without the '+')
        if to_phone.startswith("+"):
            to_phone = to_phone[1:]

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
                "components": components or []
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"WhatsApp template '{template_name}' successfully sent to {to_phone}")
                return True
            except httpx.HTTPError as e:
                logger.error(f"Failed to send WhatsApp message to {to_phone}: {e}")
                if hasattr(e, "response") and e.response:
                    logger.error(f"Response: {e.response.text}")
                return False

    async def send_text_message(self, to_phone: str, message: str) -> bool:
        """
        Sends a standard text message (only valid if inside the 24-hour customer service window).
        """
        if to_phone.startswith("+"):
            to_phone = to_phone[1:]

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"WhatsApp text successfully sent to {to_phone}")
                return True
            except httpx.HTTPError as e:
                logger.error(f"Failed to send WhatsApp text to {to_phone}: {e}")
                return False
