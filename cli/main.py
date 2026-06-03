"""Universal AI Coding Memory Engine — CLI Tool."""
import os
import sys
import json
import zipfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import print as rprint
    from rich.markdown import Markdown
except ImportError:
    print("ERROR: Install dependencies first: pip install typer rich")
    sys.exit(1)

from storage import db
from core import dna, file_summarizer, function_summarizer, graph_builder
from core import compressor, retriever, context_builder, updater, session_manager

app = typer.Typer(
    name="memory",
    help="Universal AI Coding Memory Engine — reduce AI token usage by 90-98%",
    add_completion=False,
)
console = Console()


def _get_project_path(path: str | None) -> str:
    return str(Path(path).resolve()) if path else str(Path.cwd())


# ── memory init ──────────────────────────────────────────────────────────────

@app.command()
def init(
    path: str = typer.Argument(None, help="Project path (default: current directory)"),
):
    """Initialize memory system for a project."""
    project_path = _get_project_path(path)
    memory_dir = Path(project_path) / ".memory"

    if memory_dir.exists():
        console.print(f"[yellow]Memory already initialized at {memory_dir}[/yellow]")
        if not typer.confirm("Re-initialize?"):
            return

    with console.status("[bold green]Initializing memory system..."):
        memory_dir.mkdir(parents=True, exist_ok=True)
        db.init_db(project_path)
        project_dna = dna.generate_and_save(project_path)

    console.print(Panel(
        f"[bold green][OK] Memory initialized![/bold green]\n\n"
        f"  Project: [cyan]{project_dna.name}[/cyan]\n"
        f"  Language: [cyan]{project_dna.language}[/cyan]\n"
        f"  Framework: [cyan]{project_dna.framework or 'not detected'}[/cyan]\n"
        f"  Architecture: [cyan]{project_dna.architecture}[/cyan]\n"
        f"  Memory stored at: [dim]{memory_dir}[/dim]\n\n"
        f"  Next step: [bold]memory index[/bold]",
        title="Memory Engine",
        border_style="green",
    ))


# ── memory index ─────────────────────────────────────────────────────────────

@app.command()
def index(
    path: str = typer.Argument(None, help="Project path (default: current directory)"),
):
    """Full project scan and index."""
    project_path = _get_project_path(path)
    memory_dir = Path(project_path) / ".memory"

    if not memory_dir.exists():
        console.print("[red]Not initialized. Run: memory init[/red]")
        raise typer.Exit(1)

    file_count = 0
    fn_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        # Count files first
        from parsers.base_parser import should_index
        all_files = [f for f in Path(project_path).rglob("*")
                     if f.is_file() and should_index(str(f))]
        task = progress.add_task("Indexing files...", total=len(all_files))

        def on_progress(done, total, current_file):
            nonlocal file_count
            file_count = done
            progress.update(task, completed=done,
                            description=f"[cyan]{Path(current_file).name}[/cyan]")

        results = file_summarizer.summarize_directory(project_path, on_progress)
        progress.update(task, completed=len(all_files), description="Building function index...")
        fn_count = function_summarizer.summarize_all_functions(project_path, results)
        progress.update(task, description="Building dependency graph...")
        graph_builder.build_graph(project_path)

    stats = db.get_stats(project_path)
    console.print(Panel(
        f"[bold green][OK] Indexing complete![/bold green]\n\n"
        f"  Files indexed:    [cyan]{stats['file_memory']}[/cyan]\n"
        f"  Functions stored: [cyan]{stats['function_memory']}[/cyan]\n"
        f"  Graph edges:      [cyan]{stats['knowledge_graph']}[/cyan]\n\n"
        f"  Next step: [bold]memory ask \"your question\"[/bold]",
        title="Index Complete",
        border_style="green",
    ))


# ── memory update ─────────────────────────────────────────────────────────────

@app.command()
def update(
    path: str = typer.Argument(None, help="Project path (default: current directory)"),
):
    """Incremental update — only re-index changed files."""
    project_path = _get_project_path(path)

    with console.status("[bold green]Detecting changes..."):
        changed = updater.get_changed_files(project_path)

    if not changed:
        console.print("[green][OK] Everything up to date. No changes detected.[/green]")
        return

    console.print(f"[yellow]Found {len(changed)} changed file(s)[/yellow]")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Updating...", total=len(changed))

        def on_progress(done, total, fp):
            progress.update(task, completed=done,
                            description=f"[cyan]{Path(fp).name}[/cyan]")

        result = updater.update_project(project_path, on_progress)

    console.print(f"[green][OK] Updated {result['changed']} files, "
                  f"{result['functions_updated']} functions[/green]")

    # Auto-compress if threshold reached
    if compressor.should_compress(project_path):
        with console.status("Compressing old sessions..."):
            compressor.compress_sessions(project_path)
        console.print("[dim]Session memory compressed.[/dim]")


# ── memory ask ───────────────────────────────────────────────────────────────

@app.command()
def ask(
    query: str = typer.Argument(..., help="Your question or coding task"),
    path: str = typer.Option(None, "--path", "-p", help="Project path"),
    max_tokens: int = typer.Option(3000, "--max-tokens", "-t", help="Max context tokens"),
    show_context: bool = typer.Option(True, "--context/--no-context", help="Show context package"),
    copy: bool = typer.Option(False, "--copy", "-c", help="Copy context to clipboard"),
):
    """Retrieve optimized AI context for a query. Shows token savings."""
    project_path = _get_project_path(path)

    memory_dir = Path(project_path) / ".memory"
    if not memory_dir.exists():
        console.print("[red]Not initialized. Run: memory init && memory index[/red]")
        raise typer.Exit(1)

    with console.status("[bold green]Retrieving memory..."):
        pkg = retriever.retrieve(project_path, query, max_tokens=max_tokens)

    report = context_builder.savings_report(pkg)

    # Show savings banner
    savings_color = "green" if report["savings_pct"] >= 80 else "yellow"
    console.print(Panel(
        f"Original context:  [dim]~{report['original']:,} tokens[/dim]\n"
        f"Optimized context: [bold {savings_color}]{report['optimized']:,} tokens[/bold {savings_color}]\n"
        f"Token savings:     [bold {savings_color}]{report['savings_pct']}%[/bold {savings_color}] [OK]",
        title=f"[bold]Query: {query[:60]}{'...' if len(query) > 60 else ''}[/bold]",
        border_style=savings_color,
    ))

    if show_context:
        context_md = context_builder.build_context_string(pkg)
        console.print(Markdown(context_md))

    if copy:
        try:
            import pyperclip
            pyperclip.copy(context_builder.build_system_prompt_prefix(pkg))
            console.print("[green][OK] Context copied to clipboard![/green]")
        except ImportError:
            console.print("[yellow]Install pyperclip to use --copy[/yellow]")

    # Log this as a session
    session_id = session_manager.start_session(project_path)
    session_manager.save_session(project_path, session_id, query)


# ── memory search ─────────────────────────────────────────────────────────────

@app.command()
def search(
    query: str = typer.Argument(..., help="Search term"),
    path: str = typer.Option(None, "--path", "-p"),
    limit: int = typer.Option(10, "--limit", "-n"),
):
    """Search memory — files and functions."""
    project_path = _get_project_path(path)

    files = db.search_files_fts(project_path, query, limit=limit)
    functions = db.search_functions_fts(project_path, query, limit=limit)

    if files:
        table = Table(title="Files", show_header=True, header_style="bold cyan")
        table.add_column("File", style="cyan")
        table.add_column("Purpose")
        table.add_column("Risk", width=8)
        for f in files:
            table.add_row(f["file_path"], f.get("purpose", "")[:80], f.get("risk_level", ""))
        console.print(table)

    if functions:
        table = Table(title="Functions", show_header=True, header_style="bold magenta")
        table.add_column("Function", style="magenta")
        table.add_column("File", style="dim")
        table.add_column("Summary")
        for fn in functions:
            summary = fn.get("summary") or fn.get("docstring", "")
            table.add_row(fn["name"], fn["file_path"], summary[:80])
        console.print(table)

    if not files and not functions:
        console.print(f"[yellow]No results for: {query}[/yellow]")


# ── memory stats ──────────────────────────────────────────────────────────────

@app.command()
def stats(
    path: str = typer.Argument(None, help="Project path"),
):
    """Show memory statistics and health."""
    project_path = _get_project_path(path)
    project_dna = db.get_project_dna(project_path)
    raw_stats = db.get_stats(project_path)

    name = project_dna["name"] if project_dna else Path(project_path).name

    table = Table(title=f"Memory Stats — {name}", show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Files indexed", str(raw_stats["file_memory"]))
    table.add_row("Functions stored", str(raw_stats["function_memory"]))
    table.add_row("Graph edges", str(raw_stats["knowledge_graph"]))
    table.add_row("Decisions recorded", str(raw_stats["decision_memory"]))
    table.add_row("Sessions tracked", str(raw_stats["session_memory"]))

    if project_dna:
        table.add_section()
        table.add_row("Language", project_dna.get("language", ""))
        table.add_row("Framework", project_dna.get("framework", ""))
        table.add_row("Architecture", project_dna.get("architecture", ""))

    console.print(table)


# ── memory compress ───────────────────────────────────────────────────────────

@app.command()
def compress(
    path: str = typer.Argument(None),
    force: bool = typer.Option(False, "--force", "-f", help="Force compress even if < threshold"),
):
    """Compress session memory into intelligence blocks."""
    project_path = _get_project_path(path)

    with console.status("Compressing sessions..."):
        result = compressor.compress_sessions(project_path, force=force)

    if result:
        console.print("[green][OK] Sessions compressed into intelligence block.[/green]")
        console.print(Markdown(result[:1000] + ("..." if len(result) > 1000 else "")))
    else:
        sessions = db.get_uncompressed_sessions(project_path)
        console.print(f"[yellow]Not enough sessions to compress "
                      f"({len(sessions)}/{compressor.COMPRESS_THRESHOLD}). "
                      f"Use --force to override.[/yellow]")


# ── memory graph ──────────────────────────────────────────────────────────────

@app.command()
def graph(
    path: str = typer.Argument(None),
    max_nodes: int = typer.Option(30, "--max"),
):
    """Visualize the dependency graph in terminal."""
    project_path = _get_project_path(path)
    output = graph_builder.visualize_ascii(project_path, max_nodes=max_nodes)
    console.print(Panel(output, title="Dependency Graph", border_style="blue"))


# ── memory export ─────────────────────────────────────────────────────────────

@app.command()
def export(
    output: str = typer.Argument("memory-export.zip", help="Output zip file"),
    path: str = typer.Option(None, "--path", "-p"),
):
    """Export .memory/ folder as a zip archive."""
    project_path = _get_project_path(path)
    memory_dir = Path(project_path) / ".memory"

    if not memory_dir.exists():
        console.print("[red].memory/ folder not found[/red]")
        raise typer.Exit(1)

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in memory_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(project_path))

    size_kb = Path(output).stat().st_size // 1024
    console.print(f"[green][OK] Exported to {output} ({size_kb} KB)[/green]")


# ── memory import ─────────────────────────────────────────────────────────────

@app.command(name="import")
def import_memory(
    archive: str = typer.Argument(..., help="Zip file to import"),
    path: str = typer.Option(None, "--path", "-p"),
):
    """Import .memory/ folder from a zip archive."""
    project_path = _get_project_path(path)

    with zipfile.ZipFile(archive, "r") as zf:
        zf.extractall(project_path)

    console.print(f"[green][OK] Memory imported from {archive}[/green]")


# ── memory decide ─────────────────────────────────────────────────────────────

@app.command()
def decide(
    title: str = typer.Argument(..., help="Decision title"),
    path: str = typer.Option(None, "--path", "-p"),
):
    """Record an architectural decision interactively."""
    from core import decision_manager

    project_path = _get_project_path(path)
    decision = typer.prompt("Decision")
    reason = typer.prompt("Reason (why)", default="")
    tags_str = typer.prompt("Tags (comma-separated)", default="")
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    decision_manager.add_decision(project_path, title, decision, reason, tags=tags)
    console.print(f"[green][OK] Decision recorded: {title}[/green]")


if __name__ == "__main__":
    app()
