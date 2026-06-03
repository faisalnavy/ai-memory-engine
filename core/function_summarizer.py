"""Function Summarizer — stores function-level memory from parsed file info."""
from pathlib import Path
from parsers.base_parser import parse_file, should_index
from storage import db


def summarize_functions(project_path: str, file_path: str, functions=None) -> int:
    """Summarize and store functions from a file. Returns count stored."""
    if functions is None:
        if not should_index(file_path):
            return 0
        info = parse_file(file_path)
        if info is None:
            return 0
        functions = info.functions

    try:
        rel_path = str(Path(file_path).relative_to(project_path))
    except ValueError:
        rel_path = file_path

    count = 0
    for fn in functions:
        fn_data = {
            "file_path": rel_path,
            "name": fn.name,
            "qualified_name": fn.qualified_name or fn.name,
            "args": fn.args,
            "return_type": fn.return_type,
            "callers": fn.callers,
            "callees": fn.callees,
            "decorators": fn.decorators,
            "is_async": fn.is_async,
            "is_public": fn.is_public,
            "docstring": fn.docstring,
            "summary": fn.summary,
            "line_start": fn.line_start,
            "line_end": fn.line_end,
        }
        db.upsert_function_memory(project_path, fn_data)
        count += 1

    return count


def summarize_all_functions(project_path: str, file_results: list[dict]) -> int:
    """Summarize functions from pre-parsed file results."""
    total = 0
    for result in file_results:
        functions = result.get("functions", [])
        file_info = result.get("file_info", {})
        file_path = file_info.get("file_path", "")
        if file_path:
            count = summarize_functions(project_path, file_path, functions)
            total += count
    return total
