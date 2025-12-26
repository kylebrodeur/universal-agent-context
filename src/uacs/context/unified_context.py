"""Unified context adapter combining SKILLS.md, AGENTS.md, and shared context.

This module creates a single unified interface for all agent context sources:
- SKILL.md: Individual skill files (Agent Skills format, recommended)
- AGENTS.md: Project-specific instructions
- Shared Context: Runtime agent communication with compression
"""

import json
from pathlib import Path
from typing import Any

from uacs.adapters.agent_skill_adapter import AgentSkillAdapter
from uacs.adapters.agents_md_adapter import AgentsMDAdapter
from uacs.context.shared_context import SharedContextManager
from uacs.utils.paths import get_project_root


class UnifiedContextAdapter:
    """Unified adapter for all agent context sources."""

    def __init__(
        self,
        agents_md_path: Path | None = None,
        context_storage: Path | None = None,
    ):
        """Initialize unified adapter.

        Args:
            agents_md_path: Path to AGENTS.md or project root
            context_storage: Path for shared context storage
        """
        # Initialize all adapters
        self.agents_md = AgentsMDAdapter(agents_md_path)
        self.shared_context = SharedContextManager(context_storage)
        self.agent_skills = AgentSkillAdapter.discover_skills(get_project_root())

    def build_agent_prompt(
        self,
        user_query: str,
        agent_name: str,
        include_history: bool = True,
        max_context_tokens: int = 4000,
    ) -> str:
        """Build complete agent prompt with all context sources.

        Args:
            user_query: User's query
            agent_name: Name of agent receiving prompt
            include_history: Include shared context history
            max_context_tokens: Max tokens for context

        Returns:
            Complete prompt string
        """
        prompt_parts = []

        # 1. AGENTS.md project context (if available)
        agents_md_prompt = self.agents_md.to_system_prompt()
        if agents_md_prompt:
            prompt_parts.append("# PROJECT CONTEXT (from AGENTS.md)")
            prompt_parts.append(agents_md_prompt)
            prompt_parts.append("")

        # 2. Skills capabilities (search Agent Skills format)
        skill_prompt = None

        # Try Agent Skills format (recommended)
        for adapter in self.agent_skills:
            if adapter.parsed and hasattr(adapter.parsed, "triggers"):
                query_lower = user_query.lower()
                for trigger in adapter.parsed.triggers:
                    if trigger.lower() in query_lower or query_lower in trigger.lower():
                        skill_prompt = adapter.to_system_prompt()
                        break
            if skill_prompt:
                break

        if skill_prompt:
            prompt_parts.append("# ACTIVE SKILL")
            prompt_parts.append(skill_prompt)
            prompt_parts.append("")

        # 3. Shared context from other agents (if enabled)
        if include_history:
            # Reserve tokens for history
            reserved_tokens = max_context_tokens // 2
            context_history = self.shared_context.get_compressed_context(
                agent=None,  # Include all agents
                max_tokens=reserved_tokens,
            )

            if context_history:
                prompt_parts.append("# SHARED CONTEXT (from other agents)")
                prompt_parts.append(context_history)
                prompt_parts.append("")

        # 4. User query
        prompt_parts.append("# USER REQUEST")
        prompt_parts.append(user_query)

        full_prompt = "\n".join(prompt_parts)

        # Store this interaction in shared context
        self.shared_context.add_entry(
            content=f"Query: {user_query[:200]}...", agent=agent_name, references=[]
        )

        return full_prompt

    def export_config(self, output_path: Path) -> None:
        """Export unified context configuration.

        Args:
            output_path: Path to save configuration
        """
        config = {
            "skills_path": ".agent/skills/",
            "agents_md_path": str(self.agents_md.file_path)
            if self.agents_md.file_path
            else None,
            "context_storage": str(self.shared_context.storage_path)
            if self.shared_context.storage_path
            else None,
            "capabilities": self.get_unified_capabilities(),
        }

        output_path.write_text(json.dumps(config, indent=2))

    def record_agent_response(
        self, agent_name: str, response: str, references: list | None = None
    ) -> str:
        """Record agent response in shared context.

        Args:
            agent_name: Name of responding agent
            response: Agent's response
            references: IDs of context entries referenced

        Returns:
            Entry ID
        """
        return self.shared_context.add_entry(
            content=response, agent=agent_name, references=references or []
        )

    def get_unified_capabilities(self) -> dict[str, Any]:
        """Get all capabilities from all sources.

        Returns:
            Combined capabilities dictionary
        """
        skills_capabilities = []
        available_skills = []

        for adapter in self.agent_skills:
            if adapter.parsed:
                skills_capabilities.append(adapter.to_adk_capabilities())
                available_skills.append(adapter.parsed.name)

        return {
            "skills": skills_capabilities,
            "project_context": self.agents_md.to_adk_capabilities(),
            "shared_context_stats": self.shared_context.get_stats(),
            "available_skills": available_skills,
            "agents_md_loaded": self.agents_md.config is not None,
        }

    def get_token_stats(self) -> dict[str, Any]:
        """Get token usage statistics across all sources.

        Returns:
            Token statistics
        """
        context_stats = self.shared_context.get_stats()

        # Estimate tokens from AGENTS.md
        agents_md_tokens = 0
        if self.agents_md.config:
            agents_md_prompt = self.agents_md.to_system_prompt()
            agents_md_tokens = len(agents_md_prompt) // 4

        # Estimate tokens from Agent Skills
        skills_tokens = 0
        for adapter in self.agent_skills:
            skill_prompt = adapter.to_system_prompt()
            skills_tokens += len(skill_prompt) // 4

        return {
            "agents_md_tokens": agents_md_tokens,
            "skills_tokens": skills_tokens,
            "shared_context_tokens": context_stats["total_tokens"],
            "tokens_saved_by_compression": context_stats["tokens_saved"],
            "total_potential_tokens": agents_md_tokens
            + skills_tokens
            + context_stats["total_tokens"],
            "compression_ratio": context_stats["compression_ratio"],
        }

    def optimize_context(self):
        """Trigger context optimization (compression, summarization).

        This is called automatically but can be triggered manually.
        """
        # The shared context manager handles this internally
        self.shared_context._auto_compress()

    def export_unified_config(self, output_path: Path):
        """Export unified configuration to JSON.

        Args:
            output_path: Path to save configuration
        """

        config = {
            "capabilities": self.get_unified_capabilities(),
            "token_stats": self.get_token_stats(),
            "context_graph": self.shared_context.get_context_graph(),
        }

        output_path.write_text(json.dumps(config, indent=2))

    def visualize_context(self):
        """Launch interactive context visualization."""

    from uacs.visualization import ContextVisualizer

    def create_snapshot(self, name: str) -> dict[str, Any]:
        """Create snapshot of current context state.

        Args:
            name: Snapshot name

        Returns:
            Snapshot data
        """
        snapshot = {
            "name": name,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "capabilities": self.get_unified_capabilities(),
            "token_stats": self.get_token_stats(),
            "context_entries": len(self.shared_context.entries),
            "summaries": len(self.shared_context.summaries),
        }

        # Save snapshot
        snapshot_path = self.shared_context.storage_path / f"snapshot_{name}.json"

        snapshot_path.write_text(json.dumps(snapshot, indent=2))

        return snapshot

    def get_compression_report(self) -> str:
        """Get detailed compression report.

        Returns:
            Formatted report string
        """
        stats = self.shared_context.get_stats()
        token_stats = self.get_token_stats()

        report = f"""
# Context Compression Report

## Overall Statistics
- Total Entries: {stats["entry_count"]}
- Summaries Created: {stats["summary_count"]}
- Compression Ratio: {stats["compression_ratio"]}
- Storage Size: {stats["storage_size_mb"]:.2f} MB

## Token Savings
- Original Tokens: {stats["total_tokens"] + stats["tokens_saved"]:,}
- Current Tokens: {stats["total_tokens"]:,}
- Saved by Compression: {stats["tokens_saved"]:,}
- Effective Reduction: {stats["compression_ratio"]}

## Source Breakdown
- AGENTS.md: {token_stats["agents_md_tokens"]:,} tokens
- SKILLS.md: {token_stats["skills_tokens"]:,} tokens (across {len(self.skills.skills)} skills)
- Shared Context: {token_stats["shared_context_tokens"]:,} tokens

## Recommendations
"""

        # Add recommendations based on stats
        if stats["entry_count"] > 20:
            report += "- Consider creating more summaries to reduce token usage\n"

        if stats["compression_ratio"] == "0%":
            report += (
                "- No compression active yet - will auto-compress after 10+ entries\n"
            )

        if token_stats["shared_context_tokens"] > 4000:
            report += "- Shared context is large - consider reviewing old entries\n"

        return report

    def get_capabilities(self, agent_name: str | None = None) -> dict[str, Any]:
        """Get available capabilities for an agent.

        Args:
            agent_name: Optional agent name to filter capabilities

        Returns:
            Dictionary of capabilities
        """
        skill_names = [s.parsed.name for s in self.agent_skills if s.parsed]
        return {
            "skills": skill_names,
            "agents_md_loaded": self.agents_md.exists(),
            "context_entries": len(self.shared_context.entries),
        }

    def build_context(
        self, query: str, agent_name: str, max_tokens: int | None = None
    ) -> str:
        """Build context for an agent query.

        Args:
            query: The query or task
            agent_name: Agent name
            max_tokens: Optional token limit

        Returns:
            Formatted context string
        """
        return self.build_agent_prompt(
            user_query=query,
            agent_name=agent_name,
            max_context_tokens=max_tokens or 4000,
        )
