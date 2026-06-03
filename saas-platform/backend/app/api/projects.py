"""Project routes — CRUD, index, ask, search, stats."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.services.auth import get_current_user_id
from app.core.db import get_db
from app.models.schema import Project, FileMemory, FunctionMemory, Session, Decision

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    org_id: str

class AskRequest(BaseModel):
    query: str
    max_tokens: int = 3000

class DecisionCreate(BaseModel):
    title: str
    decision: str
    reason: str = ""
    tags: list[str] = []


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.get("/")
async def list_projects(org_id: str, user_id: str = Depends(get_current_user_id),
                        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.org_id == org_id))
    projects = result.scalars().all()
    return {"projects": [{"id": p.id, "name": p.name, "language": p.language,
                          "framework": p.framework, "created_at": p.created_at} for p in projects]}


@router.post("/")
async def create_project(req: ProjectCreate, user_id: str = Depends(get_current_user_id),
                         db: AsyncSession = Depends(get_db)):
    project = Project(org_id=req.org_id, name=req.name, description=req.description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return {"id": project.id, "name": project.name, "created_at": project.created_at}


@router.get("/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(get_current_user_id),
                      db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str, user_id: str = Depends(get_current_user_id),
                         db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    await db.delete(project)
    await db.commit()
    return {"status": "deleted"}


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/{project_id}/stats")
async def project_stats(project_id: str, user_id: str = Depends(get_current_user_id),
                        db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    files     = await db.scalar(select(func.count()).where(FileMemory.project_id == project_id))
    functions = await db.scalar(select(func.count()).where(FunctionMemory.project_id == project_id))
    sessions  = await db.scalar(select(func.count()).where(Session.project_id == project_id))
    decisions = await db.scalar(select(func.count()).where(Decision.project_id == project_id))

    # Total tokens saved
    saved_result = await db.execute(
        select(func.sum(Session.tokens_original - Session.tokens_optimized))
        .where(Session.project_id == project_id))
    tokens_saved = saved_result.scalar() or 0

    return {
        "files": files, "functions": functions,
        "sessions": sessions, "decisions": decisions,
        "tokens_saved": tokens_saved,
    }


# ── Sessions ──────────────────────────────────────────────────────────────────

@router.post("/{project_id}/sessions")
async def log_session(project_id: str, req: AskRequest,
                      tokens_original: int = 0, tokens_optimized: int = 0,
                      user_id: str = Depends(get_current_user_id),
                      db: AsyncSession = Depends(get_db)):
    savings_pct = 0.0
    if tokens_original > 0:
        savings_pct = round((1 - tokens_optimized / tokens_original) * 100, 1)

    session = Session(
        project_id=project_id,
        request=req.query,
        tokens_original=tokens_original,
        tokens_optimized=tokens_optimized,
        savings_pct=savings_pct,
    )
    db.add(session)
    await db.commit()
    return {"status": "ok", "savings_pct": savings_pct}


@router.get("/{project_id}/sessions")
async def list_sessions(project_id: str, limit: int = 20,
                        user_id: str = Depends(get_current_user_id),
                        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Session).where(Session.project_id == project_id)
        .order_by(Session.created_at.desc()).limit(limit))
    sessions = result.scalars().all()
    return {"sessions": [{"id": s.id, "request": s.request,
                          "savings_pct": s.savings_pct,
                          "tokens_saved": s.tokens_original - s.tokens_optimized,
                          "created_at": s.created_at} for s in sessions]}


# ── Decisions ─────────────────────────────────────────────────────────────────

@router.post("/{project_id}/decisions")
async def add_decision(project_id: str, req: DecisionCreate,
                       user_id: str = Depends(get_current_user_id),
                       db: AsyncSession = Depends(get_db)):
    import json
    decision = Decision(
        project_id=project_id, title=req.title,
        decision=req.decision, reason=req.reason,
        tags=json.dumps(req.tags),
    )
    db.add(decision)
    await db.commit()
    return {"status": "ok", "id": decision.id}


@router.get("/{project_id}/decisions")
async def list_decisions(project_id: str, user_id: str = Depends(get_current_user_id),
                         db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Decision).where(Decision.project_id == project_id)
        .order_by(Decision.created_at.desc()))
    decisions = result.scalars().all()
    return {"decisions": [{"id": d.id, "title": d.title, "decision": d.decision,
                           "reason": d.reason, "created_at": d.created_at} for d in decisions]}
