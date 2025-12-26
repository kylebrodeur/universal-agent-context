"""CLI commands for context management and visualization."""

from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from uacs import UACS
from uacs.visualization import ContextVisualizer
from uacs.cli.utils import get_project_root

app = typer.Typer(help="Manage shared context and compression")
console = Console()


def get_uacs() -> UACS:
    """Get UACS instance for current project."""
    return UACS(get_project_root())


@app.command("stats")
def show_stats():
    """Show context and token usage statistics."""
    uacs = get_uacs()

    # Get stats from UACS
    stats = uacs.get_stats()
    token_stats = uacs.get_token_stats()
    context_stats = stats.get("context", {})

    # Render stats
    console.print("\n[bold cyan]📊 Context Statistics[/bold cyan]\n")

    console.print("[bold]Token Usage:[/bold]")
    console.print(f"  AGENTS.md:      {token_stats['agents_md_tokens']:>6,} tokens")
    console.print(f"  SKILLS.md:      {token_stats['skills_tokens']:>6,} tokens")
    console.print(
        f"  Shared Context: {token_stats['shared_context_tokens']:>6,} tokens"
    )
    console.print(
        f"  [dim]Total:          {token_stats['total_potential_tokens']:>6,} tokens[/dim]"
    )

    console.print("\n[bold]Compression:[/bold]")
    console.print(f"  Tokens Saved:   {token_stats['tokens_saved_by_compression']:>6,}")
    console.print(f"  Compression:    {context_stats['compression_ratio']:>6}")
    console.print(f"  Storage:        {context_stats['storage_size_mb']:>6.2f} MB")

    console.print("\n[bold]Entries:[/bold]")
    console.print(f"  Context Entries: {context_stats['entry_count']:>3}")
    console.print(f"  Summaries:       {context_stats['summary_count']:>3}")


@app.command("visualize")
def visualize_context(
    update_interval: float = typer.Option(
        2.0, "--interval", "-i", help="Update interval in seconds"
    ),
):
    """Launch live context visualization dashboard."""
    uacs = get_uacs()
    viz = ContextVisualizer(console)

    console.print("[cyan]Starting live dashboard...[/cyan]")
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")

    try:
        viz.live_dashboard(uacs.shared_context, update_interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard closed[/yellow]")


@app.command("graph")
def show_graph():
    """Show context relationship graph."""
    uacs = get_uacs()
    viz = ContextVisualizer(console)

    graph = uacs.shared_context.get_context_graph()
    console.print(viz.render_context_graph(graph))


@app.command("compress")
def compress_context(
    force: bool = typer.Option(
        False, "--force", help="Force compression even if not needed"
    ),
):
    """Manually trigger context compression."""
    uacs = get_uacs()

    before_stats = uacs.shared_context.get_stats()
    before_tokens = before_stats["total_tokens"]

    console.print("🗜️  Compressing context...")

    uacs.unified_context.optimize_context()

    after_stats = uacs.shared_context.get_stats()
    after_tokens = after_stats["total_tokens"]

    viz = ContextVisualizer(console)
    console.print(
        viz.render_compression_viz(before_tokens, after_tokens, "auto-summary")
    )

    console.print("\n[green]✓[/green] Compression complete")
    console.print(
        f"  Created {after_stats['summary_count'] - before_stats['summary_count']} new summaries"
    )


@app.command("report")
def compression_report():
    """Show detailed compression report."""
    uacs = get_uacs()
    report = uacs.unified_context.get_compression_report()

    md = Markdown(report)
    console.print(Panel(md, title="Compression Report", border_style="cyan"))


@app.command("export")
def export_config(
    output: Path = typer.Option(
        Path("unified-context.json"), "--output", "-o", help="Output file path"
    ),
):
    """Export unified context configuration."""
    uacs = get_uacs()

    uacs.unified_context.export_unified_config(output)

    console.print(f"[green]✓[/green] Exported configuration to {output}")

    # Show summary
    caps = uacs.unified_context.get_unified_capabilities()
    console.print(f"\n  Skills: {len(caps['available_skills'])}")
    console.print(f"  AGENTS.md: {'✓' if caps['agents_md_loaded'] else '✗'}")
    console.print(f"  Context entries: {caps['shared_context_stats']['entry_count']}")


@app.command("snapshot")
def create_snapshot(name: str = typer.Argument(..., help="Snapshot name")):
    """Create snapshot of current context state."""
    uacs = get_uacs()

    snapshot = uacs.unified_context.create_snapshot(name)

    console.print(f"[green]✓[/green] Created snapshot: [cyan]{name}[/cyan]")
    console.print(f"\n  Timestamp: {snapshot['timestamp']}")
    console.print(f"  Entries: {snapshot['context_entries']}")
    console.print(f"  Summaries: {snapshot['summaries']}")


@app.command("capabilities")
def show_capabilities():
    """Show all unified capabilities."""
    uacs = get_uacs()
    caps = uacs.get_capabilities()

    console.print("\n[bold cyan]🎯 Unified Capabilities[/bold cyan]\n")

    # AGENTS.md
    if caps["agents_md_loaded"]:
        console.print("[green]✓[/green] AGENTS.md loaded")
        project_caps = caps["project_context"]
        if project_caps.get("setup"):
            console.print(f"  Setup commands: {len(project_caps['setup'])}")
        if project_caps.get("code_style"):
            console.print(f"  Style rules: {len(project_caps['code_style'])}")
    else:
        console.print("[dim]○ AGENTS.md not found[/dim]")

    # SKILLS.md
    skills = caps["available_skills"]
    if skills:
        console.print(f"\n[green]✓[/green] SKILLS.md loaded ({len(skills)} skills)")
        for skill in skills[:5]:
            console.print(f"  - {skill}")
        if len(skills) > 5:
            console.print(f"  [dim]... and {len(skills) - 5} more[/dim]")
    else:
        console.print("\n[dim]○ No skills loaded[/dim]")

    # Shared Context
    console.print("\n[green]✓[/green] Shared Context active")
    context_stats = caps["shared_context_stats"]
    console.print(f"  Entries: {context_stats['entry_count']}")
    console.print(f"  Summaries: {context_stats['summary_count']}")
    console.print(f"  Compression: {context_stats['compression_ratio']}")


@app.command("clear")
def clear_context(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Clear all shared context (keeps SKILLS.md and AGENTS.md)."""
    if not confirm:
        response = typer.confirm("Clear all shared context? This cannot be undone.")
        if not response:
            console.print("[yellow]Cancelled[/yellow]")
            return

    uacs = get_uacs()

    # Clear context
    uacs.shared_context.entries.clear()
    uacs.shared_context.summaries.clear()
    uacs.shared_context.dedup_index.clear()

    # Clear storage
    for file in uacs.shared_context.storage_path.glob("*"):
        if file.is_file():
            file.unlink()

    console.print("[green]✓[/green] Cleared all shared context")


@app.command("validate")
def validate_project(
    fix: bool = typer.Option(False, "--fix", help="Show fix suggestions"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show all issues including suggestions"
    ),
):
    """Validate AGENTS.md and SKILLS.md configuration."""
    # Note: ProjectValidator is not part of UACS core, so this command may need updates
    # or be removed if the validator doesn't exist in UACS
    console.print("[yellow]⚠ This command requires ProjectValidator which may not be available in UACS[/yellow]")
    console.print("Use 'uacs skills validate' to validate individual SKILL.md files")


@app.command("build")
def build_focused_context(
    query: str = typer.Argument(..., help="Query or task for context building"),
    agent: str = typer.Option("claude", "--agent", "-a", help="Agent name"),
    topics: str | None = typer.Option(
        None, "--topics", "-t", help="Comma-separated topics to filter context"
    ),
    max_tokens: int = typer.Option(
        4000, "--max-tokens", "-m", help="Maximum tokens to return"
    ),
):
    """Build focused context filtered by topics."""
    uacs = get_uacs()

    # Parse topics if provided
    topic_list = [t.strip() for t in topics.split(",")] if topics else None

    console.print(f"\n[cyan]🔍 Building context for: {query}[/cyan]")
    if topic_list:
        console.print(f"[dim]Topics: {', '.join(topic_list)}[/dim]")
    console.print()

    # Build context
    context = uacs.build_context(
        query=query, agent=agent, max_tokens=max_tokens, topics=topic_list
    )

    # Display context
    console.print(Panel(context, title=f"Context for {agent}", border_style="cyan"))

    # Show token count
    token_count = uacs.shared_context.count_tokens(context)
    console.print(f"\n[dim]Token count: {token_count:,}[/dim]")


@app.command("add")
def add_context_entry(
    content: str = typer.Argument(..., help="Content to add to context"),
    agent: str = typer.Option("user", "--agent", "-a", help="Agent name"),
    topics: str | None = typer.Option(
        None, "--topics", "-t", help="Comma-separated topics for this entry"
    ),
):
    """Add an entry to shared context with optional topics."""
    uacs = get_uacs()

    # Parse topics if provided
    topic_list = [t.strip() for t in topics.split(",")] if topics else None

    entry_id = uacs.shared_context.add_entry(
        content=content, agent=agent, topics=topic_list
    )

    console.print(f"[green]✓[/green] Added context entry: [cyan]{entry_id}[/cyan]")
    if topic_list:
        console.print(f"[dim]Topics: {', '.join(topic_list)}[/dim]")


@app.command("init")
def init_agents_md():
    """Initialize AGENTS.md file with template."""
    target = get_project_root() / "AGENTS.md"

    if target.exists():
        console.print(f"[yellow]AGENTS.md already exists: {target}[/yellow]")
        return

    template = """# AGENTS.md

## Project Overview
Brief description of your project, its architecture, and key concepts.

## Setup Commands
- Install dependencies: `npm install` or `pip install -r requirements.txt`
- Start dev server: `npm run dev` or `python app.py`

## Dev Environment Tips
- Use environment variables from .env.example
- Database migrations: `npm run migrate`
- Check logs: `tail -f logs/app.log`

## Code Style
- TypeScript strict mode enabled
- Use single quotes for strings
- 2-space indentation
- No semicolons
- Prefer functional patterns

## Build Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`

## Testing Instructions
- Run unit tests: `npm test`
- Run integration tests: `npm run test:integration`
- Coverage report: `npm run test:coverage`
- All tests must pass before merging

## PR Instructions
- Title format: `[Component] Brief description`
- Link related issues
- Update tests for changed code
- Run `npm run lint` before committing
- Request review from @team
"""

    target.write_text(template)
    console.print(f"[green]✓[/green] Created AGENTS.md at {target}")
    console.print("\nEdit this file to customize for your project.")


if __name__ == "__main__":
    app()
