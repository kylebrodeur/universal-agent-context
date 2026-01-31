"""CLI commands for minimal package management.

Inspired by GitHub CLI extensions pattern - simple, focused commands
for installing packages from GitHub, Git URLs, or local paths.
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from uacs.packages import PackageManager
from uacs.cli.utils import get_project_root

app = typer.Typer(help="Package management (GitHub CLI-style)")
console = Console()


def get_package_manager() -> PackageManager:
    """Get PackageManager instance for current project."""
    return PackageManager(get_project_root())


@app.command("install")
def install(
    source: str = typer.Argument(
        ...,
        help="Package source: owner/repo, https://github.com/...git, or ./local/path",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite if already installed"
    ),
    no_validate: bool = typer.Option(
        False, "--no-validate", help="Skip validation after install"
    ),
):
    """Install a package from GitHub, Git URL, or local path.

    Examples:
        uacs install owner/repo                     # GitHub repository
        uacs install https://github.com/owner/repo.git  # Git URL
        uacs install ./local/path                   # Local directory
        uacs install owner/repo --force             # Overwrite existing
        uacs install owner/repo --no-validate       # Skip validation
    """
    pm = get_package_manager()

    try:
        # Determine source type and display info
        if source.startswith(("http://", "https://", "git@")):
            console.print(f"[cyan]Installing from Git URL...[/cyan]")
        elif source.startswith(("./", "../", "/")):
            console.print(f"[cyan]Installing from local path...[/cyan]")
        elif "/" in source:
            console.print(f"[cyan]Installing {source} from GitHub...[/cyan]")
        else:
            console.print(
                "[red]✗[/red] Invalid source format. Use: owner/repo, git URL, or ./path"
            )
            return

        # Install with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Installing...", total=None)
            package = pm.install(source, force=force, validate=not no_validate)

        # Show success
        console.print(f"[green]✓[/green] Successfully installed: [bold]{package.name}[/bold]")

        # Display package info
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="dim")
        table.add_column("Value")

        table.add_row("Name", package.name)
        table.add_row("Source", package.source)
        table.add_row("Type", package.source_type.value)
        if package.version:
            table.add_row("Version", package.version)
        if package.location:
            table.add_row("Location", str(package.location))

        console.print(table)

        # Show validation warnings
        if not package.is_valid:
            console.print("\n[yellow]⚠[/yellow] Validation warnings:")
            for error in package.validation_errors:
                console.print(f"  • {error}")

        console.print("\n[dim]List packages with: uacs list[/dim]")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error installing package: {e}")


@app.command("list")
def list_packages(
    show_invalid: bool = typer.Option(
        False, "--show-invalid", help="Include invalid packages"
    ),
):
    """List installed packages.

    Examples:
        uacs list                    # List all valid packages
        uacs list --show-invalid     # Include invalid packages
    """
    pm = get_package_manager()

    try:
        packages = pm.list_installed()

        if not packages:
            console.print("[yellow]No packages installed[/yellow]")
            console.print("\n[dim]Install with: uacs install owner/repo[/dim]")
            return

        # Create table
        table = Table(
            title="Installed Packages",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Name", style="cyan", width=25)
        table.add_column("Source", style="green", width=35)
        table.add_column("Type", style="magenta", width=10)
        table.add_column("Version", style="blue", width=12)
        table.add_column("Status", style="white", width=10)

        for pkg in packages:
            status = "[green]✓[/green]" if pkg.is_valid else "[red]✗[/red]"
            version = pkg.version or "-"

            table.add_row(
                pkg.name,
                pkg.source,
                pkg.source_type.value,
                version,
                status,
            )

        console.print(table)
        console.print(f"\n[dim]Total installed: {len(packages)}[/dim]")

        # Show validation summary
        invalid_count = sum(1 for p in packages if not p.is_valid)
        if invalid_count > 0:
            console.print(
                f"[yellow]{invalid_count} package(s) have validation errors[/yellow]"
            )
            console.print("[dim]Use 'uacs validate <name>' for details[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Error listing packages: {e}")


@app.command("validate")
def validate_package(
    package_name: str = typer.Argument(..., help="Package name to validate"),
):
    """Validate an installed package.

    Examples:
        uacs validate my-package     # Validate specific package
    """
    pm = get_package_manager()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Validating...", total=None)
            is_valid, errors = pm.validate(package_name)

        if is_valid:
            console.print(
                f"[green]✓[/green] Package '[bold]{package_name}[/bold]' is valid"
            )
        else:
            console.print(
                f"[red]✗[/red] Package '[bold]{package_name}[/bold]' has validation errors:"
            )
            for error in errors:
                console.print(f"  • {error}")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error validating package: {e}")


@app.command("remove")
def remove_package(
    package_name: str = typer.Argument(..., help="Package name to remove"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Remove an installed package.

    Examples:
        uacs remove my-package       # Remove with confirmation
        uacs remove my-package -y    # Remove without confirmation
    """
    pm = get_package_manager()

    try:
        # Get package info for confirmation
        packages = pm.list_installed()
        package = next((p for p in packages if p.name == package_name), None)

        if not package:
            console.print(f"[red]✗[/red] Package '{package_name}' not found")
            console.print("\n[dim]List packages with: uacs list[/dim]")
            return

        # Show package info
        console.print(f"\n[bold]Package: {package.name}[/bold]")
        console.print(f"  Source: {package.source}")
        console.print(f"  Type: {package.source_type.value}")
        if package.location:
            console.print(f"  Location: {package.location}")

        # Confirm removal
        if not yes:
            confirm = typer.confirm(f"\nRemove '{package_name}'?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Remove package
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Removing...", total=None)
            pm.remove(package_name)

        console.print(f"[green]✓[/green] Removed '{package_name}'")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error removing package: {e}")


@app.command("update")
def update_package(
    package_name: str = typer.Argument(..., help="Package name to update"),
):
    """Update a package to the latest version.

    Examples:
        uacs update my-package       # Update to latest version
    """
    pm = get_package_manager()

    try:
        # Get current package info
        packages = pm.list_installed()
        package = next((p for p in packages if p.name == package_name), None)

        if not package:
            console.print(f"[red]✗[/red] Package '{package_name}' not found")
            console.print("\n[dim]List packages with: uacs list[/dim]")
            return

        console.print(f"[cyan]Updating {package_name}...[/cyan]")
        console.print(f"  Current source: {package.source}")

        # Update with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Updating...", total=None)
            updated_package = pm.update(package_name)

        # Show success
        console.print(
            f"[green]✓[/green] Successfully updated: [bold]{updated_package.name}[/bold]"
        )

        # Display version info if available
        if updated_package.version:
            console.print(f"  Version: {updated_package.version}")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error updating package: {e}")


__all__ = ["app"]


if __name__ == "__main__":
    app()
