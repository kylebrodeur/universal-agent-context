"""UACS CLI - Universal Agent Context System command-line interface."""

import asyncio
from pathlib import Path

import typer

from uacs.cli import context, memory, mcp, packages, plugin, skills

app = typer.Typer(
    name="uacs",
    help="Universal Agent Context System - unified context for AI agents",
    no_args_is_help=True,
)

# Register sub-apps
app.add_typer(skills.app, name="skills")
app.add_typer(context.app, name="context")
app.add_typer(packages.app, name="packages")
app.add_typer(memory.app, name="memory")
app.add_typer(mcp.app, name="mcp")
app.add_typer(plugin.app, name="plugin")


@app.command()
def serve(
    host: str = typer.Option("localhost", "--host", "-h", help="Server host"),
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
    with_ui: bool = typer.Option(False, "--with-ui", help="Start web UI visualization server"),
    ui_port: int = typer.Option(8081, "--ui-port", help="Web UI port"),
):
    """Start UACS MCP server for tool integration.

    The MCP server exposes all UACS capabilities as tools that can be
    consumed by AI agents via the Model Context Protocol.

    Use --with-ui to also start the web-based context visualization UI.

    Examples:
        uacs serve --host 0.0.0.0 --port 8080
        uacs serve --with-ui --ui-port 8081
    """
    from uacs.protocols.mcp.skills_server import main as mcp_main

    console = typer.get_text_stream("stdout")
    typer.echo(f"Starting UACS MCP server on {host}:{port}...")
    typer.echo("Exposing skills, context, and package management tools")

    if with_ui:
        typer.echo(f"Web UI will be available at http://{host}:{ui_port}")
        typer.echo("Starting visualization server...")
        _run_with_ui(host, port, ui_port)
    else:
        typer.echo("Press Ctrl+C to stop\n")
        try:
            asyncio.run(mcp_main())
        except KeyboardInterrupt:
            typer.echo("\n\nServer stopped")


@app.command()
def stats(
    project_path: Path = typer.Option(Path("."), "--project", "-p", help="Project path")
):
    """Show comprehensive UACS statistics.

    Displays counts for conversations, knowledge, and embeddings.

    Example:
        uacs stats
        uacs stats --project /path/to/project
    """
    from rich.console import Console
    from rich.table import Table
    from uacs import UACS
    from uacs import __version__

    console = Console()

    try:
        uacs = UACS(project_path=project_path)
        stats_data = uacs.get_stats()

        console.print(f"\n[bold]UACS Statistics[/bold] (v{__version__})\n")
        console.print(f"Project: {project_path.absolute()}\n")

        # Semantic context stats
        semantic = stats_data.get("semantic", {})
        if semantic:
            # Conversations table
            conv_stats = semantic.get("conversations", {})
            if conv_stats:
                console.print("[bold cyan]Conversations:[/bold cyan]")
                table = Table(show_header=False, box=None, padding=(0, 2))
                table.add_row("User Messages:", str(conv_stats.get("total_user_messages", 0)))
                table.add_row("Assistant Messages:", str(conv_stats.get("total_assistant_messages", 0)))
                table.add_row("Tool Uses:", str(conv_stats.get("total_tool_uses", 0)))
                table.add_row("Sessions:", str(conv_stats.get("total_sessions", 0)))
                console.print(table)
                console.print()

            # Knowledge table
            knowledge = semantic.get("knowledge", {})
            if knowledge:
                console.print("[bold green]Knowledge:[/bold green]")
                table = Table(show_header=False, box=None, padding=(0, 2))
                table.add_row("Conventions:", str(knowledge.get("conventions", 0)))
                table.add_row("Decisions:", str(knowledge.get("decisions", 0)))
                table.add_row("Learnings:", str(knowledge.get("learnings", 0)))
                table.add_row("Artifacts:", str(knowledge.get("artifacts", 0)))
                console.print(table)
                console.print()

            # Embeddings table
            embeddings = semantic.get("embeddings", {})
            if embeddings:
                console.print("[bold magenta]Embeddings:[/bold magenta]")
                table = Table(show_header=False, box=None, padding=(0, 2))
                table.add_row("Total Vectors:", str(embeddings.get("total_vectors", 0)))
                table.add_row("Model:", embeddings.get("model_name", "N/A"))
                table.add_row("Dimension:", str(embeddings.get("dimension", "N/A")))
                console.print(table)
        else:
            console.print("[yellow]No semantic context data found.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results to return"),
    types: str = typer.Option(None, "--types", "-t", help="Comma-separated types to search (e.g., 'decision,convention')"),
    project_path: Path = typer.Option(Path("."), "--project", "-p", help="Project path"),
):
    """Search context with natural language.

    Search across conversations and knowledge using semantic similarity.

    Examples:
        uacs search "how did we implement authentication?"
        uacs search "security decisions" --types decision,convention --limit 5
        uacs search "JWT" --types learning,artifact
    """
    from rich.console import Console
    from rich.panel import Panel
    from uacs import UACS

    console = Console()

    try:
        uacs = UACS(project_path=project_path)

        # Parse types
        type_list = types.split(",") if types else None

        # Perform search
        results = uacs.search(query=query, types=type_list, limit=limit)

        console.print(f"\n[bold]Search Results[/bold] ({len(results)} found)\n")

        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return

        for i, result in enumerate(results, 1):
            # Extract result data (handle both SearchResult types)
            result_type = result.metadata.get("type", "unknown")
            score = getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)
            text = getattr(result, 'text', None) or getattr(result, 'content', '')

            # Truncate text for display
            display_text = text[:200] + "..." if len(text) > 200 else text

            # Format type with color
            type_colors = {
                "user_message": "cyan",
                "assistant_message": "green",
                "tool_use": "blue",
                "convention": "yellow",
                "decision": "magenta",
                "learning": "red",
                "artifact": "white",
            }
            type_color = type_colors.get(result_type, "white")

            # Create panel
            title = f"[{type_color}]{result_type}[/{type_color}] ({score:.1%})"
            console.print(Panel(display_text, title=title, border_style=type_color))

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(1)


def _run_with_ui(host: str, port: int, ui_port: int):
    """Run MCP server with web UI visualization.

    Args:
        host: Server host
        port: MCP server port
        ui_port: Web UI port
    """
    import uvicorn
    from pathlib import Path
    from uacs.context.shared_context import SharedContextManager
    from uacs.visualization.web_server import VisualizationServer

    # Initialize shared context manager
    storage_path = Path.cwd() / ".state" / "context"
    context_manager = SharedContextManager(storage_path=storage_path)

    # Create visualization server
    viz_server = VisualizationServer(context_manager, host, ui_port)

    # Print startup message
    typer.echo(f"\n✓ Web UI available at http://{host}:{ui_port}")
    typer.echo("✓ MCP server running (stdio mode)")
    typer.echo("Press Ctrl+C to stop\n")

    # Run visualization server (MCP server runs in stdio mode alongside)
    config = uvicorn.Config(
        viz_server.app,
        host=host,
        port=ui_port,
        log_level="info",
    )
    server = uvicorn.Server(config)

    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        typer.echo("\n\nServers stopped")


@app.command()
def version():
    """Show UACS version information."""
    try:
        from importlib.metadata import version as get_version

        uacs_version = get_version("universal-agent-context")
        typer.echo(f"UACS version: {uacs_version}")
    except Exception:
        typer.echo("UACS version: development")


@app.command()
def web(
    host: str = typer.Option("localhost", "--host", "-h", help="Server host"),
    port: int = typer.Option(8081, "--port", "-p", help="Server port"),
    project_path: Path = typer.Option(
        Path.cwd(), "--project", help="Project path (default: current directory)"
    ),
):
    """Start UACS Web UI visualization server.

    Serves the bundled Next.js UI for browsing conversations, knowledge,
    and semantic search. All in one command - no separate frontend server needed!

    Examples:
        uacs web                         # Start on http://localhost:8081
        uacs web --port 3000             # Custom port
        uacs web --host 0.0.0.0          # Listen on all interfaces
    """
    try:
        import uvicorn
        from uacs.api import UACS
        from uacs.visualization.web_server import VisualizationServer

        typer.echo(f"\n🚀 Starting UACS Web UI...")
        typer.echo(f"📁 Project: {project_path}")
        typer.echo(f"🌐 URL: http://{host}:{port}\n")

        # Initialize UACS and server
        uacs = UACS(project_path=project_path)
        server = VisualizationServer(uacs=uacs, host=host, port=port)

        # Check if Next.js build exists (packaged or development)
        packaged_ui = Path(__file__).parent.parent / "visualization" / "static_ui"
        dev_ui = Path(__file__).parent.parent.parent.parent / "uacs-web-ui" / "out"

        if not packaged_ui.exists() and not dev_ui.exists():
            typer.echo("⚠️  Warning: Next.js build not found!")
            typer.echo(f"   Expected at: {packaged_ui} (packaged) or {dev_ui} (dev)")
            typer.echo("   Run: cd uacs-web-ui && pnpm build\n")

        typer.echo("✨ Web UI is ready! Press Ctrl+C to stop\n")

        # Start server
        uvicorn.run(server.app, host=host, port=port, log_level="info")

    except KeyboardInterrupt:
        typer.echo("\n\n👋 Web UI stopped")
    except Exception as e:
        typer.echo(f"\n❌ Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def init(
    project_root: Path = typer.Argument(
        Path.cwd(), help="Project root directory (default: current directory)"
    ),
):
    """Initialize UACS for a project.

    Creates necessary directories and example configuration files.
    """
    from rich.console import Console

    console = Console()

    # Create .agent directory structure
    agent_dir = project_root / ".agent"
    skills_dir = agent_dir / "skills"
    state_dir = project_root / ".state"
    context_dir = state_dir / "context"

    dirs_to_create = [agent_dir, skills_dir, state_dir, context_dir]

    for directory in dirs_to_create:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]✓[/green] Created {directory}")
        else:
            console.print(f"[dim]○[/dim] Already exists: {directory}")

    # Create example Agent Skill if .agent/skills/ is empty
    skills_dir = project_root / ".agent" / "skills"
    example_skill_dir = skills_dir / "example-skill"
    if skills_dir.exists() and not any(skills_dir.iterdir()):
        # Directory exists but is empty - create example
        example_skill_dir.mkdir(parents=True, exist_ok=True)
        example_skill = """---
name: example-skill
description: Example skill demonstrating the Agent Skills format
---

# Example Skill

This is an example skill showing the Agent Skills format structure.

## When to Use

Use this skill when you need to demonstrate:
- How to structure a skill with YAML frontmatter
- How to organize instructions
- How to trigger skill usage

## Instructions

1. **Understand the format**: Skills use YAML frontmatter + Markdown body
2. **Define clear triggers**: Describe when this skill should be used
3. **Provide actionable steps**: Break down the skill into clear instructions
4. **Include examples**: Show concrete usage examples when relevant

## Examples

When a user asks "Show me how skills work", you can:
1. Reference this example skill
2. Explain the YAML frontmatter structure
3. Show the markdown instruction format
"""
        skill_file = example_skill_dir / "SKILL.md"
        skill_file.write_text(example_skill)
        console.print(
            f"[green]✓[/green] Created example skill {example_skill_dir.name}"
        )

    console.print("\n[bold cyan]UACS initialized successfully![/bold cyan]")
    console.print("\nNext steps:")
    console.print("  1. Run 'uacs skills list' to see available skills")
    console.print("  2. Run 'uacs install owner/repo' to install packages from GitHub")
    console.print("  3. Run 'uacs list' to see installed packages")
    console.print("  4. Run 'uacs serve' to start the MCP server")


__all__ = ["app"]


if __name__ == "__main__":
    app()
