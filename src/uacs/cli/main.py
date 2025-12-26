"""UACS CLI - Universal Agent Context System command-line interface."""

import asyncio
from pathlib import Path

import typer

from uacs.cli import context, marketplace, memory, mcp, skills

app = typer.Typer(
    name="uacs",
    help="Universal Agent Context System - unified context for AI agents",
    no_args_is_help=True,
)

# Register sub-apps
app.add_typer(skills.app, name="skills")
app.add_typer(context.app, name="context")
app.add_typer(marketplace.app, name="marketplace")
app.add_typer(memory.app, name="memory")
app.add_typer(mcp.app, name="mcp")


@app.command()
def serve(
    host: str = typer.Option("localhost", "--host", "-h", help="Server host"),
    port: int = typer.Option(8080, "--port", "-p", help="Server port"),
):
    """Start UACS MCP server for tool integration.

    The MCP server exposes all UACS capabilities as tools that can be
    consumed by AI agents via the Model Context Protocol.

    Example:
        uacs serve --host 0.0.0.0 --port 8080
    """
    from uacs.protocols.mcp.skills_server import main as mcp_main

    console = typer.get_text_stream("stdout")
    typer.echo(f"Starting UACS MCP server on {host}:{port}...")
    typer.echo("Exposing skills, context, and marketplace tools")
    typer.echo("Press Ctrl+C to stop\n")

    try:
        asyncio.run(mcp_main())
    except KeyboardInterrupt:
        typer.echo("\n\nServer stopped")


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

    # Create example SKILLS.md if it doesn't exist
    skills_file = project_root / "SKILLS.md"
    if not skills_file.exists():
        example_skills = """# Agent Skills

This file defines available skills for AI agents using the Agent Skills format.

## Code Review

**Triggers:** code review, review code, check code

Perform comprehensive code review with focus on:
- Code quality and maintainability
- Security vulnerabilities
- Performance issues
- Best practices adherence

## Test Generation

**Triggers:** generate tests, create tests, test coverage

Generate unit and integration tests for code:
- Identify untested code paths
- Create test cases with good coverage
- Follow testing best practices
"""
        skills_file.write_text(example_skills)
        console.print(f"[green]✓[/green] Created example {skills_file}")
    else:
        console.print(f"[dim]○[/dim] Already exists: {skills_file}")

    console.print("\n[bold cyan]UACS initialized successfully![/bold cyan]")
    console.print("\nNext steps:")
    console.print("  1. Edit SKILLS.md to define your agent skills")
    console.print("  2. Run 'uacs skills list' to see available skills")
    console.print("  3. Run 'uacs marketplace search QUERY' to find more skills")
    console.print("  4. Run 'uacs serve' to start the MCP server")


__all__ = ["app"]


if __name__ == "__main__":
    app()
