"""Requires TEST_DATABASE_URL pointing to a dedicated PostgreSQL database."""
import os, uuid
from decimal import Decimal
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.models.entities import User, Account, LedgerEntry, Transfer
from app.services.transfers import move

@pytest.fixture
def db():
    url=os.getenv("TEST_DATABASE_URL")
    if not url: pytest.skip("TEST_DATABASE_URL not configured; PostgreSQL integration test not run")
    engine=create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
        s.rollback()
    Base.metadata.drop_all(engine)
    engine.dispose()

def test_balanced_transfer_and_idempotency(db):
    user=User(email=f"{uuid.uuid4()}@example.org",password_hash="test")
    db.add(user);db.flush()
    a=Account(user_id=user.id,balance=Decimal("100.00"))
    b=Account(user_id=user.id,balance=Decimal("0.00"))
    db.add_all([a,b]);db.commit()
    t,replayed=move(db,user.id,a.id,b.id,Decimal("30.00"),"sample-key-123")
    db.commit()
    assert not replayed
    again,replayed=move(db,user.id,a.id,b.id,Decimal("30.00"),"sample-key-123")
    db.commit()
    assert replayed and again.id==t.id
    db.refresh(a);db.refresh(b)
    assert a.balance==Decimal("70.00") and b.balance==Decimal("30.00")
    entries=db.execute(select(LedgerEntry).where(LedgerEntry.transfer_id==t.id)).scalars().all()
    assert len(entries)==2
    assert sum((e.amount if e.direction=="credit" else -e.amount for e in entries),Decimal(0))==0
