"""
SQLAlchemy models for the multi-tenant SaaS platform.
Tables: organizations → users → projects → memory_files/functions/sessions/decisions
"""
from datetime import datetime
from sqlalchemy import (Column, String, Integer, Float, Boolean, DateTime,
                        Text, ForeignKey, UniqueConstraint, Enum as SAEnum)
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid, enum


def new_uuid(): return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────────

class PlanType(str, enum.Enum):
    free       = "free"
    pro        = "pro"
    team       = "team"
    enterprise = "enterprise"

class OrgRole(str, enum.Enum):
    owner  = "owner"
    admin  = "admin"
    member = "member"


# ── Organizations ─────────────────────────────────────────────────────────────

class Organization(Base):
    __tablename__ = "organizations"

    id            = Column(String, primary_key=True, default=new_uuid)
    name          = Column(String(120), nullable=False)
    slug          = Column(String(60), unique=True, nullable=False)
    plan          = Column(SAEnum(PlanType), default=PlanType.free)
    stripe_customer_id     = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    max_projects  = Column(Integer, default=3)
    max_members   = Column(Integer, default=1)
    created_at    = Column(DateTime, default=datetime.utcnow)

    members  = relationship("OrganizationMember", back_populates="organization", cascade="all, delete")
    projects = relationship("Project",            back_populates="organization", cascade="all, delete")


class OrganizationMember(Base):
    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("org_id", "user_id"),)

    id      = Column(String, primary_key=True, default=new_uuid)
    org_id  = Column(String, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"),         nullable=False)
    role    = Column(SAEnum(OrgRole), default=OrgRole.member)
    joined_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="members")
    user         = relationship("User",         back_populates="org_memberships")


# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id             = Column(String, primary_key=True, default=new_uuid)
    email          = Column(String(255), unique=True, nullable=False)
    hashed_password= Column(String, nullable=False)
    full_name      = Column(String(120), nullable=True)
    is_active      = Column(Boolean, default=True)
    is_verified    = Column(Boolean, default=False)
    avatar_url     = Column(String, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    last_login     = Column(DateTime, nullable=True)

    org_memberships = relationship("OrganizationMember", back_populates="user", cascade="all, delete")
    api_keys        = relationship("ApiKey", back_populates="user", cascade="all, delete")


# ── API Keys ──────────────────────────────────────────────────────────────────

class ApiKey(Base):
    __tablename__ = "api_keys"

    id         = Column(String, primary_key=True, default=new_uuid)
    user_id    = Column(String, ForeignKey("users.id"), nullable=False)
    key_hash   = Column(String, unique=True, nullable=False)
    name       = Column(String(80), nullable=False)
    last_used  = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="api_keys")


# ── Projects ──────────────────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id           = Column(String, primary_key=True, default=new_uuid)
    org_id       = Column(String, ForeignKey("organizations.id"), nullable=False)
    name         = Column(String(120), nullable=False)
    description  = Column(Text, nullable=True)
    language     = Column(String(40), nullable=True)
    framework    = Column(String(60), nullable=True)
    architecture = Column(String(60), nullable=True)
    s3_prefix    = Column(String, nullable=True)    # where .memory/ is stored in S3
    is_public    = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization",  back_populates="projects")
    files        = relationship("FileMemory",    back_populates="project", cascade="all, delete")
    functions    = relationship("FunctionMemory",back_populates="project", cascade="all, delete")
    decisions    = relationship("Decision",      back_populates="project", cascade="all, delete")
    sessions     = relationship("Session",       back_populates="project", cascade="all, delete")


# ── File Memory ───────────────────────────────────────────────────────────────

class FileMemory(Base):
    __tablename__ = "file_memory"
    __table_args__ = (UniqueConstraint("project_id", "file_path"),)

    id          = Column(String, primary_key=True, default=new_uuid)
    project_id  = Column(String, ForeignKey("projects.id"), nullable=False)
    file_path   = Column(String, nullable=False)
    purpose     = Column(Text, nullable=True)
    public_apis = Column(Text, nullable=True)   # JSON
    imports     = Column(Text, nullable=True)   # JSON
    exports     = Column(Text, nullable=True)   # JSON
    risk_level  = Column(String(10), default="low")
    file_hash   = Column(String(64), nullable=True)
    line_count  = Column(Integer, default=0)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="files")


# ── Function Memory ───────────────────────────────────────────────────────────

class FunctionMemory(Base):
    __tablename__ = "function_memory"

    id            = Column(String, primary_key=True, default=new_uuid)
    project_id    = Column(String, ForeignKey("projects.id"), nullable=False)
    file_path     = Column(String, nullable=False)
    name          = Column(String(120), nullable=False)
    qualified_name= Column(String(255), nullable=True)
    args          = Column(Text, nullable=True)   # JSON
    return_type   = Column(String(120), nullable=True)
    docstring     = Column(Text, nullable=True)
    summary       = Column(Text, nullable=True)
    is_async      = Column(Boolean, default=False)
    is_public     = Column(Boolean, default=True)
    line_start    = Column(Integer, default=0)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="functions")


# ── Decisions ─────────────────────────────────────────────────────────────────

class Decision(Base):
    __tablename__ = "decisions"

    id         = Column(String, primary_key=True, default=new_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title      = Column(String(255), nullable=False)
    decision   = Column(Text, nullable=False)
    reason     = Column(Text, nullable=True)
    tags       = Column(String, nullable=True)   # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="decisions")


# ── Sessions ──────────────────────────────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id                = Column(String, primary_key=True, default=new_uuid)
    project_id        = Column(String, ForeignKey("projects.id"), nullable=False)
    request           = Column(Text, nullable=True)
    files_changed     = Column(Text, nullable=True)  # JSON
    tokens_original   = Column(Integer, default=0)
    tokens_optimized  = Column(Integer, default=0)
    savings_pct       = Column(Float, default=0.0)
    created_at        = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="sessions")


# ── Usage / Billing ───────────────────────────────────────────────────────────

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id           = Column(String, primary_key=True, default=new_uuid)
    org_id       = Column(String, ForeignKey("organizations.id"), nullable=False)
    project_id   = Column(String, nullable=True)
    month        = Column(String(7), nullable=False)  # YYYY-MM
    queries      = Column(Integer, default=0)
    tokens_saved = Column(Integer, default=0)
    files_indexed= Column(Integer, default=0)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
