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
from uacs.skills_validator import SkillValidator
from uacs.cli.utils import get_project_root

app = typer.Typer(help="Manage agent skills")
console = Console()


def get_uacs() -> UACS:
    """Get UACS instance for current project."""
    return UACS(get_project_root())
