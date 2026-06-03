"""FastAPI app — AI Memory Engine SaaS backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.db import engine
from app.models.schema import Base
from app.api import auth, projects, billing


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(billing.router,  prefix="/api/v1")


@app.get("/")
def root():
    return {"name": settings.APP_NAME, "version": settings.VERSION, "status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}
