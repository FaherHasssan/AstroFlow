from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import Dict, Any
import logging

from app.services.meta_api import MetaAPIClient
from app.services.google_ads import GoogleAdsAPIClient
from app.services.whatsapp_api import WhatsAppAPIClient
from app.core.config import settings
from app.workers.tasks import process_incoming_lead

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services with environment variables (mock or real)
# In production, these should be handled securely, possibly injected via Depends()
meta_client = MetaAPIClient(
    app_secret=settings.META_APP_SECRET if hasattr(settings, 'META_APP_SECRET') else "mock_secret",
    access_token=settings.META_ACCESS_TOKEN if hasattr(settings, 'META_ACCESS_TOKEN') else "mock_token"
)

google_client = GoogleAdsAPIClient(
    developer_token=settings.GOOGLE_ADS_DEVELOPER_TOKEN if hasattr(settings, 'GOOGLE_ADS_DEVELOPER_TOKEN') else "mock_token"
)

whatsapp_client = WhatsAppAPIClient(
    phone_number_id=settings.WHATSAPP_PHONE_ID if hasattr(settings, 'WHATSAPP_PHONE_ID') else "mock_phone_id",
    access_token=settings.WHATSAPP_TOKEN if hasattr(settings, 'WHATSAPP_TOKEN') else "mock_token"
)

@router.get("/meta")
async def verify_meta_webhook(
    request: Request,
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    """
    Mandatory Meta Webhook Verification Endpoint.
    Facebook/Instagram sends a GET request here to verify the endpoint during setup.
    """
    VERIFY_TOKEN = "astroflow_secure_token" # Should be in settings
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("Meta Webhook Successfully Verified!")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/meta")
async def receive_meta_lead(request: Request, x_hub_signature_256: str = Header(None)):
    """
    Receives live Lead Ads data from Meta (Facebook/Instagram).
    """
    payload = await request.body()
    
    # 1. Verify Signature
    if not meta_client.verify_signature(payload, x_hub_signature_256):
        logger.warning("Invalid Meta Webhook Signature Detected.")
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()
    
    # 2. Extract Leadgen ID and fetch data
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "leadgen":
                leadgen_id = change.get("value", {}).get("lead_id")
                if leadgen_id:
                    # Async task delegation to Celery worker 
                    # We pass the ID and the worker fetches it to keep the endpoint fast
                    process_incoming_lead.delay(source="meta", raw_payload={"leadgen_id": leadgen_id})
                    
    return {"status": "ok"}

@router.post("/google")
async def receive_google_lead(request: Request, google_key: str = None):
    """
    Receives live Lead Form data directly from Google Ads.
    """
    # 1. Verify Google Source
    expected_key = "astroflow_google_secure_key" # Should be in settings
    if not google_client.verify_google_key(google_key, expected_key):
        raise HTTPException(status_code=401, detail="Invalid Google verification key")

    payload = await request.json()
    
    # 2. Delegate to worker
    process_incoming_lead.delay(source="google", raw_payload=payload)
    
    return {"status": "ok"}
