"""Universal Agent Context System - Main API

See docs/uacs/README.md for details.
"""

from pathlib import Path
from typing import Any

from uacs.adapters.agent_skill_adapter import AgentSkillAdapter
from uacs.adapters.agents_md_adapter import AgentsMDAdapter
from uacs.context.shared_context import SharedContextManager
from uacs.context.unified_context import UnifiedContextAdapter
from uacs.marketplace.marketplace import (
    MarketplaceAdapter,
    MarketplaceAsset,
)


class UACS:
    """Universal Agent Context System

    Provides unified context management across:
    - Marketplace (Skills + MCP discovery)
    - Adapters (Format translation)
    - Context (Shared memory + compression)
    - Project metadata (AGENTS.md)

    Example:
        >>> uacs = UACS(project_path=Path("."))
        >>> results = uacs.search("code review")
        >>> context = uacs.build_context(query="...", agent="claude")
    """

    def __init__(
        self,
        project_path: Path,
        marketplace_repos: dict[str, list[str]] | None = None,
    ):
        """Initialize UACS.

        Args:
            project_path: Path to the project root
            marketplace_repos: Optional marketplace configuration
        """
        self.project_path = project_path

        # Initialize components
        self.marketplace = MarketplaceAdapter()

        # Detect and load project format adapters
        agents_md_path = project_path / "AGENTS.md"

        # Modern Agent Skills support (.agent/skills/)
        self.agent_skills = AgentSkillAdapter.discover_skills(project_path)

        self.agents_md = (
            AgentsMDAdapter(agents_md_path) if agents_md_path.exists() else None
        )

        # Initialize shared context and unified adapter
        self.shared_context = SharedContextManager(project_path / ".state" / "context")
        self.unified_context = UnifiedContextAdapter(
            agents_md_path=agents_md_path if agents_md_path.exists() else None,
            context_storage=project_path / ".state" / "context",
        )

    def search_marketplace(
        self,
        query: str,
        category: str | None = None,
        asset_type: str | None = None,
        limit: int = 20,
    ) -> list[MarketplaceAsset]:
        """Search for skills or MCP servers in the marketplace.

        Args:
            query: Search query
            category: Filter by category
            asset_type: Filter by type (skill, mcp_server)
            limit: Maximum results

        Returns:
            List of matching assets
        """
        return self.marketplace.search(
            query=query, category=category, asset_type=asset_type, limit=limit
        )

    def get_capabilities(self, agent: str | None = None) -> dict[str, Any]:
        """Get available capabilities for an agent.

        Args:
            agent: Optional agent name to filter capabilities

        Returns:
            Dictionary of capabilities
        """
        capabilities = self.unified_context.get_capabilities(agent_name=agent)

        # Add discovered Agent Skills
        if self.agent_skills:
            capabilities["agent_skills"] = [
                {
                    "name": skill.parsed.name,
                    "description": skill.parsed.description,
                    "triggers": skill.parsed.triggers,
                    "source": skill.source_directory or "local",
                }
                for skill in self.agent_skills
                if skill.parsed
            ]

        return capabilities

    def build_context(
        self,
        query: str,
        agent: str,
        max_tokens: int | None = None,
        topics: list[str] | None = None,
    ) -> str:
        """Build context for an agent query.

        Args:
            query: The query or task
            agent: Agent name (claude, gemini, etc.)
            max_tokens: Optional token limit
            topics: Optional topics to filter and prioritize context

        Returns:
            Formatted context string
        """
        # If topics are provided, use focused context
        if topics:
            focused_context = self.shared_context.get_focused_context(
                topics=topics, agent=agent, max_tokens=max_tokens or 4000
            )
            # Combine with unified context
            unified = self.unified_context.build_context(
                query=query, agent_name=agent, max_tokens=max_tokens
            )
            return f"{focused_context}\n\n{unified}" if focused_context else unified

        return self.unified_context.build_context(
            query=query, agent_name=agent, max_tokens=max_tokens
        )

    def add_to_context(
        self,
        key: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        topics: list[str] | None = None,
    ):
        """Add content to shared context.

        Args:
            key: Context key (used as agent name)
            content: Content to store
            metadata: Optional metadata
            topics: Optional topics for semantic filtering

        Example:
            uacs.add_to_context(
                "claude",
                "Reviewed auth.py, found SQL injection",
                topics=["code-review", "security"]
            )
        """
        # Add to shared context with topics
        self.shared_context.add_entry(
            content=content,
            agent=key,
            metadata=metadata,
            topics=topics,
        )

    def get_token_stats(self) -> dict[str, int]:
        """Get token usage statistics.

        Returns:
            Dictionary of token counts
        """
        return self.unified_context.get_token_stats()

    def export_config(self, output_path: Path):
        """Export UACS configuration.

        Args:
            output_path: Path to save configuration
        """
        self.unified_context.export_unified_config(output_path)

    def install(self, package: Any) -> dict[str, Any]:
        """Install package from marketplace.

        Args:
            package: Package to install (MarketplaceAsset or dict)

        Returns:
            Installation result with status and details
        """
        # Install the asset
        install_path = self.marketplace.install_asset(package)

        result = {
            "name": package.name if hasattr(package, "name") else str(package),
            "type": package.asset_type if hasattr(package, "asset_type") else "unknown",
            "path": str(install_path),
            "status": "installed",
        }

        # Reload adapters after installation
        agents_md_path = self.project_path / "AGENTS.md"

        self.agents_md = (
            AgentsMDAdapter(agents_md_path) if agents_md_path.exists() else None
        )

        # Reload Agent Skills
        self.agent_skills = AgentSkillAdapter.discover_skills(self.project_path)

        # Recreate unified context with updated adapters
        self.unified_context = UnifiedContextAdapter(
            agents_md_path=agents_md_path if agents_md_path.exists() else None,
            context_storage=self.project_path / ".state" / "context",
        )

        return result

    def visualize_context(self, output_path: Path | None = None) -> str:
        """Visualize context structure.

        Args:
            output_path: Optional path to save visualization

        Returns:
            Visualization string (ASCII art or HTML)
        """
        from uacs.visualization import ContextVisualizer

        visualizer = ContextVisualizer()
        # Get graph and stats from shared context
        graph = self.shared_context.get_graph()
        stats = self.shared_context.get_stats()

        # Render the visualizations
        graph_panel = visualizer.render_context_graph(graph)
        stats_table = visualizer.render_stats_table(stats)

        # Print to console
        visualizer.console.print(graph_panel)
        visualizer.console.print(stats_table)

        # Optionally save to file
        if output_path:
            output_path.write_text(f"Context Graph: {graph}\nStats: {stats}")
            return f"Visualization saved to {output_path}"

        return "Visualization rendered to console"

    def configure_marketplace(self, repos: dict[str, list[str]]) -> None:
        """Update marketplace repositories configuration.

        Args:
            repos: Dictionary mapping repo types to URLs
                   e.g., {'mcp': ['smithery'], 'skills': ['github.com/org/repo']}
        """
        # Store config
        config_path = self.project_path / ".state" / "marketplace_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        import json

        config_path.write_text(json.dumps(repos, indent=2))

        # Note: Marketplace update would happen here in Task 2.2
        # For now, just save the config

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive UACS statistics.

        Returns:
            Dictionary with statistics from all components
        """
        # Merge token stats with shared context stats
        token_stats = self.get_token_stats()
        context_stats = self.shared_context.get_stats()
        token_stats.update(context_stats)

        stats = {
            "project_path": str(self.project_path),
            "adapters": {
                "agent_skills": {
                    "count": len(self.agent_skills),
                    "paths": [str(s.file_path) for s in self.agent_skills],
                },
                "agents_md": {
                    "loaded": self.agents_md is not None,
                    "path": str(self.project_path / "AGENTS.md")
                    if self.agents_md
                    else None,
                },
            },
            "marketplace": {"cache_dir": str(self.marketplace.cache_dir)},
            "context": token_stats,
            "capabilities": self.get_capabilities(),
        }

        return stats


__all__ = ["UACS"]
