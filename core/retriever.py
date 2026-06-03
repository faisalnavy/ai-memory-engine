"""Retrieval Engine — 6-step algorithm to build minimal context packages."""
import json
import re
from storage import db
from core import graph_builder
from models.memory_types import ContextPackage

# Rough token estimator: 1 token ≈ 4 characters
def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def retrieve(project_path: str, query: str, max_tokens: int = 3000) -> ContextPackage:
    pkg = ContextPackage(query=query)

    # Step 1: Analyze query — extract keywords
    keywords = _extract_keywords(query)

    # Step 2: Find relevant files via FTS5
    relevant_files = []
    for kw in keywords[:3]:
        results = db.search_files_fts(project_path, kw, limit=5)
        for r in results:
            if not any(f["file_path"] == r["file_path"] for f in relevant_files):
                relevant_files.append(r)
    pkg.relevant_files = relevant_files[:8]

    # Step 3: Find relevant functions via FTS5
    relevant_functions = []
    for kw in keywords[:3]:
        results = db.search_functions_fts(project_path, kw, limit=5)
        for r in results:
            if not any(f["name"] == r["name"] and f["file_path"] == r["file_path"]
                       for f in relevant_functions):
                relevant_functions.append(r)
    pkg.relevant_functions = relevant_functions[:12]

    # Step 4: Traverse dependency graph to add related files
    graph_related = []
    for file in pkg.relevant_files[:3]:
        related = graph_builder.get_related_files(project_path, file["file_path"], depth=1)
        for rel_path in related[:3]:
            if not any(f["file_path"] == rel_path for f in pkg.relevant_files):
                rows = db.execute(project_path,
                    "SELECT * FROM file_memory WHERE project_path=? AND file_path=?",
                    (project_path, rel_path))
                if rows:
                    graph_related.append(rows[0])
    pkg.relevant_files.extend(graph_related[:4])

    # Step 5: Load project DNA + compressed memory + recent decisions
    dna = db.get_project_dna(project_path)
    if dna:
        pkg.project_dna = dict(dna)

    compressed = db.get_compressed_memory(project_path, limit=2)
    pkg.compressed_memory = [c["content"] for c in compressed]

    decisions = db.get_recent_decisions(project_path, limit=5)
    pkg.recent_decisions = decisions

    # Step 6: Build context and estimate tokens
    markdown = pkg.as_markdown()
    pkg.token_estimate = _estimate_tokens(markdown)

    # Trim if over budget
    while pkg.token_estimate > max_tokens and (pkg.relevant_files or pkg.relevant_functions):
        if pkg.relevant_files:
            pkg.relevant_files.pop()
        elif pkg.relevant_functions:
            pkg.relevant_functions.pop()
        pkg.token_estimate = _estimate_tokens(pkg.as_markdown())

    # Estimate original (raw files) token cost
    total_lines = sum(f.get("line_count", 0) for f in pkg.relevant_files)
    pkg.original_token_estimate = max(total_lines * 5, pkg.token_estimate * 10)

    return pkg


def _extract_keywords(query: str) -> list[str]:
    # Remove stop words, split on whitespace and punctuation
    stop_words = {"the", "a", "an", "is", "in", "on", "at", "to", "for",
                  "of", "and", "or", "but", "how", "what", "where", "when",
                  "does", "do", "can", "i", "me", "my", "we", "our"}
    words = re.split(r"[\s\W]+", query.lower())
    keywords = [w for w in words if w and len(w) > 2 and w not in stop_words]
    # Prefer longer, more specific words first
    keywords.sort(key=len, reverse=True)
    return keywords[:10]
