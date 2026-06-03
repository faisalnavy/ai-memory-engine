"""Auth routes — register, login, refresh, logout, API keys."""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import (hash_password, verify_password,
                                create_access_token, create_refresh_token,
                                decode_token, generate_api_key,
                                get_current_user_id)
from app.core.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    from app.models.schema import User
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "access_token":  create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type":    "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name},
    }


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    from app.models.schema import User
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(403, "Account disabled")

    user.last_login = datetime.utcnow()
    await db.commit()

    return {
        "access_token":  create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type":    "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name},
    }


@router.post("/refresh")
async def refresh(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")
    return {"access_token": create_access_token(payload["sub"]), "token_type": "bearer"}


@router.get("/me")
async def me(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    from app.models.schema import User
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    return {"id": user.id, "email": user.email, "full_name": user.full_name,
            "created_at": user.created_at, "last_login": user.last_login}


@router.post("/api-keys")
async def create_api_key(name: str, user_id: str = Depends(get_current_user_id),
                         db: AsyncSession = Depends(get_db)):
    from app.models.schema import ApiKey
    raw, hashed = generate_api_key()
    key = ApiKey(user_id=user_id, key_hash=hashed, name=name)
    db.add(key)
    await db.commit()
    return {"key": raw, "name": name, "note": "Save this key — it won't be shown again."}
