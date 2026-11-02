import os
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import User, Account, Transfer, LedgerEntry
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.schemas.api import Register, Login, TransferRequest, FundingRequest, AccountResponse
from app.services.transfers import move, ensure_system_account, SYSTEM_ACCOUNT_ID
router = APIRouter()
oauth = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user(token: str=Depends(oauth), db: Session=Depends(get_db)):
    user = db.get(User, decode_token(token))
    if not user: raise HTTPException(401, "Unknown user")
    return user

def owned(db, user, account_id):
    a = db.get(Account, account_id)
    if not a or a.user_id != user.id or a.system: raise HTTPException(404, "Account not found")
    return a

def key_header(key: str=Header(min_length=8, max_length=128, alias="Idempotency-Key")):
    return key

@router.post("/auth/register", status_code=201)
def register(data: Register, db: Session=Depends(get_db)):
    if db.execute(select(User.id).where(User.email==str(data.email).lower())).first(): raise HTTPException(409, "Email already registered")
    user = User(email=str(data.email).lower(), password_hash=hash_password(data.password))
    db.add(user)
    try: db.commit()
    except Exception:
        db.rollback(); raise
    return {"id":user.id, "email":user.email}

@router.post("/auth/login")
def login(data: Login, db: Session=Depends(get_db)):
    user = db.execute(select(User).where(User.email==str(data.email).lower())).scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash): raise HTTPException(401, "Invalid credentials")
    return {"access_token":create_token(user.id),"token_type":"bearer"}

@router.get("/users/me")
def me(user: User=Depends(current_user)):
    return {"id":user.id,"email":user.email}

@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(user: User=Depends(current_user), db: Session=Depends(get_db)):
    a=Account(user_id=user.id)
    db.add(a); db.commit(); db.refresh(a)
    return a

@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(user: User=Depends(current_user), db: Session=Depends(get_db)):
    return db.execute(select(Account).where(Account.user_id==user.id).order_by(Account.id)).scalars().all()

@router.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, user: User=Depends(current_user), db: Session=Depends(get_db)):
    return owned(db,user,account_id)

@router.post("/accounts/{account_id}/freeze")
def freeze(account_id: str, user: User=Depends(current_user), db: Session=Depends(get_db)):
    a=owned(db,user,account_id)
    a.status="frozen"; db.commit()
    return {"status":a.status}

@router.post("/transfers", status_code=201)
def transfer(data: TransferRequest, key: str=Depends(key_header), user: User=Depends(current_user), db: Session=Depends(get_db)):
    owned(db,user,data.source_id)
    try:
        t,replay=move(db,user.id,data.source_id,data.destination_id,data.amount,key)
        db.commit()
        return {"transfer_id":t.id,"replayed":replay,"amount":str(t.amount)}
    except Exception:
        db.rollback(); raise

@router.post("/funding", status_code=201)
def funding(data: FundingRequest, key: str=Depends(key_header), user: User=Depends(current_user), db: Session=Depends(get_db)):
    owned(db,user,data.account_id)
    if os.getenv("ENABLE_SIMULATED_FUNDING", "false").lower() != "true": raise HTTPException(403,"Simulated funding disabled")
    try:
        ensure_system_account(db)
        t,replay=move(db,user.id,SYSTEM_ACCOUNT_ID,data.account_id,data.amount,key,"funding")
        db.commit()
        return {"transfer_id":t.id,"replayed":replay}
    except Exception:
        db.rollback(); raise

@router.post("/withdrawals", status_code=201)
def withdraw(data: FundingRequest, key: str=Depends(key_header), user: User=Depends(current_user), db: Session=Depends(get_db)):
    owned(db,user,data.account_id)
    try:
        ensure_system_account(db)
        t,replay=move(db,user.id,data.account_id,SYSTEM_ACCOUNT_ID,data.amount,key,"withdrawal")
        db.commit()
        return {"transfer_id":t.id,"replayed":replay}
    except Exception:
        db.rollback(); raise

@router.get("/accounts/{account_id}/transactions")
def history(account_id: str, limit: int=Query(20,ge=1,le=100), offset: int=Query(0,ge=0), user: User=Depends(current_user), db: Session=Depends(get_db)):
    owned(db,user,account_id)
    ts=db.execute(select(Transfer).where(or_(Transfer.source_id==account_id,Transfer.destination_id==account_id)).order_by(Transfer.created_at.desc(),Transfer.id.desc()).offset(offset).limit(limit)).scalars().all()
    return [{"id":t.id,"kind":t.kind,"amount":str(t.amount),"source_id":t.source_id,"destination_id":t.destination_id,"created_at":t.created_at.isoformat()} for t in ts]

@router.get("/transfers/{transfer_id}")
def transfer_detail(transfer_id: str, user: User=Depends(current_user), db: Session=Depends(get_db)):
    t=db.get(Transfer,transfer_id)
    if not t or (t.actor_id != user.id and not user.is_admin): raise HTTPException(404,"Transfer not found")
    return {"id":t.id,"kind":t.kind,"amount":str(t.amount),"source_id":t.source_id,"destination_id":t.destination_id}

@router.get("/health")
def health(): return {"status":"ok"}

@router.get("/ready")
def ready(db: Session=Depends(get_db)):
    from sqlalchemy import text
    db.execute(text("SELECT 1"))
    return {"status":"ready"}
