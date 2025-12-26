"""Skills marketplace integration adapter.

Supports multiple marketplaces:
- GitHub (MCP servers and skills)
- SkillsMP.com (Claude skills from GitHub)
- Skills4Agents.com
- AgentShare.io
- Claude Skills Market
"""

import json
import logging
from pathlib import Path
from typing import Any, ClassVar, Literal

import httpx

logger = logging.getLogger(__name__)

# Optional MAOS integration
try:
    from uacs.protocols.mcp.manager import McpManager

    MAOS_AVAILABLE = True
except ImportError:
    MAOS_AVAILABLE = False
    McpManager = None  # type: ignore[assignment,misc]

from uacs.marketplace.cache import MarketplaceCache, paginate
from uacs.marketplace.repositories import (
    GitHubMCPRepository,
    GitHubSkillsRepository,
)


class MarketplaceAsset:
    def __init__(
        self,
        id: str = "",
        name: str = "",
        description: str = "",
        author: str = "unknown",
        category: str = "uncategorized",
        source_url: str = "",
        marketplace: str = "unknown",
        asset_type: Literal["skill", "mcp_server"] = "skill",
        downloads: int = 0,
        rating: float = 0.0,
        tags: list[str] | None = None,
        content: str | None = None,
        config: dict[str, Any] | None = None,
        **kwargs,  # Accept extra args to be safe
    ):
        self.id = id
        self.name = name
        self.description = description
        self.author = author
        self.category = category
        self.source_url = source_url
        self.marketplace = marketplace
        self.asset_type = asset_type
        self.downloads = downloads
        self.rating = rating
        self.tags = tags if tags is not None else []
        self.content = content
        self.config = config


class MarketplaceAdapter:
    """Unified adapter for multiple marketplaces."""

    MARKETPLACES: ClassVar[dict[str, dict[str, str]]] = {
        "github-mcp": {
            "name": "GitHub MCP Servers",
            "url": "https://github.com/modelcontextprotocol/servers",
            "type": "mcp_registry",
        },
        "github-skills": {
            "name": "GitHub Skills",
            "url": "https://github.com/agentskills",
            "type": "skill_aggregator",
        },
        # Future integrations (not yet implemented):
        # "skillsmp": SkillsMP.com API integration
        # "glama": Glama.ai MCP registry
    }

    def __init__(self, cache_dir: Path | None = None):
        """Initialize marketplace adapter.

        Args:
            cache_dir: Directory to cache downloaded assets
        """
        self.cache_dir = (
            cache_dir or Path.home() / ".cache" / "multi-agent-cli" / "assets"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.installed_assets: dict[str, MarketplaceAsset] = {}
        self._load_installed()

        # Initialize cache system
        self.cache = MarketplaceCache()

        # Initialize GitHub repositories
        self.github_mcp_repo = GitHubMCPRepository()
        self.github_skills_repo = GitHubSkillsRepository()

    def search(
        self,
        query: str,
        marketplace: str | None = None,
        category: str | None = None,
        asset_type: str | None = None,
        limit: int = 20,
        use_cache: bool = True,
    ) -> list[MarketplaceAsset]:
        """Search for assets across marketplaces.

        Args:
            query: Search query
            marketplace: Specific marketplace to search (None for all)
            category: Filter by category
            asset_type: Filter by asset type (skill, mcp_server)
            limit: Maximum results
            use_cache: Use cached results if available (default: True)

        Returns:
            List of matching assets
        """
        # Try cache first if enabled
        if use_cache and not marketplace and not category:
            cached = self.cache.get_search_results(query, asset_type)
            if cached:
                logger.debug(f"Using cached search results for: {query}")
                # Convert cached dicts back to MarketplaceAsset objects
                assets = [MarketplaceAsset(**item) for item in cached]
                return assets[:limit]
        results = []

        marketplaces = [marketplace] if marketplace else list(self.MARKETPLACES.keys())

        for mp in marketplaces:
            # Skip if marketplace doesn't support requested asset type
            mp_config = self.MARKETPLACES.get(mp)
            if not mp_config:
                continue

            if asset_type == "mcp_server" and mp_config["type"] == "skill_aggregator":
                continue
            if asset_type == "skill" and mp_config["type"] == "mcp_registry":
                continue

            try:
                mp_results = self._search_marketplace(mp, query, category, limit)
                results.extend(mp_results)
            except Exception:
                # print(f"Error searching {mp}: {e}")
                pass

        # Sort by relevance (downloads * rating)
        results.sort(key=lambda s: s.downloads * s.rating, reverse=True)

        final_results = results[:limit]

        # Cache results if simple search (no marketplace/category filters)
        if use_cache and not marketplace and not category and final_results:
            # Convert MarketplaceAsset objects to dicts for caching
            cache_data = [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "author": a.author,
                    "category": a.category,
                    "source_url": a.source_url,
                    "marketplace": a.marketplace,
                    "asset_type": a.asset_type,
                    "downloads": a.downloads,
                    "rating": a.rating,
                    "tags": a.tags,
                    "config": a.config,
                }
                for a in final_results
            ]
            self.cache.set_search_results(query, asset_type, cache_data)
            logger.debug(f"Cached {len(cache_data)} search results for: {query}")

        return final_results

    def _search_marketplace(
        self, marketplace: str, query: str, category: str | None, limit: int
    ) -> list[MarketplaceAsset]:
        """Search a specific marketplace.

        Args:
            marketplace: Marketplace ID
            query: Search query
            category: Category filter
            limit: Result limit

        Returns:
            List of skills from this marketplace
        """
        # Use real GitHub repositories
        if marketplace == "github-mcp":
            return self._search_github_mcp(query, limit)
        if marketplace == "github-skills":
            return self._search_github_skills(query, limit)
        # Unknown marketplace - return empty results
        return []

    async def _search_github_mcp_async(
        self, query: str, limit: int
    ) -> list[MarketplaceAsset]:
        """Async search GitHub MCP repositories."""
        packages = await self.github_mcp_repo.search(query)

        # Convert Package objects to MarketplaceAsset
        assets = []
        for pkg in packages[:limit]:
            asset = MarketplaceAsset(
                id=pkg.name,
                name=pkg.name,
                description=pkg.description,
                author=pkg.metadata.get("owner", "unknown"),
                category="system",
                source_url=pkg.url,
                marketplace="github-mcp",
                asset_type="mcp_server",
                downloads=0,  # GitHub doesn't provide download counts easily
                rating=0.0,
                tags=["mcp", "github"],
                config={
                    "command": "npx",
                    "args": ["-y", pkg.metadata.get("npm_package", pkg.name)],
                },
            )
            assets.append(asset)

        return assets

    def _search_github_mcp(self, query: str, limit: int) -> list[MarketplaceAsset]:
        """Synchronous wrapper for GitHub MCP search."""
        import asyncio

        try:
            return asyncio.run(self._search_github_mcp_async(query, limit))
        except Exception as e:
            logger.warning("Error searching GitHub MCP: %s", e)
            return []

    async def _search_github_skills_async(
        self, query: str, limit: int
    ) -> list[MarketplaceAsset]:
        """Async search GitHub Skills repositories."""
        packages = await self.github_skills_repo.search(query)

        # Convert Package objects to MarketplaceAsset
        assets = []
        for pkg in packages[:limit]:
            asset = MarketplaceAsset(
                id=pkg.name,
                name=pkg.name,
                description=pkg.description,
                author=pkg.metadata.get("owner", "unknown"),
                category="skill",
                source_url=pkg.url,
                marketplace="github-skills",
                asset_type="skill",
                downloads=0,
                rating=0.0,
                tags=getattr(pkg, "triggers", []),
                content=getattr(pkg, "instructions", ""),
            )
            assets.append(asset)

        return assets

    def _search_github_skills(self, query: str, limit: int) -> list[MarketplaceAsset]:
        """Synchronous wrapper for GitHub Skills search."""
        import asyncio

        try:
            return asyncio.run(self._search_github_skills_async(query, limit))
        except Exception as e:
            logger.warning("Error searching GitHub Skills: %s", e)
            return []

    def list_repository(
        self,
        owner: str,
        repo: str,
        asset_type: str | None = None,
        offset: int = 0,
        limit: int = 20,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """List all packages from a GitHub repository (cached).

        Args:
            owner: Repository owner
            repo: Repository name
            asset_type: Filter by asset type ('skill' or 'mcp_server')
            offset: Pagination offset
            limit: Items per page
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            Dictionary with paginated items and metadata
        """
        # Check cache first unless force refresh
        cached_data = None
        if not force_refresh:
            cached_data = self.cache.get_repo_index(owner, repo)

        if cached_data:
            logger.info(f"Using cached data for {owner}/{repo}")
            packages = cached_data.get("packages", [])
        else:
            # Fetch fresh data from GitHub
            logger.info(f"Fetching fresh data for {owner}/{repo}")
            packages = self._fetch_repo_packages(owner, repo, asset_type)

            # Cache the results
            if packages:
                # Convert MarketplaceAsset to dict for caching
                cache_data = [
                    {
                        "id": a.id,
                        "name": a.name,
                        "description": a.description,
                        "author": a.author,
                        "category": a.category,
                        "source_url": a.source_url,
                        "marketplace": a.marketplace,
                        "asset_type": a.asset_type,
                        "downloads": a.downloads,
                        "rating": a.rating,
                        "tags": a.tags,
                        "config": a.config,
                    }
                    for a in packages
                ]
                self.cache.set_repo_index(owner, repo, cache_data)

        # Convert dicts back to MarketplaceAsset objects first
        if packages and isinstance(packages[0], dict):
            packages = [MarketplaceAsset(**p) for p in packages]

        # Filter by asset type if specified
        if asset_type:
            type_filter = "mcp_server" if asset_type == "mcp" else asset_type
            packages = [p for p in packages if p.asset_type == type_filter]

        # Paginate results
        paginated = paginate(packages, offset, limit)

        return {
            "owner": owner,
            "repo": repo,
            "items": paginated["items"],
            "pagination": paginated["pagination"],
            "from_cache": cached_data is not None and not force_refresh,
        }

    def _fetch_repo_packages(
        self, owner: str, repo: str, asset_type: str | None = None
    ) -> list[MarketplaceAsset]:
        """Fetch all packages from a GitHub repository.

        Args:
            owner: Repository owner
            repo: Repository name
            asset_type: Optional asset type filter

        Returns:
            List of MarketplaceAsset objects
        """
        import asyncio

        # Determine repo type from CURATED_REPOS
        from uacs.marketplace.repositories import CURATED_REPOS

        repo_config = None
        for config in CURATED_REPOS:
            if config["owner"] == owner and config["repo"] == repo:
                repo_config = config
                break

        if not repo_config:
            logger.warning(f"Repository {owner}/{repo} not in curated list")
            return []

        repo_type = repo_config["type"]

        # Filter by asset type if specified
        if asset_type:
            type_filter = "mcp" if asset_type == "mcp_server" else asset_type
            if repo_type != type_filter:
                logger.warning(
                    f"Repository {owner}/{repo} is type '{repo_type}', not '{type_filter}'"
                )
                return []

        # Fetch packages based on type
        if repo_type == "mcp":
            try:
                packages = asyncio.run(
                    self.github_mcp_repo.search("")
                )  # Empty query = list all
                # Convert to MarketplaceAsset
                assets = []
                for pkg in packages:
                    asset = MarketplaceAsset(
                        id=pkg.name,
                        name=pkg.name,
                        description=pkg.description,
                        author=pkg.metadata.get("owner", "unknown"),
                        category="system",
                        source_url=pkg.url,
                        marketplace="github-mcp",
                        asset_type="mcp_server",
                        downloads=0,
                        rating=0.0,
                        tags=["mcp", "github"],
                        config={
                            "command": "npx",
                            "args": ["-y", pkg.metadata.get("npm_package", pkg.name)],
                        },
                    )
                    assets.append(asset)
                return assets
            except Exception as e:
                logger.error(f"Error fetching MCP packages: {e}")
                return []

        elif repo_type == "skill":
            try:
                packages = asyncio.run(
                    self.github_skills_repo.search("")
                )  # Empty query = list all
                # Convert to MarketplaceAsset
                assets = []
                for pkg in packages:
                    asset = MarketplaceAsset(
                        id=pkg.name,
                        name=pkg.name,
                        description=pkg.description,
                        author=pkg.metadata.get("owner", "unknown"),
                        category="general",
                        source_url=pkg.url,
                        marketplace="github-skills",
                        asset_type="skill",
                        downloads=0,
                        rating=0.0,
                        tags=getattr(pkg, "triggers", []),
                        content=getattr(pkg, "instructions", ""),
                    )
                    assets.append(asset)
                return assets
            except Exception as e:
                logger.error(f"Error fetching skill packages: {e}")
                return []

        return []

    def install_asset(
        self, asset: MarketplaceAsset, destination: Path | None = None
    ) -> Path:
        """Install an asset from marketplace.

        Args:
            asset: Asset to install (Package or MarketplaceAsset)
            destination: Installation path (default: user's SKILLS.md for skills)

        Returns:
            Path to installed asset or config
        """
        # Support both old MarketplaceAsset and new Package types
        asset_type = getattr(
            asset, "package_type", getattr(asset, "asset_type", "skill")
        )

        if asset_type == "mcp" or asset_type == "mcp_server":
            return self._install_mcp_server(asset)
        return self._install_skill(asset, destination)

    def _install_mcp_server(self, asset: MarketplaceAsset) -> Path:
        """Install an MCP server asset."""
        if not asset.config:
            raise ValueError(f"MCP server asset {asset.name} missing config")

        # Security: Whitelist allowed commands
        allowed_commands = {"npx", "uv", "python", "python3", "node", "docker"}
        command = asset.config["command"]

        if command not in allowed_commands:
            # Check if it's a full path to a known safe executable (optional, for now strict whitelist)
            raise ValueError(
                f"Command '{command}' is not allowed. Allowed: {', '.join(allowed_commands)}"
            )

        # Process args for placeholders
        args = asset.config.get("args", [])
        processed_args = []
        for arg in args:
            if "{cwd}" in arg:
                arg = arg.replace("{cwd}", str(Path.cwd()))
            processed_args.append(arg)

        # Security: Validate arguments to prevent inline execution
        self._validate_mcp_args(command, processed_args)

        manager = McpManager()
        manager.add_server(
            name=asset.id,
            command=command,
            args=processed_args,
            env=asset.config.get("env", {}),
        )

        self._cache_asset(asset)
        return manager.config_file

    def _validate_mcp_args(self, command: str, args: list[str]):
        """Validate arguments for known interpreters to prevent inline execution."""
        # Block inline execution flags for interpreters
        if command in ("python", "python3"):
            for arg in args:
                if arg.strip() == "-c":
                    raise ValueError(
                        f"Inline execution (-c) is not allowed for {command}"
                    )

        if command == "node":
            for arg in args:
                if arg.strip() in ("-e", "--eval", "--print", "-p"):
                    raise ValueError(f"Inline execution is not allowed for {command}")

        # Block shell operators in arguments (basic check)
        dangerous_chars = [";", "&&", "||", "`", "$("]
        for arg in args:
            for char in dangerous_chars:
                if char in arg:
                    logger.warning(
                        f"Suspicious character '{char}' found in argument: {arg}"
                    )

    def _install_skill(
        self, skill: MarketplaceAsset, destination: Path | None = None
    ) -> Path:
        """Install a skill asset.

        Installs to .agent/skills/<name>/SKILL.md by default (Agent Skills standard).
        """
        # Download skill content
        if not skill.content:
            skill.content = self._download_asset_content(skill)

        # Determine installation path
        if destination is None:
            # Use new Agent Skills standard: .agent/skills/<name>/SKILL.md
            destination = Path.cwd() / ".agent" / "skills" / skill.name / "SKILL.md"

        # Ensure parent directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Format content (ensure it has frontmatter if missing)
        content = skill.content
        if not content.startswith("---"):
            # Add minimal frontmatter for Agent Skills format
            content = f"---\nname: {skill.name}\ndescription: {skill.description}\n---\n\n{content}"

        destination.write_text(content)
        self._cache_asset(skill)

        return destination

    def _cache_asset(self, asset: MarketplaceAsset):
        """Cache installed asset metadata."""
        cache_file = self.cache_dir / f"{asset.id}.json"
        cache_file.write_text(
            json.dumps(
                {
                    "asset": asset.__dict__,
                    "installed_at": __import__("datetime").datetime.now().isoformat(),
                },
                indent=2,
            )
        )

        self.installed_assets[asset.id] = asset

    def _download_asset_content(self, asset: MarketplaceAsset) -> str:
        """Download asset content from source.

        Args:
            asset: Asset to download

        Returns:
            Asset content
        """
        # For GitHub URLs, fetch raw SKILL.md
        if asset.source_url and "github.com" in asset.source_url:
            # Convert to raw URL
            raw_url = asset.source_url.replace(
                "github.com", "raw.githubusercontent.com"
            )
            raw_url = raw_url.replace("/blob/", "/")

            try:
                with httpx.Client() as client:
                    response = client.get(raw_url + "/SKILL.md", timeout=10)
                    if response.status_code == 200:
                        return response.text
            except Exception as e:
                logger.warning("Error downloading from GitHub: %s", e)

        # Return mock content for demo
        return self._generate_mock_asset_content(asset)

    def _generate_mock_asset_content(self, asset: MarketplaceAsset) -> str:
        """Generate mock asset content for demonstration."""
        return f"""## {asset.name}

### Description
{asset.description}

### Triggers
- {asset.name.lower()}
- {asset.tags[0] if asset.tags else "general"}

### Instructions
This is a marketplace asset from {asset.marketplace}.

1. Analyze the request
2. Apply asset expertise
3. Provide detailed response

### Examples
```
User: Use {asset.name}
Agent: I'll apply the {asset.name} asset...
```

### Metadata
author: {asset.author}
source: {asset.marketplace}
downloads: {asset.downloads}
rating: {asset.rating}
tags: {", ".join(asset.tags)}
"""

    def list_installed(self) -> list[MarketplaceAsset]:
        """List installed marketplace assets.

        Returns:
            List of installed assets
        """
        return list(self.installed_assets.values())

    def uninstall_asset(self, asset_id: str, destination: Path | None = None):
        """Uninstall a marketplace asset.

        Args:
            asset_id: Asset ID to uninstall
            destination: Path to skill directory (optional)
        """
        if asset_id not in self.installed_assets:
            raise ValueError(f"Asset {asset_id} not installed")

        asset = self.installed_assets[asset_id]

        if asset.asset_type == "mcp_server":
            manager = McpManager()
            manager.remove_server(asset.id)
        else:
            # Uninstall skill from .agent/skills/<name>
            if destination is None:
                destination = Path.cwd() / ".agent" / "skills" / asset.name

            if destination.exists() and destination.is_dir():
                import shutil

                shutil.rmtree(destination)
            elif destination.exists() and destination.is_file():
                # Fallback for single file installs (unlikely with new format but safe to handle)
                destination.unlink()

        # Remove from cache
        cache_file = self.cache_dir / f"{asset_id}.json"
        if cache_file.exists():
            cache_file.unlink()

        del self.installed_assets[asset_id]

    def _load_installed(self):
        """Load list of installed assets from cache."""
        if not self.cache_dir.exists():
            return

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(cache_file.read_text())
                if "asset" in data:
                    asset_data = data["asset"]
                    # Handle old format with 'source' instead of 'source_url'
                    if "source" in asset_data and "source_url" not in asset_data:
                        asset_data["source_url"] = asset_data.pop("source")
                    # Handle old format with 'package_type' instead of 'asset_type'
                    if "package_type" in asset_data and "asset_type" not in asset_data:
                        asset_data["asset_type"] = asset_data.pop("package_type")
                    asset = MarketplaceAsset(**asset_data)
                    self.installed_assets[asset.id] = asset
                elif "skill" in data:
                    # Migration for old format
                    skill_data = data["skill"]
                    asset = MarketplaceAsset(
                        id=skill_data["id"],
                        name=skill_data["name"],
                        description=skill_data["description"],
                        author=skill_data["author"],
                        category=skill_data.get("category", "unknown"),
                        source_url=skill_data.get("url", ""),
                        marketplace=skill_data.get("marketplace", "unknown"),
                        asset_type="skill",
                        downloads=skill_data.get("downloads", 0),
                        rating=skill_data.get("rating", 0.0),
                        tags=skill_data.get("tags", []),
                        content=skill_data.get("content"),
                    )
                    self.installed_assets[asset.id] = asset
            except Exception as e:
                logger.warning("Error loading cached asset %s: %s", cache_file, e)

    def get_categories(self, marketplace: str | None = None) -> list[str]:
        """Get available categories.

        Args:
            marketplace: Specific marketplace (None for all)

        Returns:
            List of category names
        """
        # Standard categories across marketplaces
        return [
            "code",
            "design",
            "data",
            "devops",
            "security",
            "testing",
            "documentation",
            "business",
            "research",
            "automation",
        ]

    def get_marketplace_stats(self) -> dict[str, Any]:
        """Get statistics about marketplace usage.

        Returns:
            Statistics dictionary
        """
        return {
            "installed_skills": len(self.installed_assets),
            "cache_size_mb": sum(f.stat().st_size for f in self.cache_dir.glob("*"))
            / (1024 * 1024),
            "available_marketplaces": len(self.MARKETPLACES),
            "marketplaces": list(self.MARKETPLACES.keys()),
        }
