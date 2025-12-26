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

    # Get marketplace-installed MCP servers
    from uacs.marketplace.marketplace import MarketplaceAdapter

    marketplace = MarketplaceAdapter()
    marketplace_mcps = {
        asset.name: asset
        for asset in marketplace.list_installed()
        if asset.asset_type == "mcp_server"
    }

    if not servers and not marketplace_mcps:
        console.print("[yellow]No MCP servers configured.[/yellow]")
        console.print("\nSearched locations:")
        console.print("  - Manual configuration (~/.uacs/mcp-config.json)")
        console.print("  - Marketplace installations")
        return

    table = Table(title="MCP Servers in Use")
    table.add_column("Name", style="cyan", width=20)
    table.add_column("Source", style="yellow", width=30)
    table.add_column("Command", style="green", width=25)
    table.add_column("Args", style="white", width=30)
    table.add_column("Status", style="magenta", width=10)

    # Track which marketplace servers we've seen
    seen_marketplace = set()

    # Add configured servers
    for server in servers:
        source = "Manual Config"
        if server.name in marketplace_mcps:
            asset = marketplace_mcps[server.name]
            source = f"Marketplace ({asset.marketplace})"
            seen_marketplace.add(server.name)

        status = "Enabled" if server.enabled else "Disabled"
        args_str = " ".join(server.args[:2])
        if len(server.args) > 2:
            args_str += "..."

        table.add_row(server.name, source, server.command, args_str, status)

    # Add marketplace-only servers (not in config)
    for mcp_name, asset in marketplace_mcps.items():
        if mcp_name not in seen_marketplace:
            source = f"Marketplace ({asset.marketplace})"
            command = asset.config.get("command", "N/A") if asset.config else "N/A"
            args_str = ""
            if asset.config and "args" in asset.config:
                args = asset.config["args"]
                if isinstance(args, list):
                    args_str = " ".join(args[:2])
                    if len(args) > 2:
                        args_str += "..."
            table.add_row(mcp_name, source, command, args_str, "N/A")

    console.print(table)
    console.print(f"\n[dim]Total: {len(table.rows)} MCP server(s) in use[/dim]")


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
