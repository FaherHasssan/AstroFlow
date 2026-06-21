import logging
import urllib.parse
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.domain import SystemBudgetLedger, LeadRecord

logger = logging.getLogger(__name__)

# Standard synchronous SQLAlchemy engine mapped explicitly for worker thread architecture
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_lead_and_generate_links(lead_id: str, tenant_id: str):
    """
    Asynchronous processing module managing automated payload workflows.
    Executes a hard SELECT FOR UPDATE row-level lock against the PostgreSQL table 
    to guarantee zero budget slippage during extreme simultaneous traffic spikes.
    """
    with SessionLocal() as db:
        try:
            # Atomic lock: The transaction blocks other workers acting on the same ledger row
            stmt = select(SystemBudgetLedger).where(
                SystemBudgetLedger.tenant_id == tenant_id
            ).with_for_update()
            
            ledger = db.execute(stmt).scalar_one_or_none()
            
            if not ledger:
                logger.error(f"Ledger isolation lookup failed. Tenant '{tenant_id}' absent. Aborting sequence.")
                return
            
            # --- ATOMIC BUDGET MONITORING LOCK ---
            if ledger.is_locked or ledger.current_day_spend >= ledger.daily_spend_limit:
                logger.critical(
                    f"ABORT COMMAND ISSUED: Budget limit of {ledger.daily_spend_limit} AED "
                    f"exceeded or tenant locked. Halting pipeline for {tenant_id}."
                )
                return

            # Proceed to load the securely parsed webhook record payload
            lead_stmt = select(LeadRecord).where(LeadRecord.id == lead_id)
            lead = db.execute(lead_stmt).scalar_one_or_none()
            
            if not lead:
                logger.error(f"Lead lookup isolation failed. ID '{lead_id}' absent.")
                return

            # Construct Zero-Cost WhatsApp Integration Links
            # Using E.164 standardized target_phone_number stored in the LeadRecord
            agency_text = f"Hi {lead.customer_name}, we've received your property inquiry."
            encoded_text = urllib.parse.quote(agency_text)
            
            # WhatsApp URL structure requires stripping the standard '+' prefix from the E.164 string
            wa_phone = lead.target_phone_number.replace("+", "")
            tracked_url = f"https://wa.me/{wa_phone}?text={encoded_text}"
            
            lead.tracked_wa_link = tracked_url
            lead.is_synced = True
            
            # Explicitly increment the daily consumption tracker directly proportional to 
            # the established simulated operational compute parameter metrics.
            ledger.current_day_spend += settings.COST_PER_DATABASE_WRITE
            
            # Proactively flip the safety boolean if the boundary is breached on this precise transaction
            if ledger.current_day_spend >= ledger.daily_spend_limit:
                ledger.is_locked = True
                logger.warning(f"Tenant '{tenant_id}' just breached daily boundaries. Lock applied.")
            
            # Flush changes and release the PostgreSQL FOR UPDATE row lock
            db.commit()
            logger.info(f"Successfully configured Zero-Cost link structure for Lead {lead_id}.")

        except Exception as e:
            # Revert states and instantly unlock database rows if application crashes
            db.rollback()
            logger.error(f"Transaction aborted. Row-lock released. Internal System Error: {str(e)}")
            raise
