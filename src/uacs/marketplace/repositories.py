"""Repository adapters for different package sources."""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import httpx
import yaml
from dotenv import load_dotenv

from .packages import MCPPackage, Package, SkillPackage

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def load_curated_repos() -> list[dict[str, Any]]:
    """Load curated repositories from configuration file."""
    try:
        config_path = Path(__file__).parent.parent / "config" / "repositories.yaml"
        if not config_path.exists():
            logger.warning(f"Repositories config not found at {config_path}")
            return []

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config.get("repositories", [])
    except Exception as e:
        logger.error(f"Failed to load repositories config: {e}")
        return []


# Curated GitHub repositories for marketplace integration
CURATED_REPOS = load_curated_repos()


class RepositoryAdapter(ABC):
    """Base class for package repositories."""

    def __init__(self, config: dict[str, Any]):
        self.config = config

    @abstractmethod
    async def search(self, query: str) -> list[Package]:
        """Search repository for packages.

        Args:
            query: Search query string

        Returns:
            List of matching packages
        """
        pass

    @abstractmethod
    async def install(self, package: Package) -> dict[str, Any]:
        """Install package from repository.

        Args:
            package: Package to install

        Returns:
            Installation result dictionary
        """
        pass


class SmitheryRepository(RepositoryAdapter):
    """Smithery MCP marketplace repository."""

    SMITHERY_API = "https://smithery.ai/api/v1"

    async def search(self, query: str) -> list[Package]:
        """Search Smithery for MCP servers.

        Args:
            query: Search query

        Returns:
            List of matching packages
        """
        packages: list[Package] = []

        try:
            async with httpx.AsyncClient() as client:
                # Search Smithery API (this is a placeholder - adjust based on actual API)
                response = await client.get(
                    f"{self.SMITHERY_API}/servers", params={"q": query}, timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    servers = data.get("servers", [])

                    for server in servers:
                        package = MCPPackage(
                            name=server.get("name", ""),
                            description=server.get("description", ""),
                            source="smithery",
                            package_type="mcp",
                            url=server.get("url", ""),
                            version=server.get("version", "latest"),
                            tools=server.get("tools", []),
                            protocol_version=server.get("protocol_version", "1.0"),
                            install_command=server.get("install_command", ""),
                            config=server.get("config", {}),
                            metadata=server.get("metadata", {}),
                        )
                        packages.append(package)

        except Exception as e:
            # Log error but don't fail completely
            logger.warning("Error searching Smithery: %s", e)

        return packages

    async def install(self, package: Package) -> dict[str, Any]:
        """Install MCP server from Smithery.

        Args:
            package: MCP package to install

        Returns:
            Installation result
        """
        if not isinstance(package, MCPPackage):
            raise ValueError(f"Expected MCPPackage, got {type(package)}")

        # Installation is handled by MarketplaceAdapter._install_mcp_server
        return {"status": "ready", "package": package.name, "source": "smithery"}


class GitHubMCPRepository(RepositoryAdapter):
    """GitHub repository for MCP servers."""

    GITHUB_API = "https://api.github.com"

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize GitHub MCP repository.

        Args:
            config: Repository configuration (optional)
        """
        super().__init__(config or {})
        self._setup_auth_headers()

    def _setup_auth_headers(self) -> None:
        """Setup authentication headers for GitHub API."""
        self.headers = {"Accept": "application/vnd.github.v3+json"}

        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.headers["Authorization"] = f"Bearer {github_token}"
        else:
            print(
                "⚠️  Warning: No GITHUB_TOKEN found, using unauthenticated requests (60 req/hr limit)"
            )

    async def search(self, query: str) -> list[Package]:
        """Search GitHub for MCP servers.

        Args:
            query: Search query

        Returns:
            List of MCP packages
        """
        packages: list[Package] = []

        # Search curated MCP repositories
        for repo_config in CURATED_REPOS:
            if repo_config["type"] != "mcp":
                continue

            try:
                owner = repo_config["owner"]
                repo = repo_config["repo"]
                path = repo_config["path"]

                async with httpx.AsyncClient() as client:
                    # List directory contents
                    response = await client.get(
                        f"{self.GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
                        headers=self.headers,
                        timeout=10.0,
                    )

                    if response.status_code == 403:
                        logger.warning("Rate limit exceeded for %s/%s", owner, repo)
                        continue
                    if response.status_code == 404:
                        logger.debug("Path not found: %s/%s/%s", owner, repo, path)
                        continue
                    if response.status_code != 200:
                        continue

                    contents = response.json()

                    # Process each subdirectory (each is an MCP server)
                    for item in contents:
                        if item.get("type") != "dir":
                            continue

                        server_name = item["name"]

                        # Check if name matches query
                        if query.lower() not in server_name.lower():
                            continue

                        # Fetch package.json
                        try:
                            pkg_response = await client.get(
                                f"{self.GITHUB_API}/repos/{owner}/{repo}/contents/{path}/{server_name}/package.json",
                                headers=self.headers,
                                timeout=10.0,
                            )

                            if pkg_response.status_code == 200:
                                pkg_data = pkg_response.json()
                                # Decode base64 content
                                import base64

                                content = base64.b64decode(pkg_data["content"]).decode(
                                    "utf-8"
                                )
                                pkg_json = __import__("json").loads(content)

                                # Create MCPPackage
                                package = MCPPackage(
                                    name=pkg_json.get("name", server_name),
                                    description=pkg_json.get(
                                        "description", f"MCP server: {server_name}"
                                    ),
                                    source="github-mcp",
                                    package_type="mcp",
                                    url=f"https://github.com/{owner}/{repo}/tree/main/{path}/{server_name}",
                                    version=pkg_json.get("version", "latest"),
                                    tools=[],  # Could parse from README
                                    protocol_version="1.0",
                                    install_command=f"npx -y @{owner}/{server_name}",
                                    config={},
                                    metadata={
                                        "owner": owner,
                                        "repo": repo,
                                        "server_name": server_name,
                                        "npm_package": pkg_json.get("name", ""),
                                    },
                                )
                                packages.append(package)

                        except Exception:
                            # Skip individual server errors
                            continue

            except httpx.HTTPError as e:
                logger.warning("Network error searching %s: %s", repo_config["repo"], e)
                continue
            except Exception as e:
                logger.warning("Error searching %s: %s", repo_config["repo"], e)
                continue

        return packages

    async def install(self, package: Package) -> dict[str, Any]:
        """Install MCP server from GitHub.

        Args:
            package: MCP package to install

        Returns:
            Installation result
        """
        if not isinstance(package, MCPPackage):
            raise ValueError(f"Expected MCPPackage, got {type(package)}")

        return {"status": "ready", "package": package.name, "source": "github-mcp"}


class GitHubSkillsRepository(RepositoryAdapter):
    """GitHub repository for Skills."""

    GITHUB_API = "https://api.github.com"

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize GitHub Skills repository.

        Args:
            config: Repository configuration (optional)
        """
        super().__init__(config or {})
        self._setup_auth_headers()

    def _setup_auth_headers(self) -> None:
        """Setup authentication headers for GitHub API."""
        self.headers = {"Accept": "application/vnd.github.v3+json"}

        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.headers["Authorization"] = f"Bearer {github_token}"
        else:
            logger.warning(
                "No GITHUB_TOKEN found, using unauthenticated requests "
                "(60 req/hr limit)"
            )

    async def _find_skill_files(
        self, client: httpx.AsyncClient, owner: str, repo: str, path: str
    ) -> list[dict[str, Any]]:
        """Recursively find SKILL.md files in a repository.

        Args:
            client: HTTP client
            owner: Repository owner
            repo: Repository name
            path: Path to search

        Returns:
            List of file metadata dictionaries
        """
        skill_files = []

        try:
            response = await client.get(
                f"{self.GITHUB_API}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                timeout=10.0,
            )

            if response.status_code != 200:
                return skill_files

            contents = response.json()

            for item in contents:
                if item.get("type") == "file" and item["name"] == "SKILL.md":
                    skill_files.append(item)
                elif item.get("type") == "dir":
                    # Recursively search subdirectories
                    subpath = f"{path}/{item['name']}" if path else item["name"]
                    subfiles = await self._find_skill_files(
                        client, owner, repo, subpath
                    )
                    skill_files.extend(subfiles)

        except Exception:
            pass

        return skill_files

    async def search(self, query: str) -> list[Package]:
        """Search GitHub for skill files.

        Args:
            query: Search query

        Returns:
            List of skill packages
        """
        packages: list[Package] = []

        # Search curated skill repositories
        for repo_config in CURATED_REPOS:
            if repo_config["type"] != "skill":
                continue

            try:
                owner = repo_config["owner"]
                repo = repo_config["repo"]
                path = repo_config["path"]

                async with httpx.AsyncClient() as client:
                    # Find all SKILL.md files
                    skill_files = await self._find_skill_files(
                        client, owner, repo, path
                    )

                    for skill_file in skill_files:
                        # Fetch file content
                        try:
                            response = await client.get(
                                skill_file["download_url"], timeout=10.0
                            )

                            if response.status_code != 200:
                                continue

                            content = response.text

                            # Parse YAML frontmatter if present
                            name = skill_file["path"].split("/")[-2]  # Parent directory
                            description = f"Skill from {owner}/{repo}"
                            keywords = []

                            # Basic frontmatter parsing
                            if content.startswith("---"):
                                parts = content.split("---", 2)
                                if len(parts) >= 3:
                                    frontmatter = parts[1]
                                    # Extract name, description, keywords
                                    for line in frontmatter.split("\n"):
                                        if line.startswith("name:"):
                                            name = line.split(":", 1)[1].strip()
                                        elif line.startswith("description:"):
                                            description = line.split(":", 1)[1].strip()
                                        elif line.startswith("keywords:"):
                                            keywords_str = line.split(":", 1)[1].strip()
                                            keywords = [
                                                k.strip()
                                                for k in keywords_str.split(",")
                                            ]

                            # Check if query matches (skip filter if query is empty)
                            if query:  # Only filter if query provided
                                query_lower = query.lower()
                                if not (
                                    query_lower in name.lower()
                                    or query_lower in description.lower()
                                    or query_lower
                                    in content.lower()  # Search in content too!
                                    or any(query_lower in k.lower() for k in keywords)
                                ):
                                    continue

                            # Create SkillPackage
                            package = SkillPackage(
                                name=name,
                                description=description,
                                source="github-skills",
                                package_type="skill",
                                url=skill_file["html_url"],
                                version="1.0.0",
                                instructions=content,
                                triggers=keywords,
                                files=[skill_file["name"]],
                                metadata={
                                    "owner": owner,
                                    "repo": repo,
                                    "path": skill_file["path"],
                                },
                            )
                            packages.append(package)

                        except Exception:
                            # Skip individual file errors
                            continue

            except httpx.HTTPError as e:
                logger.warning("Network error searching %s: %s", repo_config["repo"], e)
                continue
            except Exception as e:
                logger.warning("Error searching %s: %s", repo_config["repo"], e)
                continue

        return packages

    async def install(self, package: Package) -> dict[str, Any]:
        """Install skill from GitHub.

        Args:
            package: Skill package to install

        Returns:
            Installation result
        """
        if not isinstance(package, SkillPackage):
            raise ValueError(f"Expected SkillPackage, got {type(package)}")

        return {"status": "ready", "package": package.name, "source": "github-skills"}


__all__ = [
    "CURATED_REPOS",
    "GitHubMCPRepository",
    "GitHubSkillsRepository",
    "RepositoryAdapter",
    "SmitheryRepository",
]
