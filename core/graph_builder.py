"""Dependency Graph Builder — builds a NetworkX knowledge graph from memory."""
import json
from pathlib import Path
from storage import db

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False


def build_graph(project_path: str):
    """Build and store the knowledge graph. Returns NetworkX DiGraph (or None)."""
    files = db.get_all_files(project_path)
    functions = db.get_all_functions(project_path)

    # Map: import module → file paths that define it
    module_to_file = _build_module_map(files)

    # Add file → file edges (import relationships)
    for file in files:
        file_path = file["file_path"]
        imports = json.loads(file.get("imports") or "[]")
        for imp in imports:
            target = _resolve_import(imp, file_path, module_to_file)
            if target:
                db.upsert_graph_edge(project_path, file_path, target, "imports")

    # Add function → function edges (call relationships)
    fn_name_to_file: dict[str, str] = {}
    for fn in functions:
        fn_name_to_file[fn["name"]] = fn["file_path"]
        fn_name_to_file[fn.get("qualified_name") or fn["name"]] = fn["file_path"]

    for fn in functions:
        callees = json.loads(fn.get("callees") or "[]")
        source = f"{fn['file_path']}::{fn['name']}"
        for callee in callees:
            callee_base = callee.split("(")[0].split(".")[-1]
            if callee_base in fn_name_to_file:
                target = f"{fn_name_to_file[callee_base]}::{callee_base}"
                if source != target:
                    db.upsert_graph_edge(project_path, source, target, "calls")

    if not HAS_NX:
        return None

    G = nx.DiGraph()
    edges = db.get_all_edges(project_path)
    for edge in edges:
        G.add_edge(edge["source"], edge["target"],
                   relationship=edge["relationship"])

    return G


def _build_module_map(files: list[dict]) -> dict[str, str]:
    """Map module-like names to their file paths."""
    mapping = {}
    for f in files:
        path = f["file_path"]
        # foo/bar/baz.py → foo.bar.baz, bar.baz, baz
        p = Path(path)
        parts = list(p.with_suffix("").parts)
        for i in range(len(parts)):
            module_name = ".".join(parts[i:])
            mapping[module_name] = path
    return mapping


def _resolve_import(imp: str, from_file: str, module_map: dict) -> str | None:
    """Try to resolve an import string to a file path in the project."""
    # Direct match
    if imp in module_map:
        return module_map[imp]
    # Partial match (last component)
    last = imp.split(".")[-1]
    if last in module_map:
        return module_map[last]
    return None


def get_related_files(project_path: str, file_path: str, depth: int = 2) -> list[str]:
    """Return files related to file_path via the knowledge graph (BFS)."""
    if not HAS_NX:
        return _simple_bfs(project_path, file_path, depth)

    G = _load_graph(project_path)
    if file_path not in G:
        return []

    related = set()
    frontier = {file_path}
    for _ in range(depth):
        next_frontier = set()
        for node in frontier:
            for neighbor in list(G.predecessors(node)) + list(G.successors(node)):
                if neighbor not in related and "::" not in neighbor:
                    next_frontier.add(neighbor)
                    related.add(neighbor)
        frontier = next_frontier

    related.discard(file_path)
    return list(related)


def _load_graph(project_path: str):
    G = nx.DiGraph()
    edges = db.get_all_edges(project_path)
    for edge in edges:
        G.add_edge(edge["source"], edge["target"],
                   relationship=edge["relationship"])
    return G


def _simple_bfs(project_path: str, file_path: str, depth: int) -> list[str]:
    """BFS without networkx using raw edge data."""
    edges = db.get_all_edges(project_path)
    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        s, t = edge["source"], edge["target"]
        adjacency.setdefault(s, []).append(t)
        adjacency.setdefault(t, []).append(s)

    visited = {file_path}
    frontier = {file_path}
    for _ in range(depth):
        next_frontier = set()
        for node in frontier:
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_frontier.add(neighbor)
        frontier = next_frontier

    visited.discard(file_path)
    return [v for v in visited if "::" not in v]


def visualize_ascii(project_path: str, max_nodes: int = 30) -> str:
    """Return a simple ASCII representation of the graph."""
    edges = db.get_all_edges(project_path)
    file_edges = [(e["source"], e["target"], e["relationship"])
                  for e in edges if "::" not in e["source"] and "::" not in e["target"]]

    if not file_edges:
        return "(no file-level relationships found)"

    lines = ["File Dependency Graph:", "=" * 40]
    seen = set()
    for src, tgt, rel in file_edges[:max_nodes]:
        arrow = "--[imports]-->" if rel == "imports" else f"--[{rel}]-->"
        line = f"  {src} {arrow} {tgt}"
        if line not in seen:
            seen.add(line)
            lines.append(line)

    return "\n".join(lines)
