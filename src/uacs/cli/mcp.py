"""CLI commands for MCP server management."""

import json

import typer
from rich.console import Console
from rich.table import Table

from uacs.protocols.mcp.manager import McpManager

app = typer.Typer(help="Manage MCP servers")
console = Console()


@app.command("list")
def list_servers():
    """List all MCP servers in use in this project, regardless of installation source."""
    manager = McpManager()
    servers = manager.list_servers()

    if not servers:
        console.print("[yellow]No MCP servers configured.[/yellow]")
        console.print("\nConfigure MCP servers in: ~/.uacs/mcp-config.json")
        return

    table = Table(title="MCP Servers in Use")
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Command", style="green", width=40)
    table.add_column("Args", style="white", width=30)
    table.add_column("Status", style="magenta", width=10)

    # Add configured servers
    for server in servers:
        status = "Enabled" if server.enabled else "Disabled"
        args_str = " ".join(server.args[:2])
        if len(server.args) > 2:
            args_str += "..."

        table.add_row(server.name, server.command, args_str, status)

    console.print(table)
    console.print(f"\n[dim]Total: {len(servers)} MCP server(s) configured[/dim]")


@app.command("add")
def add_server(
    name: str = typer.Argument(..., help="Name of the MCP server"),
    command: str = typer.Argument(..., help="Executable command"),
    args: list[str] = typer.Argument(None, help="Arguments for the command"),
    env: str = typer.Option(None, help="Environment variables as JSON string"),
):
    """Add a new MCP server."""
    manager = McpManager()

    env_dict = {}
    if env:
        try:
            env_dict = json.loads(env)
        except json.JSONDecodeError:
            console.print("[red]Error: Invalid JSON for environment variables[/red]")
            raise typer.Exit(1)

    manager.add_server(name, command, args or [], env_dict)
    console.print(f"[green]Added MCP server: {name}[/green]")


@app.command("remove")
def remove_server(name: str = typer.Argument(..., help="Name of the MCP server")):
    """Remove an MCP server."""
    manager = McpManager()
    if manager.get_server(name):
        manager.remove_server(name)
        console.print(f"[green]Removed MCP server: {name}[/green]")
    else:
        console.print(f"[red]Server {name} not found[/red]")


@app.command("install-filesystem")
def install_filesystem(
    path: str = typer.Argument(..., help="Root path for filesystem access"),
):
    """Helper to add the standard filesystem MCP server."""
    manager = McpManager()
    import shutil

    # Detect available runner
    command = None
    args = []

    if shutil.which("pnpm"):
        command = "pnpm"
        args = ["dlx", "@modelcontextprotocol/server-filesystem", path]
    elif shutil.which("bun"):
        command = "bun"
        args = ["x", "@modelcontextprotocol/server-filesystem", path]
    elif shutil.which("npx"):
        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-filesystem", path]
    else:
        console.print(
            "[red]Error: No suitable runner found (pnpm, bun, or npx required).[/red]"
        )
        raise typer.Exit(1)

    manager.add_server(name="filesystem", command=command, args=args)
    console.print(
        f"[green]Added filesystem MCP server using {command} for path: {path}[/green]"
    )


__all__ = ["app"]


if __name__ == "__main__":
    app()
