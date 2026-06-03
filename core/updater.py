"""Incremental Updater — re-index only changed files using hash comparison."""
from pathlib import Path
from parsers.base_parser import compute_hash, should_index
from storage import db
from core import file_summarizer, function_summarizer, graph_builder


def get_changed_files(project_path: str) -> list[str]:
    """Return list of file paths that have changed since last index."""
    root = Path(project_path)
    changed = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if not should_index(str(file_path)):
            continue

        try:
            rel_path = str(file_path.relative_to(project_path))
        except ValueError:
            continue

        new_hash = compute_hash(str(file_path))
        stored_hash = db.get_file_hash(project_path, rel_path)

        if stored_hash != new_hash:
            changed.append(str(file_path))

    return changed


def update_project(project_path: str, progress_callback=None) -> dict:
    """Run incremental update. Returns summary of what changed."""
    changed = get_changed_files(project_path)

    if not changed:
        return {"changed": 0, "functions_updated": 0}

    fn_count = 0
    for i, file_path in enumerate(changed):
        result = file_summarizer.summarize_file(project_path, file_path)
        if result:
            fn_count += function_summarizer.summarize_functions(
                project_path, file_path, result.get("functions", []))
        if progress_callback:
            progress_callback(i + 1, len(changed), file_path)

    # Rebuild graph edges for changed files
    graph_builder.build_graph(project_path)

    return {"changed": len(changed), "functions_updated": fn_count}


def watch_project(project_path: str, on_change=None) -> None:
    """Watch for file changes and trigger incremental updates.
    Requires the `watchdog` package.
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        raise ImportError("Install watchdog: pip install watchdog")

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory and should_index(event.src_path):
                result = file_summarizer.summarize_file(project_path, event.src_path)
                if result:
                    function_summarizer.summarize_functions(
                        project_path, event.src_path, result.get("functions", []))
                    graph_builder.build_graph(project_path)
                if on_change:
                    on_change(event.src_path)

        on_created = on_modified

    observer = Observer()
    observer.schedule(Handler(), project_path, recursive=True)
    observer.start()
    return observer
