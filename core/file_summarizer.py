"""File Summarizer — parses files and stores file memory."""
from pathlib import Path
from parsers.base_parser import parse_file, should_index
from storage import db


def summarize_file(project_path: str, file_path: str) -> dict | None:
    if not should_index(file_path):
        return None

    info = parse_file(file_path)
    if info is None:
        return None

    # Make file_path relative for cleaner storage
    try:
        rel_path = str(Path(file_path).relative_to(project_path))
    except ValueError:
        rel_path = file_path

    file_data = {
        "file_path": rel_path,
        "purpose": info.purpose,
        "public_apis": info.public_apis,
        "imports": info.imports,
        "exports": info.exports,
        "dependencies": info.dependencies,
        "risk_level": info.risk_level,
        "file_hash": info.file_hash,
        "line_count": info.line_count,
    }

    db.upsert_file_memory(project_path, file_data)
    db.set_file_hash(project_path, rel_path, info.file_hash)

    return {"file_info": file_data, "functions": info.functions}


def summarize_directory(project_path: str, progress_callback=None) -> list[dict]:
    root = Path(project_path)
    results = []
    files = [f for f in root.rglob("*") if f.is_file() and should_index(str(f))]

    for i, file_path in enumerate(files):
        result = summarize_file(project_path, str(file_path))
        if result:
            results.append(result)
        if progress_callback:
            progress_callback(i + 1, len(files), str(file_path))

    return results
