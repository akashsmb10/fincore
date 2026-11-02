import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, DateTime, UniqueConstraint, CheckConstraint, Index, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (CheckConstraint("balance >= 0", name="nonnegative_balance"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[str] = mapped_column(String(12), default="active", nullable=False)
    system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Transfer(Base):
    __tablename__ = "transfers"
    __table_args__ = (UniqueConstraint("actor_id", "idempotency_key", name="uq_actor_idempotency"), CheckConstraint("amount > 0", name="positive_transfer"), Index("ix_transfer_from_created", "source_id", "created_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    destination_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18,2), nullable=False)
    kind: Mapped[str] = mapped_column(String(12), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (CheckConstraint("amount > 0", name="positive_entry"), Index("ix_ledger_account", "account_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    transfer_id: Mapped[str] = mapped_column(ForeignKey("transfers.id"), nullable=False)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    direction: Mapped[str] = mapped_column(String(6), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18,2), nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
