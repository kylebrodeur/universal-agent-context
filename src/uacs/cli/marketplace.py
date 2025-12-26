"""CLI commands for skills marketplace."""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from uacs import UACS
from uacs.cli.utils import get_project_root

app = typer.Typer(help="Skills marketplace integration")
console = Console()


def _parse_query_type(query: str) -> tuple[str, str | None]:
    """Parse query for type hints like 'term skill' or 'term mcp'.

    Args:
        query: Search query string

    Returns:
        Tuple of (cleaned_query, detected_type)

    Examples:
        >>> _parse_query_type("git skill")
        ("git", "skill")
        >>> _parse_query_type("database mcp")
        ("database", "mcp")
        >>> _parse_query_type("filesystem")
        ("filesystem", None)
    """
    query_lower = query.lower().strip()

    # Check for "skill" suffix
    if query_lower.endswith(" skill"):
        return query[:-6].strip(), "skill"

    # Check for "mcp" suffix
    if query_lower.endswith(" mcp"):
        return query[:-4].strip(), "mcp"

    # Check for "mcp server" suffix
    if query_lower.endswith(" mcp server"):
        return query[:-11].strip(), "mcp"

    return query, None


def get_uacs() -> UACS:
    """Get UACS instance for current project."""
    return UACS(get_project_root())


@app.command("search")
def search_marketplace(
    query: str = typer.Argument(..., help="Search query"),
    marketplace: str | None = typer.Option(
        None,
        "--marketplace",
        "-m",
        help="Specific marketplace (skillsmp, skills4agents, agentshare, glama)",
    ),
    category: str | None = typer.Option(
        None, "--category", "-c", help="Filter by category"
    ),
    asset_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by type: 'skill' or 'mcp'",
    ),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum results"),
):
    """Search assets across marketplaces.

    Examples:
        uacs marketplace search "filesystem"
        uacs marketplace search "code review" --type skill
        uacs marketplace search "database" --type mcp
        uacs marketplace search "git skill"  # Auto-detects type
    """
    uacs = get_uacs()

    # Parse query for type hints ("term skill" or "term mcp")
    parsed_query, detected_type = _parse_query_type(query)

    # Use detected type if not explicitly provided
    if asset_type is None and detected_type:
        asset_type = detected_type
        query = parsed_query  # Use cleaned query
        console.print(f"[dim]Auto-detected type: {asset_type}[/dim]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Searching marketplaces...", total=None)
        results = uacs.search_marketplace(
            query, category, asset_type=asset_type, limit=limit
        )

    if not results:
        console.print("[yellow]No assets found matching your query[/yellow]")
        return

    # Display results in table
    table = Table(
        title=f"Search Results: '{query}'",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Name", style="cyan", width=25)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Author", style="green", width=15)
    table.add_column("Source", style="blue", width=12)
    table.add_column("Downloads", justify="right", style="yellow", width=10)
    table.add_column("Rating", justify="right", style="yellow", width=8)
    table.add_column("Description", width=40)

    for asset in results:
        table.add_row(
            asset.name,
            asset.asset_type,
            asset.author,
            asset.marketplace,
            f"{asset.downloads:,}",
            f"{asset.rating:.1f}⭐",
            asset.description[:80] + "..."
            if len(asset.description) > 80
            else asset.description,
        )

    console.print(table)
    console.print(f"\n[dim]Showing {len(results)} results[/dim]")
    console.print("[dim]Install with: uacs marketplace install ASSET_ID [SOURCE][/dim]")


@app.command("install")
def install_asset(
    asset_id: str = typer.Argument(..., help="Asset ID to install"),
    source: str | None = typer.Argument(
        None, help="Marketplace source (optional if unique)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite if already installed"
    ),
):
    """Install an asset from marketplace."""
    uacs = get_uacs()

    if source:
        console.print(f"[cyan]Installing {asset_id} from {source}...[/cyan]")
    else:
        console.print(f"[cyan]Searching for {asset_id}...[/cyan]")

    try:
        # Search for the asset
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Searching...", total=None)
            # If source is None, search all marketplaces
            results = uacs.marketplace.search(asset_id, source, limit=5)

        # Filter for exact ID match if possible
        exact_matches = [r for r in results if r.id == asset_id]
        if exact_matches:
            results = exact_matches

        if not results:
            msg = f"Asset '{asset_id}' not found"
            if source:
                msg += f" in {source}"
            console.print(f"[red]✗[/red] {msg}")
            return

        if len(results) > 1:
            # If multiple matches and no source specified, ask user to choose
            if not source:
                console.print(
                    f"[yellow]Multiple assets found for '{asset_id}':[/yellow]"
                )
                for i, asset in enumerate(results, 1):
                    console.print(
                        f"  {i}. {asset.name} ({asset.marketplace}) - {asset.description}"
                    )

                choice = typer.prompt("Select asset number to install", type=int)
                if choice < 1 or choice > len(results):
                    console.print("[red]Invalid selection[/red]")
                    return
                asset = results[choice - 1]
            else:
                # If source specified but multiple results (unlikely with exact ID match logic above, but possible)
                asset = results[0]
        else:
            asset = results[0]

        # Show asset info
        console.print(f"\n[bold]{asset.name}[/bold]")
        console.print(f"  Type: {asset.asset_type}")
        console.print(f"  Author: {asset.author}")
        console.print(f"  Source: {asset.marketplace}")
        console.print(f"  Rating: {asset.rating}⭐ ({asset.downloads:,} downloads)")
        console.print(f"  Description: {asset.description}")

        # Confirm
        if not force:
            confirm = typer.confirm("\nInstall this asset?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Install
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Installing...", total=None)
            uacs.marketplace.install_asset(asset)

        console.print("[green]✓[/green] Successfully installed")
        if asset.asset_type == "mcp_server":
            console.print(
                "\n[dim]MCP Server configured. Restart agent to use tools.[/dim]"
            )
        else:
            console.print('\n[dim]Test with: uacs skills test "your query"[/dim]')

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error installing asset: {e}")


@app.command("list")
def list_assets(
    repository: str | None = typer.Option(
        None,
        "--repo",
        "-r",
        help="List packages from specific GitHub repo (owner/repo)",
    ),
    installed: bool = typer.Option(
        False, "--installed", "-i", help="List installed assets only"
    ),
    asset_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by type: 'skill' or 'mcp'",
    ),
    offset: int = typer.Option(0, "--offset", help="Pagination offset"),
    limit: int = typer.Option(20, "--limit", "-l", help="Items per page"),
    force_refresh: bool = typer.Option(
        False, "--force-refresh", "-f", help="Bypass cache and fetch fresh data"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Enable interactive pagination"
    ),
):
    """List marketplace assets.

    Examples:
        # List installed assets
        uacs marketplace list --installed

        # List all packages from a repository
        uacs marketplace list --repo agentskills/agentskills
        uacs marketplace list --repo modelcontextprotocol/servers --type mcp

        # Paginate through results
        uacs marketplace list --repo agentskills/agentskills --offset 20 --limit 10
    """
    uacs = get_uacs()

    # Handle --installed flag
    if installed:
        _list_installed_assets(uacs)
        return

    # Handle --repo flag
    if repository:
        _list_repository_packages(
            uacs, repository, asset_type, offset, limit, force_refresh, interactive
        )
        return

    # Default: show help about options
    console.print("[yellow]Please specify what to list:[/yellow]\n")
    console.print("  [cyan]--installed[/cyan]     List installed assets")
    console.print("  [cyan]--repo OWNER/REPO[/cyan]  List packages from a repository\n")
    console.print("Examples:")
    console.print("  uacs marketplace list --installed")
    console.print("  uacs marketplace list --repo agentskills/agentskills")


def _list_installed_assets(uacs):
    """List installed marketplace assets."""
    installed = uacs.marketplace.list_installed()

    if not installed:
        console.print("[yellow]No marketplace assets installed[/yellow]")
        console.print("\n[dim]Search assets with: uacs marketplace search QUERY[/dim]")
        return

    table = Table(
        title="Installed Marketplace Assets", show_header=True, header_style="bold cyan"
    )

    table.add_column("Name", style="cyan", width=30)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Author", style="green", width=20)
    table.add_column("Source", style="blue", width=15)
    table.add_column("Rating", justify="right", style="yellow", width=10)

    for asset in installed:
        table.add_row(
            asset.name,
            asset.asset_type,
            asset.author,
            asset.marketplace,
            f"{asset.rating:.1f}⭐",
        )

    console.print(table)
    console.print(f"\n[dim]Total installed: {len(installed)}[/dim]")


def _list_repository_packages(
    uacs, repository, asset_type, offset, limit, force_refresh, interactive
):
    """List all packages from a GitHub repository."""

    # Parse owner/repo
    if "/" not in repository:
        console.print(
            "[red]✗[/red] Invalid repository format. Use: owner/repo (e.g., agentskills/agentskills)"
        )
        return

    owner, repo = repository.split("/", 1)

    try:
        current_offset = offset

        while True:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description=f"Loading {owner}/{repo}...", total=None)
                result = uacs.marketplace.list_repository(
                    owner, repo, asset_type, current_offset, limit, force_refresh
                )

            # Display results
            items = result["items"]
            pagination = result["pagination"]
            from_cache = result["from_cache"]

            if not items and current_offset == 0:
                console.print(f"[yellow]No packages found in {owner}/{repo}[/yellow]")
                return

            # Show table
            cache_indicator = " [dim](cached)[/dim]" if from_cache else ""
            table = Table(
                title=f"{owner}/{repo} - Page {pagination['current_page']}/{pagination['total_pages']}{cache_indicator}",
                show_header=True,
                header_style="bold cyan",
            )

            table.add_column("#", style="dim", width=4)
            table.add_column("Name", style="cyan", width=30)
            table.add_column("Type", style="magenta", width=10)
            table.add_column("Description", style="white", width=60)

            for idx, item in enumerate(items, start=current_offset + 1):
                desc = (
                    item.description[:57] + "..."
                    if len(item.description) > 60
                    else item.description
                )
                table.add_row(
                    str(idx),
                    item.name,
                    item.asset_type,
                    desc,
                )

            console.print(table)

            # Show pagination info
            console.print(
                f"\n[dim]Showing {pagination['offset'] + 1}-{pagination['offset'] + pagination['count']} "
                f"of {pagination['total']} total[/dim]"
            )

            # Interactive pagination
            if interactive and pagination["has_next"]:
                if typer.confirm("\nShow more?", default=True):
                    current_offset += limit
                    force_refresh = False  # Use cache for subsequent pages
                else:
                    break
            else:
                break

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error listing repository: {e}")
        import traceback

        traceback.print_exc()


@app.command("cache")
def cache_management(
    repository: str | None = typer.Argument(
        None, help="Specific repository (owner/repo) for --clear operation"
    ),
    status: bool = typer.Option(False, "--status", "-s", help="Show cache status"),
    clear: bool = typer.Option(False, "--clear", "-c", help="Clear cache"),
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation for --clear"
    ),
):
    """Manage marketplace cache.

    Examples:
        uacs marketplace cache --status              # Show cache status
        uacs marketplace cache --clear               # Clear all cache
        uacs marketplace cache --clear OWNER/REPO    # Clear specific repo
        uacs marketplace cache -s                    # Short form for status
        uacs marketplace cache -c -y                 # Clear all without confirmation
    """
    uacs = get_uacs()

    # Show status
    if status:
        stats = uacs.marketplace.cache.get_stats()

        console.print("\n[bold cyan]Marketplace Cache Status[/bold cyan]\n")

        # Cache statistics
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="white")

        table.add_row("Total entries", str(stats.total_entries))
        table.add_row("Cache size", f"{stats.size_mb:.2f} MB")
        table.add_row("Cache hits", str(stats.cache_hits))
        table.add_row("Cache misses", str(stats.cache_misses))
        table.add_row("Hit rate", f"{stats.hit_rate:.1f}%")

        if stats.last_refresh:
            from datetime import datetime

            last_refresh = datetime.fromtimestamp(stats.last_refresh).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            table.add_row("Last refresh", last_refresh)

        console.print(table)

        # Cached repositories
        if stats.repos_cached:
            console.print("\n[bold]Cached Repositories:[/bold]\n")
            for repo in stats.repos_cached:
                console.print(f"  • {repo}")
        else:
            console.print("\n[dim]No repositories cached yet[/dim]")

        console.print("\n[dim]Clear cache with: uacs marketplace cache --clear[/dim]")
        return

    # Clear cache
    if clear:
        target = repository or "all cache"

        if not confirm:
            response = typer.confirm(f"Clear {target}?")
            if not response:
                console.print("[yellow]Cancelled[/yellow]")
                return

        try:
            if repository:
                # Clear specific repo
                if "/" not in repository:
                    console.print(
                        "[red]✗[/red] Invalid repository format. Use: owner/repo"
                    )
                    return

                owner, repo = repository.split("/", 1)
                cache_key = uacs.marketplace.cache.get_repo_cache_key(owner, repo)
                cleared = uacs.marketplace.cache.clear(cache_key)
            else:
                # Clear all
                cleared = uacs.marketplace.cache.clear()

            console.print(f"[green]✓[/green] Cleared {cleared} cache entries")

        except Exception as e:
            console.print(f"[red]✗[/red] Error clearing cache: {e}")
        return

    # No flags provided - show help
    console.print("[yellow]Please specify an action:[/yellow]\n")
    console.print("  [cyan]--status[/cyan]  (-s)  Show cache statistics")
    console.print("  [cyan]--clear[/cyan]   (-c)  Clear cache\n")
    console.print("Examples:")
    console.print("  uacs marketplace cache --status")
    console.print("  uacs marketplace cache --clear")
    console.print("  uacs marketplace cache --clear agentskills/agentskills")


@app.command("refresh")
def refresh_cache(
    repository: str | None = typer.Argument(
        None, help="Specific repository to refresh (owner/repo), or all if omitted"
    ),
):
    """Refresh marketplace cache.

    Examples:
        uacs marketplace refresh                         # Refresh all cached repos
        uacs marketplace refresh agentskills/agentskills # Refresh specific repo
    """
    uacs = get_uacs()

    if repository:
        # Refresh specific repo
        if "/" not in repository:
            console.print("[red]✗[/red] Invalid repository format. Use: owner/repo")
            return

        owner, repo = repository.split("/", 1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description=f"Refreshing {owner}/{repo}...", total=None)

            try:
                result = uacs.marketplace.list_repository(
                    owner, repo, force_refresh=True
                )
                count = result["pagination"]["total"]
                console.print(
                    f"[green]✓[/green] Refreshed {owner}/{repo} ({count} packages)"
                )
            except Exception as e:
                console.print(f"[red]✗[/red] Error refreshing {owner}/{repo}: {e}")

    else:
        # Refresh all cached repos
        stats = uacs.marketplace.cache.get_stats()
        repos = stats.repos_cached or []

        if not repos:
            console.print("[yellow]No cached repositories to refresh[/yellow]")
            return

        console.print(f"[cyan]Refreshing {len(repos)} repositories...[/cyan]\n")

        for repo_path in repos:
            if "/" not in repo_path:
                continue

            owner, repo = repo_path.split("/", 1)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(
                    description=f"Refreshing {owner}/{repo}...", total=None
                )

                try:
                    result = uacs.marketplace.list_repository(
                        owner, repo, force_refresh=True
                    )
                    count = result["pagination"]["total"]
                    console.print(f"[green]✓[/green] {owner}/{repo} ({count} packages)")
                except Exception as e:
                    console.print(f"[red]✗[/red] {owner}/{repo}: {e}")

        console.print("\n[green]✓[/green] Refresh complete")


@app.command("uninstall")
def uninstall_asset(
    asset_id: str = typer.Argument(..., help="Asset ID to uninstall"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Uninstall a marketplace asset."""
    uacs = get_uacs()

    try:
        if not confirm:
            response = typer.confirm(f"Uninstall asset '{asset_id}'?")
            if not response:
                console.print("[yellow]Cancelled[/yellow]")
                return

        uacs.marketplace.uninstall_asset(asset_id)
        console.print(f"[green]✓[/green] Uninstalled {asset_id}")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error uninstalling: {e}")


@app.command("categories")
def list_categories(
    marketplace: str | None = typer.Option(
        None, "--marketplace", "-m", help="Specific marketplace"
    ),
):
    """List available skill categories."""
    uacs = get_uacs()
    categories = uacs.marketplace.get_categories(marketplace)

    console.print("\n[bold cyan]Available Categories[/bold cyan]\n")

    for i, category in enumerate(categories, 1):
        console.print(f"  {i:2}. {category}")

    console.print(
        "\n[dim]Search by category: uacs marketplace search QUERY --category CATEGORY[/dim]"
    )


@app.command("info")
def marketplace_info():
    """Show marketplace information."""
    uacs = get_uacs()

    console.print("\n[bold cyan]Supported Marketplaces[/bold cyan]\n")

    for mp_id, mp_config in uacs.marketplace.MARKETPLACES.items():
        console.print(f"[bold]{mp_config['name']}[/bold]")
        console.print(f"  ID: {mp_id}")
        console.print(f"  URL: {mp_config['url']}")
        console.print(f"  Type: {mp_config['type']}")
        console.print()

    stats = uacs.marketplace.get_stats()

    console.print("[bold cyan]Your Stats[/bold cyan]\n")
    console.print(f"  Installed skills: {stats['installed_skills']}")
    console.print(f"  Cache size: {stats['cache_size_mb']:.2f} MB")
    console.print(f"  Available marketplaces: {stats['available_marketplaces']}")


__all__ = ["app"]


if __name__ == "__main__":
    app()
