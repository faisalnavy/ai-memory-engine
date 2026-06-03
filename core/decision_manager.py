"""Decision Memory Manager — store and retrieve architectural decisions."""
import json
from storage import db


def add_decision(project_path: str, title: str, decision: str,
                 reason: str = "", alternatives: list[str] = None,
                 tags: list[str] = None) -> None:
    db.add_decision(project_path, {
        "title": title,
        "decision": decision,
        "reason": reason,
        "alternatives": alternatives or [],
        "tags": tags or [],
    })


def get_decisions(project_path: str, limit: int = 10) -> list[dict]:
    return db.get_recent_decisions(project_path, limit)


def format_decisions_markdown(decisions: list[dict]) -> str:
    if not decisions:
        return ""
    lines = ["## Architectural Decisions\n"]
    for d in decisions:
        lines.append(f"### {d['title']} ({d['created_at'][:10]})")
        lines.append(f"{d['decision']}")
        if d.get("reason"):
            lines.append(f"**Why:** {d['reason']}")
        alts = json.loads(d.get("alternatives") or "[]")
        if alts:
            lines.append(f"**Alternatives considered:** {', '.join(alts)}")
        lines.append("")
    return "\n".join(lines)
