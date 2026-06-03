"""
FastAPI backend for the AI Memory Engine Desktop App.
Runs as a local server on port 7842, started by Electron.
"""
import sys
import argparse
from pathlib import Path

# Add memory-engine core to path
BASE = Path(__file__).parent.parent.parent / "memory-engine"
sys.path.insert(0, str(BASE))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Install: pip install fastapi uvicorn pydantic")
    sys.exit(1)

from storage import db
from core import (dna, file_summarizer, function_summarizer,
                  graph_builder, retriever, context_builder,
                  compressor, updater, session_manager, decision_manager)

app = FastAPI(title="AI Memory Engine API", version="1.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Models ────────────────────────────────────────────────────────────────────

class ProjectRequest(BaseModel):
    project_path: str

class AskRequest(BaseModel):
    project_path: str
    query: str
    max_tokens: int = 3000

class DecisionRequest(BaseModel):
    project_path: str
    title: str
    decision: str
    reason: str = ""
    tags: list[str] = []


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/init")
def init_project(req: ProjectRequest):
    try:
        memory_dir = Path(req.project_path) / ".memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        db.init_db(req.project_path)
        project_dna = dna.generate_and_save(req.project_path)
        return {
            "status": "ok",
            "name": project_dna.name,
            "language": project_dna.language,
            "framework": project_dna.framework,
            "architecture": project_dna.architecture,
            "entry_points": project_dna.entry_points,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/index")
def index_project(req: ProjectRequest):
    try:
        results = file_summarizer.summarize_directory(req.project_path)
        fn_count = function_summarizer.summarize_all_functions(req.project_path, results)
        graph_builder.build_graph(req.project_path)
        stats = db.get_stats(req.project_path)
        return {"status": "ok", **stats}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/update")
def update_project(req: ProjectRequest):
    try:
        result = updater.update_project(req.project_path)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/ask")
def ask(req: AskRequest):
    try:
        pkg = retriever.retrieve(req.project_path, req.query, req.max_tokens)
        report = context_builder.savings_report(pkg)
        context_md = context_builder.build_context_string(pkg)

        session_id = session_manager.start_session(req.project_path)
        session_manager.save_session(req.project_path, session_id, req.query)

        return {
            "status": "ok",
            "context": context_md,
            "report": report,
            "files": [f["file_path"] for f in pkg.relevant_files],
            "functions": [f["name"] for f in pkg.relevant_functions],
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/search")
def search(req: AskRequest):
    try:
        files = db.search_files_fts(req.project_path, req.query, limit=20)
        functions = db.search_functions_fts(req.project_path, req.query, limit=20)
        return {"status": "ok", "files": files, "functions": functions}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/stats")
def stats(project_path: str):
    try:
        raw = db.get_stats(project_path)
        project_dna = db.get_project_dna(project_path)
        return {"status": "ok", "stats": raw, "dna": dict(project_dna) if project_dna else {}}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/graph")
def graph(project_path: str):
    try:
        edges = db.get_all_edges(project_path)
        return {"status": "ok", "edges": edges}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/sessions")
def sessions(project_path: str):
    try:
        s = db.get_uncompressed_sessions(project_path)
        compressed = db.get_compressed_memory(project_path)
        return {"status": "ok", "sessions": s, "compressed": compressed}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/decisions")
def decisions(project_path: str):
    try:
        d = db.get_recent_decisions(project_path, limit=50)
        return {"status": "ok", "decisions": d}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/decisions")
def add_decision(req: DecisionRequest):
    try:
        decision_manager.add_decision(
            req.project_path, req.title, req.decision, req.reason, tags=req.tags)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/compress")
def compress(req: ProjectRequest):
    try:
        result = compressor.compress_sessions(req.project_path, force=True)
        return {"status": "ok", "content": result or ""}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/projects")
def list_projects():
    """Return recently used projects from a simple cache file."""
    import json
    cache = Path.home() / ".memory_engine_projects.json"
    if cache.exists():
        return {"projects": json.loads(cache.read_text())}
    return {"projects": []}


@app.post("/projects/add")
def add_project(req: ProjectRequest):
    import json
    cache = Path.home() / ".memory_engine_projects.json"
    projects = json.loads(cache.read_text()) if cache.exists() else []
    if req.project_path not in projects:
        projects.insert(0, req.project_path)
        projects = projects[:20]
    cache.write_text(json.dumps(projects))
    return {"status": "ok", "projects": projects}


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7842)
    args = parser.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
