"""
Auth service — JWT tokens, password hashing, API key management.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: str, expires_minutes: int = None) -> str:
    exp = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=exp),
        "iat": datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return None

# ── API Keys ──────────────────────────────────────────────────────────────────

def generate_api_key() -> tuple[str, str]:
    """Returns (raw_key, hashed_key). Store only the hash."""
    raw  = "mem_" + secrets.token_urlsafe(32)
    h    = hashlib.sha256(raw.encode()).hexdigest()
    return raw, h

def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

# ── Dependency ────────────────────────────────────────────────────────────────

async def get_current_user_id(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)
) -> str:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(creds.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload["sub"]
