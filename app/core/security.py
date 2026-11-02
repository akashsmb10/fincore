from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import HTTPException, status
from app.core.config import settings
hasher = PasswordHash.recommended()
def hash_password(password: str): return hasher.hash(password)
def verify_password(password: str, hashed: str): return hasher.verify(password, hashed)
def create_token(user_id: str):
    if not settings.jwt_secret: raise RuntimeError("JWT_SECRET must be configured")
    return jwt.encode({"sub":user_id,"exp":datetime.now(timezone.utc)+timedelta(minutes=settings.jwt_exp_minutes)}, settings.jwt_secret, algorithm="HS256")
def decode_token(token: str):
    try:
        if not settings.jwt_secret: raise ValueError("missing JWT secret")
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])["sub"]
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
