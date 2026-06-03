"""Session Memory Manager — track coding sessions and what changed."""
import uuid
from storage import db


def start_session(project_path: str) -> str:
    return str(uuid.uuid4())


def save_session(project_path: str, session_id: str, request: str,
                 files_changed: list[str] = None,
                 functions_changed: list[str] = None,
                 decisions_made: list[str] = None,
                 bugs_fixed: list[str] = None,
                 lessons_learned: list[str] = None) -> None:
    db.add_session(project_path, session_id, {
        "request": request,
        "files_changed": files_changed or [],
        "functions_changed": functions_changed or [],
        "decisions_made": decisions_made or [],
        "bugs_fixed": bugs_fixed or [],
        "lessons_learned": lessons_learned or [],
    })


def get_sessions(project_path: str) -> list[dict]:
    return db.get_uncompressed_sessions(project_path)
