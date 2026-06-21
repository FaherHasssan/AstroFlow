import logging
import urllib.parse
import uuid
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from pydantic import ValidationError

from app.core.config import settings
from app.models.domain import SystemBudgetLedger, LeadRecord, Tenant
from app.services.lead_parser import LeadParserService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Standard synchronous SQLAlchemy engine mapped explicitly for worker thread architecture
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(name="app.workers.tasks.process_incoming_lead", bind=True, max_retries=3)
def process_incoming_lead(self, source: str, raw_payload: dict):
    """
    Entry point for every inbound webhook (Meta, Google, etc).
    Parses the raw provider payload, persists it as a LeadRecord, then
    delegates to process_lead_and_generate_links for the budget-aware
    WhatsApp link generation step.

    ASSUMPTION: this currently resolves the single active Tenant row in
    the database (the platform isn't routing webhooks per-tenant yet).
    If you need multiple agencies/tenants on separate webhook endpoints,
    that resolution needs to happen here (e.g. via a tenant id embedded
    in the webhook URL or a per-tenant verify token) instead of picking
    the first active tenant.
    """
    try:
        parsed = LeadParserService.parse_and_normalize(source, raw_payload)
    except ValidationError as e:
        # Bad/incomplete payload from the provider - not worth retrying.
        logger.warning(f"Discarding unparseable lead from source '{source}': {e}")
        return

    with SessionLocal() as db:
        try:
            tenant = db.execute(
                select(Tenant).where(Tenant.is_active.is_(True))
            ).scalars().first()

            if not tenant:
                logger.error(f"No active tenant configured. Dropping lead from source '{source}'.")
                return

            lead = LeadRecord(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                customer_name=parsed["customer_name"],
                target_phone_number=parsed["target_phone_number"],
                raw_webhook_payload=parsed["raw_webhook_payload"],
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)

            logger.info(f"Persisted lead {lead.id} for tenant {tenant.id} from source '{source}'.")

            lead_id, tenant_id = str(lead.id), str(tenant.id)

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to ingest incoming lead from source '{source}': {str(e)}")
            raise self.retry(exc=e, countdown=10)

    process_lead_and_generate_links.delay(lead_id, tenant_id)


@celery_app.task(name="app.workers.tasks.process_lead_and_generate_links")
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
