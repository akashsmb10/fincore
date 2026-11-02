"""Atomic double-entry postings. PostgreSQL is required for row locking."""
import hashlib, json
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.entities import Account, Transfer, LedgerEntry, AuditLog

SYSTEM_ACCOUNT_ID = "00000000-0000-0000-0000-000000000001"

def ensure_system_account(db: Session):
    account = db.get(Account, SYSTEM_ACCOUNT_ID)
    if account is None:
        account = Account(id=SYSTEM_ACCOUNT_ID, user_id=None, system=True, status="active", balance=Decimal("0.00"))
        db.add(account)
        db.flush()
    return account

def move(db: Session, actor_id: str, source_id: str, dest_id: str, amount: Decimal, key: str, kind: str="transfer"):
    """Caller commits/rolls back. Locks user idempotency row via user row lock before inspecting key."""
    from app.models.entities import User
    db.execute(select(User).where(User.id == actor_id).with_for_update()).scalar_one()
    payload = json.dumps([source_id, dest_id, str(amount), kind], separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    previous = db.execute(select(Transfer).where(Transfer.actor_id==actor_id, Transfer.idempotency_key==key)).scalar_one_or_none()
    if previous:
        if previous.request_hash != digest: raise HTTPException(409, "Idempotency key reused for a different request")
        return previous, True
    if source_id == dest_id: raise HTTPException(400, "Source and destination must differ")
    if amount <= 0 or amount.as_tuple().exponent < -2: raise HTTPException(422, "Invalid amount")
    accounts = db.execute(select(Account).where(Account.id.in_([source_id,dest_id])).order_by(Account.id).with_for_update()).scalars().all()
    by_id = {a.id:a for a in accounts}
    if len(by_id)!=2: raise HTTPException(404, "Account not found")
    source, dest = by_id[source_id], by_id[dest_id]
    if source.currency != dest.currency: raise HTTPException(400, "Currency mismatch")
    if source.status != "active" or dest.status != "active": raise HTTPException(409, "Inactive account")
    if kind == "transfer" and (source.system or dest.system): raise HTTPException(403, "System account cannot be used for internal transfers")
    if kind == "funding" and (not source.system or dest.system): raise HTTPException(400, "Invalid funding accounts")
    if kind == "withdrawal" and (source.system or not dest.system): raise HTTPException(400, "Invalid withdrawal accounts")
    if source.balance < amount and not source.system: raise HTTPException(409, "Insufficient funds")
    if not source.system: source.balance -= amount
    if not dest.system: dest.balance += amount
    t = Transfer(actor_id=actor_id, source_id=source_id, destination_id=dest_id, amount=amount, kind=kind, idempotency_key=key, request_hash=digest)
    db.add(t); db.flush()
    db.add_all([LedgerEntry(transfer_id=t.id, account_id=source_id, direction="debit", amount=amount),LedgerEntry(transfer_id=t.id, account_id=dest_id, direction="credit", amount=amount)])
    db.add(AuditLog(actor_id=actor_id, action=kind, metadata_json={"transfer_id":t.id}))
    db.flush()
    return t, False
