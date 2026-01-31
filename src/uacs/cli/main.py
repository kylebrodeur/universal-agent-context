"""UACS CLI - Universal Agent Context System command-line interface."""

import asyncio
from pathlib import Path

import typer

from uacs.cli import context, memory, mcp, packages, skills

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
    typer.echo("Exposing skills, context, and package management tools")
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
