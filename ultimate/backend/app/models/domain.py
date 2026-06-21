import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 mapped models."""
    pass


class Tenant(Base):
    """
    Multi-tenant isolation barrier. Stores high-level organization metadata.
    """
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Cross-relations for cascading data bounds
    budget_ledger: Mapped["SystemBudgetLedger"] = relationship("SystemBudgetLedger", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    leads: Mapped[list["LeadRecord"]] = relationship("LeadRecord", back_populates="tenant", cascade="all, delete-orphan")


class SystemBudgetLedger(Base):
    """
    Strict atomic budget boundary for FinOps. 
    Enforces spend tracking per tenant at the PostgreSQL row level.
    """
    __tablename__ = "system_budget_ledgers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), unique=True)
    
    # Financial metrics enforcing the 1.00 AED/day limits
    daily_spend_limit: Mapped[float] = mapped_column(Float, default=1.00)
    current_day_spend: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Absolute circuit breaker. If True, no resources execute for this tenant
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    last_reset_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="budget_ledger")


class LeadRecord(Base):
    """
    Immutable tracking ledger for parsed real-estate inquiries and webhook payloads.
    """
    __tablename__ = "lead_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Target phone standardizes tightly onto E.164 format via the parsing service
    target_phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    
    raw_webhook_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Generated Zero-Cost URL Integration Path
    tracked_wa_link: Mapped[str] = mapped_column(String, nullable=True)
    
    # Lifecycle statuses
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="leads")
