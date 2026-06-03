"""Memory Compression Engine — compress N sessions into intelligence blocks."""
import json
from collections import Counter
from storage import db

COMPRESS_THRESHOLD = 10  # compress after this many sessions


def should_compress(project_path: str) -> bool:
    sessions = db.get_uncompressed_sessions(project_path)
    return len(sessions) >= COMPRESS_THRESHOLD


def compress_sessions(project_path: str, force: bool = False) -> str | None:
    sessions = db.get_uncompressed_sessions(project_path)
    if not force and len(sessions) < COMPRESS_THRESHOLD:
        return None

    if not sessions:
        return None

    content = _build_compression_block(sessions)
    session_ids = [s["id"] for s in sessions]
    session_range = f"{session_ids[0]}-{session_ids[-1]}"

    db.save_compressed_block(project_path, content, session_range, len(sessions))
    db.mark_sessions_compressed(project_path, session_ids)

    return content


def _build_compression_block(sessions: list[dict]) -> str:
    all_files: list[str] = []
    all_bugs: list[str] = []
    all_lessons: list[str] = []
    all_decisions: list[str] = []
    requests: list[str] = []

    for s in sessions:
        if s.get("request"):
            requests.append(s["request"][:100])
        files = json.loads(s.get("files_changed") or "[]")
        all_files.extend(files)
        bugs = json.loads(s.get("bugs_fixed") or "[]")
        all_bugs.extend(bugs)
        lessons = json.loads(s.get("lessons_learned") or "[]")
        all_lessons.extend(lessons)
        decisions = json.loads(s.get("decisions_made") or "[]")
        all_decisions.extend(decisions)

    # Most frequently changed files
    file_counts = Counter(all_files).most_common(10)

    lines = [
        f"## Compressed Memory ({len(sessions)} sessions)",
        "",
        "### Most Active Files",
    ]
    for fp, count in file_counts:
        lines.append(f"- `{fp}` (changed {count}×)")

    if all_bugs:
        lines.append("\n### Bugs Fixed")
        for b in list(dict.fromkeys(all_bugs))[:10]:  # deduplicated
            lines.append(f"- {b}")

    if all_lessons:
        lines.append("\n### Lessons Learned")
        for lesson in list(dict.fromkeys(all_lessons))[:10]:
            lines.append(f"- {lesson}")

    if all_decisions:
        lines.append("\n### Decisions Made")
        for d in list(dict.fromkeys(all_decisions))[:10]:
            lines.append(f"- {d}")

    if requests:
        lines.append("\n### Recent Work Summary")
        for req in requests[-5:]:
            lines.append(f"- {req}")

    return "\n".join(lines)
