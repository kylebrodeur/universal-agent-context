"""CLI commands for memory management."""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from uacs.memory.simple_memory import SimpleMemoryStore
from uacs.cli.utils import get_project_root

app = typer.Typer(help="Manage memory storage and queries")
console = Console()


def _get_store(project_root: Path | None = None) -> SimpleMemoryStore:
    """Create a memory store for the current project."""
    root = project_root or get_project_root()
    global_override = os.environ.get("UACS_GLOBAL_MEMORY")
    global_path = Path(global_override) if global_override else None
    return SimpleMemoryStore(project_path=root, global_path=global_path)


def _validate_scope(scope: str) -> str:
    scope_normalized = scope.lower()
    if scope_normalized not in {"project", "global", "both"}:
        raise typer.BadParameter("Scope must be project, global, or both")
    return scope_normalized


@app.command("init")
def init_memory(
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Scope to initialize: project, global, or both",
    ),
):
    """Initialize simple JSON memory directories."""
    scope_normalized = _validate_scope(scope)
    store = _get_store()

    initialized_paths = []
    for current_scope in (
        ["project", "global"] if scope_normalized == "both" else [scope_normalized]
    ):
        path = store.init_storage(current_scope)
        initialized_paths.append(path)

    for path in initialized_paths:
        console.print(f"[green]✓[/green] Initialized memory at {path}")


@app.command("stats")
def memory_stats():
    """Show memory statistics for project and global scopes."""
    store = _get_store()
    stats = store.get_stats()

    table = Table(title="Memory Statistics")
    table.add_column("Scope", style="cyan")
    table.add_column("Entries", justify="right")
    table.add_column("Size (KB)", justify="right")
    table.add_column("Last Updated", justify="left")
    table.add_column("Path", justify="left")

    for scope in ("project", "global"):
        scope_stats = stats.get(scope, {})
        size_kb = scope_stats.get("size_bytes", 0) / 1024
        table.add_row(
            scope.capitalize(),
            str(scope_stats.get("entries", 0)),
            f"{size_kb:.1f}",
            scope_stats.get("last_updated") or "—",
            scope_stats.get("path", "—"),
        )

    console.print(table)


@app.command("search")
def search_memory(
    query: str = typer.Argument(..., help="Query to search in memory entries"),
    scope: str = typer.Option(
        "both",
        "--scope",
        "-s",
        help="Scope to search: project, global, or both",
    ),
):
    """Search memory entries by substring match."""
    scope_normalized = _validate_scope(scope)
    store = _get_store()
    results = store.search(query, scope=scope_normalized)

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    for idx, entry in enumerate(results, start=1):
        console.print(f"\n[bold]{idx}. {entry.key}[/bold] ({entry.scope})")
        console.print(f"[dim]Created:[/dim] {entry.created_at}")
        console.print(f"[dim]Updated:[/dim] {entry.updated_at}")
        console.print_json(data=entry.data)


@app.command("clean")
def clean_memory(
    scope: str = typer.Option(
        "project",
        "--scope",
        "-s",
        help="Scope to clean: project or global",
    ),
    older_than_days: int = typer.Option(
        30,
        "--older-than",
        "-o",
        help="Delete entries older than the given number of days",
    ),
):
    """Delete old memory entries for the given scope."""
    scope_normalized = _validate_scope(scope)
    if scope_normalized == "both":
        raise typer.BadParameter("Clean supports project or global scope only")

    store = _get_store()
    deleted = store.clean(older_than_days=older_than_days, scope=scope_normalized)

    console.print(
        f"[green]✓[/green] Deleted {deleted} entr{'y' if deleted == 1 else 'ies'} "
        f"from {scope_normalized} memory older than {older_than_days} days"
    )


__all__ = ["app"]


if __name__ == "__main__":
    app()
