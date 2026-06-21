import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
import redis

# Configuration bindings pulled securely from the runtime environment
from app.core.config import settings

logger = logging.getLogger("daily_reset_worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

# Execute synchronous database and cache connections for the isolated script
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def execute_daily_budget_reset():
    """
    CRON EXECUTION TARGET: Triggers exactly at 00:00 UAE Time.
    Automated zero-downtime maintenance worker that wipes isolated telemetry structures 
    and revives systems that were blocked by the daily budget failsafe boundary.
    """
    logger.info("Initializing Daily Automated Budget Reset Sequence...")
    
    # ---------------------------------------------------------
    # 1. UPSTASH REDIS: Wipe Memory-Volatile Cost Trackers
    # ---------------------------------------------------------
    try:
        keys_wiped = 0
        # Scan specifically for the 'tenant:*:cost:*' signature
        for key in redis_client.scan_iter("tenant:*:cost:*"):
            redis_client.delete(key)
            keys_wiped += 1
        logger.info(f"[SUCCESS] Purged {keys_wiped} accumulated daily spend keys from Upstash Redis cache.")
    except Exception as e:
        logger.critical(f"[EMERGENCY] Redis Cache Flush Failed during nightly reset. Error: {str(e)}")
        sys.exit(1)

    # ---------------------------------------------------------
    # 2. SUPABASE POSTGRESQL: Unlock FinOps Ledgers
    # ---------------------------------------------------------
    try:
        with SessionLocal() as db:
            from app.models.domain import SystemBudgetLedger
            
            # Atomic bulk UPDATE overriding the 'is_locked' flags 
            # and dropping accumulated daily spend dynamically to 0.00
            stmt = (
                update(SystemBudgetLedger)
                .values(
                    current_day_spend=0.0,
                    is_locked=False,
                    last_reset_date=datetime.utcnow()
                )
            )
            result = db.execute(stmt)
            db.commit()
            
            logger.info(f"[SUCCESS] Reprovisioned and unlocked {result.rowcount} tenant ledger records inside PostgreSQL.")
    except Exception as e:
        logger.critical(f"[EMERGENCY] PostgreSQL FinOps Ledger Reset Failed. Traffic will remain blocked! Error: {str(e)}")
        sys.exit(1)
        
    # ---------------------------------------------------------
    # 3. VERIFICATION & SHUTDOWN
    # ---------------------------------------------------------
    logger.info("Daily Automated Budget Reset Sequence Completed flawlessly. Traffic ingress pipeline re-opened.")

if __name__ == "__main__":
    execute_daily_budget_reset()
