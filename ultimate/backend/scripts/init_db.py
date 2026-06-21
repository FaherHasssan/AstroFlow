import os
import logging
from urllib.parse import quote_plus  # <-- Add this import
from sqlalchemy import create_engine
from app.models.domain import Base
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_production_db():
    db_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)
    
    if not db_url or "localhost" in db_url:
        logger.warning("WARNING: You appear to be running this against a local or empty Database URL.")
    
    logger.info(f"Connecting to database to initialize schemas...")
    
    try:
        sync_url = db_url.replace("+asyncpg", "")
        
        # --- ADD THIS BLOCK TO FIX THE PASSWORD ISSUE ---
        # Splitting out the password to safely encode it if it has an '@' or ':'
        if "://" in sync_url and "@" in sync_url:
            protocol, rest = sync_url.split("://", 1)
            credentials, host_db = rest.rsplit("@", 1)
            if ":" in credentials:
                username, password = credentials.split(":", 1)
                # Safely encode special characters in the password
                sync_url = f"{protocol}://{username}:{quote_plus(password)}@{host_db}"
        # ------------------------------------------------
        
        engine = create_engine(sync_url)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Production Database Schemas successfully generated!")
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {str(e)}")

if __name__ == "__main__":
    init_production_db()