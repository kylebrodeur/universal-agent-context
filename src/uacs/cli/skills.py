"""CLI commands for managing agent skills."""

import json
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from uacs import UACS
from uacs.adapters import FormatAdapterRegistry
from uacs.adapters.agent_skill_adapter import AgentSkillAdapter
from uacs.skills_validator import SkillValidator
from uacs.cli.utils import get_project_root

app = typer.Typer(help="Manage agent skills")
console = Console()


def get_uacs() -> UACS:
    """Get UACS instance for current project."""
    return UACS(get_project_root())


@app.command()
def validate(
    skill_path: Path = typer.Argument(..., help="Path to skill directory"),
    strict: bool = typer.Option(False, "--strict", help="Fail on warnings"),
):
    """Validate a skill against the Agent Skills specification."""
    result = SkillValidator.validate_file(skill_path)

    if result.valid:
        if strict and result.warnings:
            console.print(f"[red]✗[/red] Skill at {skill_path} has warnings (strict mode)")
            for warning in result.warnings:
                console.print(f"  - {warning.field}: {warning.message}")
            raise typer.Exit(code=1)

        console.print(f"[green]✓[/green] Skill at {skill_path} is valid")
        for warning in result.warnings:
            console.print(f"  [yellow]![/yellow] {warning.field}: {warning.message}")
    else:
        console.print(f"[red]✗[/red] Skill at {skill_path} is invalid")
        for error in result.errors:
            console.print(f"  - {error.field}: {error.message}")
        raise typer.Exit(code=1)


@app.command("read-properties")
def read_properties(
    skill_path: Path = typer.Argument(..., help="Path to skill directory"),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format (json/yaml)"),
):
    """Read skill properties (frontmatter)."""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        console.print(f"[red]✗[/red] SKILL.md not found in {skill_path}")
        raise typer.Exit(code=1)

    content = skill_file.read_text()
    frontmatter, _, errors = SkillValidator.extract_frontmatter(content)

    if errors:
        console.print(f"[red]✗[/red] Failed to parse frontmatter")
        for error in errors:
            console.print(f"  - {error.message}")
        raise typer.Exit(code=1)

    if output_format == "json":
        print(json.dumps(frontmatter, indent=2))
    elif output_format == "yaml":
        print(yaml.dump(frontmatter))
    else:
        console.print(f"[red]✗[/red] Unknown format: {output_format}")
        raise typer.Exit(code=1)


@app.command("to-prompt")
def to_prompt(
    skill_paths: list[Path] = typer.Argument(..., help="Paths to skill directories"),
):
    """Convert skills to prompt format."""
    adapter = AgentSkillAdapter()
    prompts = []

    for path in skill_paths:
        skill_file = path / "SKILL.md"
        if not skill_file.exists():
            console.print(f"[red]✗[/red] SKILL.md not found in {path}")
            raise typer.Exit(code=1)
        
        content = skill_file.read_text()
        adapter.parsed = adapter.parse(content)
        prompts.append(adapter.to_system_prompt())

    print("\n\n".join(prompts))


@app.command()
def list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all available skills in the project."""
    uacs = get_uacs()
    skills = uacs.get_capabilities()
    
    if json_output:
        print(json.dumps(skills, indent=2))
        return

    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Source", style="green")
    table.add_column("Description")

    for skill in skills.get("agent_skills", []):
        table.add_row(
            skill.get("name", "unknown"),
            skill.get("source", "unknown"),
            skill.get("description", "")[:100]
        )
    
    console.print(table)

