import sys
import sqlite3
import json
from pathlib import Path
from typing import Any

# When running as a PyInstaller bundle, use sys._MEIPASS for bundled files
if getattr(sys, 'frozen', False):
    SCHEMA_PATH = Path(sys._MEIPASS) / "storage" / "schema.sql"
else:
    SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db_path(project_path: str) -> Path:
    return Path(project_path) / ".memory" / "memory.db"


def get_connection(project_path: str) -> sqlite3.Connection:
    db_path = get_db_path(project_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(project_path: str) -> None:
    conn = get_connection(project_path)
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)
    conn.commit()
    conn.close()


def execute(project_path: str, sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection(project_path)
    try:
        cursor = conn.execute(sql, params)
        conn.commit()
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def execute_many(project_path: str, sql: str, params_list: list[tuple]) -> None:
    conn = get_connection(project_path)
    try:
        conn.executemany(sql, params_list)
        conn.commit()
    finally:
        conn.close()


def upsert_file_memory(project_path: str, data: dict) -> None:
    sql = """
    INSERT INTO file_memory
        (project_path, file_path, purpose, public_apis, imports, exports,
         dependencies, risk_level, file_hash, line_count, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(project_path, file_path) DO UPDATE SET
        purpose=excluded.purpose,
        public_apis=excluded.public_apis,
        imports=excluded.imports,
        exports=excluded.exports,
        dependencies=excluded.dependencies,
        risk_level=excluded.risk_level,
        file_hash=excluded.file_hash,
        line_count=excluded.line_count,
        updated_at=datetime('now')
    """
    execute(project_path, sql, (
        project_path,
        data["file_path"],
        data.get("purpose", ""),
        json.dumps(data.get("public_apis", [])),
        json.dumps(data.get("imports", [])),
        json.dumps(data.get("exports", [])),
        json.dumps(data.get("dependencies", [])),
        data.get("risk_level", "low"),
        data.get("file_hash", ""),
        data.get("line_count", 0),
    ))


def upsert_function_memory(project_path: str, data: dict) -> None:
    sql = """
    INSERT INTO function_memory
        (project_path, file_path, name, qualified_name, args, return_type,
         callers, callees, decorators, is_async, is_public, docstring, summary,
         line_start, line_end, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(project_path, file_path, name, line_start) DO UPDATE SET
        qualified_name=excluded.qualified_name,
        args=excluded.args,
        return_type=excluded.return_type,
        callers=excluded.callers,
        callees=excluded.callees,
        decorators=excluded.decorators,
        is_async=excluded.is_async,
        is_public=excluded.is_public,
        docstring=excluded.docstring,
        summary=excluded.summary,
        line_end=excluded.line_end,
        updated_at=datetime('now')
    """
    execute(project_path, sql, (
        project_path,
        data["file_path"],
        data["name"],
        data.get("qualified_name", data["name"]),
        json.dumps(data.get("args", [])),
        data.get("return_type", ""),
        json.dumps(data.get("callers", [])),
        json.dumps(data.get("callees", [])),
        json.dumps(data.get("decorators", [])),
        int(data.get("is_async", False)),
        int(data.get("is_public", True)),
        data.get("docstring", ""),
        data.get("summary", ""),
        data.get("line_start", 0),
        data.get("line_end", 0),
    ))


def upsert_graph_edge(project_path: str, source: str, target: str, relationship: str) -> None:
    sql = """
    INSERT OR IGNORE INTO knowledge_graph (project_path, source, target, relationship)
    VALUES (?, ?, ?, ?)
    """
    execute(project_path, sql, (project_path, source, target, relationship))


def get_all_files(project_path: str) -> list[dict]:
    return execute(project_path,
        "SELECT * FROM file_memory WHERE project_path=?", (project_path,))


def get_all_functions(project_path: str) -> list[dict]:
    return execute(project_path,
        "SELECT * FROM function_memory WHERE project_path=?", (project_path,))


def get_all_edges(project_path: str) -> list[dict]:
    return execute(project_path,
        "SELECT * FROM knowledge_graph WHERE project_path=?", (project_path,))


def search_files_fts(project_path: str, query: str, limit: int = 10) -> list[dict]:
    sql = """
    SELECT fm.* FROM file_memory fm
    JOIN file_memory_fts fts ON fm.id = fts.rowid
    WHERE file_memory_fts MATCH ? AND fm.project_path = ?
    ORDER BY rank LIMIT ?
    """
    return execute(project_path, sql, (query, project_path, limit))


def search_functions_fts(project_path: str, query: str, limit: int = 10) -> list[dict]:
    sql = """
    SELECT fnm.* FROM function_memory fnm
    JOIN function_memory_fts fts ON fnm.id = fts.rowid
    WHERE function_memory_fts MATCH ? AND fnm.project_path = ?
    ORDER BY rank LIMIT ?
    """
    return execute(project_path, sql, (query, project_path, limit))


def get_file_hash(project_path: str, file_path: str) -> str | None:
    rows = execute(project_path,
        "SELECT hash FROM file_hashes WHERE project_path=? AND file_path=?",
        (project_path, file_path))
    return rows[0]["hash"] if rows else None


def set_file_hash(project_path: str, file_path: str, hash_val: str) -> None:
    execute(project_path, """
    INSERT INTO file_hashes (project_path, file_path, hash)
    VALUES (?, ?, ?)
    ON CONFLICT(project_path, file_path) DO UPDATE SET hash=excluded.hash, indexed_at=datetime('now')
    """, (project_path, file_path, hash_val))


def get_project_dna(project_path: str) -> dict | None:
    rows = execute(project_path,
        "SELECT * FROM project_dna WHERE project_path=?", (project_path,))
    return rows[0] if rows else None


def upsert_project_dna(project_path: str, data: dict) -> None:
    sql = """
    INSERT INTO project_dna
        (project_path, name, language, languages, framework, database,
         architecture, entry_points, key_services, coding_standards, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(project_path) DO UPDATE SET
        name=excluded.name,
        language=excluded.language,
        languages=excluded.languages,
        framework=excluded.framework,
        database=excluded.database,
        architecture=excluded.architecture,
        entry_points=excluded.entry_points,
        key_services=excluded.key_services,
        coding_standards=excluded.coding_standards,
        updated_at=datetime('now')
    """
    execute(project_path, sql, (
        project_path,
        data.get("name", ""),
        data.get("language", ""),
        json.dumps(data.get("languages", [])),
        data.get("framework", ""),
        data.get("database", ""),
        data.get("architecture", ""),
        json.dumps(data.get("entry_points", [])),
        json.dumps(data.get("key_services", [])),
        json.dumps(data.get("coding_standards", {})),
    ))


def add_session(project_path: str, session_id: str, data: dict) -> None:
    execute(project_path, """
    INSERT INTO session_memory
        (project_path, session_id, request, files_changed, functions_changed,
         decisions_made, bugs_fixed, lessons_learned)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_path, session_id,
        data.get("request", ""),
        json.dumps(data.get("files_changed", [])),
        json.dumps(data.get("functions_changed", [])),
        json.dumps(data.get("decisions_made", [])),
        json.dumps(data.get("bugs_fixed", [])),
        json.dumps(data.get("lessons_learned", [])),
    ))


def get_uncompressed_sessions(project_path: str) -> list[dict]:
    return execute(project_path,
        "SELECT * FROM session_memory WHERE project_path=? AND compressed=0 ORDER BY created_at",
        (project_path,))


def mark_sessions_compressed(project_path: str, session_ids: list[int]) -> None:
    placeholders = ",".join("?" * len(session_ids))
    execute(project_path,
        f"UPDATE session_memory SET compressed=1 WHERE id IN ({placeholders})",
        tuple(session_ids))


def save_compressed_block(project_path: str, content: str, session_range: str, count: int) -> None:
    execute(project_path, """
    INSERT INTO compressed_memory (project_path, session_range, content, session_count)
    VALUES (?, ?, ?, ?)
    """, (project_path, session_range, content, count))


def get_compressed_memory(project_path: str, limit: int = 3) -> list[dict]:
    return execute(project_path,
        "SELECT * FROM compressed_memory WHERE project_path=? ORDER BY created_at DESC LIMIT ?",
        (project_path, limit))


def add_decision(project_path: str, data: dict) -> None:
    execute(project_path, """
    INSERT INTO decision_memory (project_path, title, decision, reason, alternatives, tags)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        project_path,
        data.get("title", ""),
        data.get("decision", ""),
        data.get("reason", ""),
        json.dumps(data.get("alternatives", [])),
        json.dumps(data.get("tags", [])),
    ))


def get_recent_decisions(project_path: str, limit: int = 10) -> list[dict]:
    return execute(project_path,
        "SELECT * FROM decision_memory WHERE project_path=? ORDER BY created_at DESC LIMIT ?",
        (project_path, limit))


def get_stats(project_path: str) -> dict:
    conn = get_connection(project_path)
    try:
        stats = {}
        for table in ["file_memory", "function_memory", "decision_memory",
                      "session_memory", "knowledge_graph"]:
            row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM {table} WHERE project_path=?",
                (project_path,)).fetchone()
            stats[table] = row["cnt"]
        return stats
    finally:
        conn.close()
