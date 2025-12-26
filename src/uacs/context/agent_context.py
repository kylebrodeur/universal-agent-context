"""Agent-specific context adaptation for chat orchestration.

This module provides agent-specific context profiles with customized token allocation
and priority-based content selection.
"""

from pathlib import Path
from typing import Any

from uacs.adapters.agent_skill_adapter import AgentSkillAdapter
from uacs.adapters.agents_md_adapter import AgentsMDAdapter
from uacs.context.shared_context import SharedContextManager
from uacs.utils.paths import get_project_root

# Optional MAOS integration
try:
    from multi_agent_cli.maos.conversation import ConversationManager

    MAOS_AVAILABLE = True
except ImportError:
    MAOS_AVAILABLE = False
    ConversationManager = None  # type: ignore[assignment,misc]

# Default context profiles for each agent
AGENT_CONTEXT_PROFILES = {
    "claude": {
        "priority": ["reasoning", "analysis", "architecture"],
        "token_allocation": {
            "agents_md": 0.30,  # 30% - High project context
            "skills": 0.20,  # 20% - Relevant skills
            "conversation": 0.30,  # 30% - Full conversation history
            "shared_context": 0.20,  # 20% - Shared memory
        },
        "history_depth": 10,  # More history for analysis
        "compress_threshold": 0.5,  # Less aggressive compression
    },
    "gemini": {
        "priority": ["code", "implementation", "examples"],
        "token_allocation": {
            "agents_md": 0.15,  # 15% - Less project context
            "skills": 0.35,  # 35% - More skills/capabilities
            "conversation": 0.25,  # 25% - Recent conversation
            "shared_context": 0.25,  # 25% - Shared memory
        },
        "history_depth": 5,  # Recent context only
        "compress_threshold": 0.7,  # More aggressive compression
    },
    "copilot": {
        "priority": ["code", "shell", "quick-answers"],
        "token_allocation": {
            "agents_md": 0.10,  # 10% - Minimal project context
            "skills": 0.40,  # 40% - Heavy skills focus
            "conversation": 0.30,  # 30% - Recent turns
            "shared_context": 0.20,  # 20% - Shared memory
        },
        "history_depth": 3,  # Very recent only
        "compress_threshold": 0.8,  # Aggressive compression
    },
    "openai": {
        "priority": ["general", "creative", "structured"],
        "token_allocation": {
            "agents_md": 0.25,  # 25% - Balanced
            "skills": 0.25,  # 25% - Balanced
            "conversation": 0.25,  # 25% - Balanced
            "shared_context": 0.25,  # 25% - Balanced
        },
        "history_depth": 7,  # Moderate history
        "compress_threshold": 0.6,  # Moderate compression
    },
}

# Pre-defined context strategies
CONTEXT_STRATEGIES = {
    "code_heavy": {
        "token_allocation": {
            "agents_md": 0.10,
            "skills": 0.50,
            "conversation": 0.25,
            "shared_context": 0.15,
        },
        "priority": ["code", "implementation", "examples"],
    },
    "analysis_heavy": {
        "token_allocation": {
            "agents_md": 0.35,
            "skills": 0.15,
            "conversation": 0.35,
            "shared_context": 0.15,
        },
        "priority": ["reasoning", "analysis", "architecture"],
    },
    "balanced": {
        "token_allocation": {
            "agents_md": 0.25,
            "skills": 0.25,
            "conversation": 0.25,
            "shared_context": 0.25,
        },
        "priority": ["general", "balanced"],
    },
}


class AgentContextAdapter:
    """Builds agent-specific context based on profiles."""

    def __init__(
        self,
        skills_path: Path | None = None,
        agents_md_path: Path | None = None,
        context_storage: Path | None = None,
    ):
        """Initialize agent context adapter.

        Args:
            skills_path: Path to SKILLS.md (ignored, using project root for discovery)
            agents_md_path: Path to AGENTS.md or project root
            context_storage: Path for shared context storage
        """
        self.project_root = get_project_root()
        self.agents_md = AgentsMDAdapter(agents_md_path)
        self.shared_context = SharedContextManager(context_storage)
        self.custom_profiles: dict[str, dict[str, Any]] = {}

    def get_profile(self, agent_name: str) -> dict[str, Any]:
        """Get context profile for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Profile dictionary with token allocation and priorities
        """
        # Check for custom profile first
        if agent_name in self.custom_profiles:
            return self.custom_profiles[agent_name]

        # Fall back to default profile
        return AGENT_CONTEXT_PROFILES.get(agent_name, AGENT_CONTEXT_PROFILES["openai"])

    def set_custom_profile(self, agent_name: str, profile: dict[str, Any]):
        """Set a custom profile for an agent.

        Args:
            agent_name: Name of the agent
            profile: Custom profile dictionary
        """
        self.custom_profiles[agent_name] = profile

    def apply_strategy(self, agent_name: str, strategy_name: str):
        """Apply a pre-defined context strategy to an agent.

        Args:
            agent_name: Name of the agent
            strategy_name: Name of the strategy
        """
        if strategy_name not in CONTEXT_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        strategy = CONTEXT_STRATEGIES[strategy_name]
        base_profile = self.get_profile(agent_name).copy()

        # Update profile with strategy
        base_profile.update(strategy)
        self.custom_profiles[agent_name] = base_profile

    def build_context(
        self,
        agent_name: str,
        user_query: str,
        conversation: ConversationManager,
        max_tokens: int = 4000,
        adjustments: dict[str, Any] | None = None,
    ) -> str:
        """Build agent-specific context.

        Args:
            agent_name: Name of agent receiving context
            user_query: User's current query
            conversation: Conversation manager
            max_tokens: Maximum tokens for context
            adjustments: Optional runtime adjustments

        Returns:
            Formatted context string
        """
        profile = self.get_profile(agent_name).copy()

        # Apply conversation-specific adjustments
        conv_adjustments = conversation.get_agent_context_adjustments(agent_name)
        if conv_adjustments:
            self._apply_adjustments(profile, conv_adjustments)

        # Apply runtime adjustments
        if adjustments:
            self._apply_adjustments(profile, adjustments)

        # Allocate tokens based on profile
        tokens = self._allocate_tokens(profile, max_tokens)

        # Build layered context
        context_parts = []

        # Layer 1: AGENTS.md project context
        if tokens["agents_md"] > 0:
            agents_context = self._get_project_context(max_tokens=tokens["agents_md"])
            if agents_context:
                context_parts.append(("PROJECT CONTEXT", agents_context))

        # Layer 2: Skills (prioritize by agent profile)
        if tokens["skills"] > 0:
            skills_context = self._get_skills_context(
                query=user_query,
                priorities=profile.get("priority", []),
                max_tokens=tokens["skills"],
            )
            if skills_context:
                context_parts.append(("CAPABILITIES", skills_context))

        # Layer 3: Conversation history (agent-specific depth)
        if tokens["conversation"] > 0:
            conv_context = conversation.get_context_for_agent(
                agent_name=agent_name,
                max_turns=profile.get("history_depth", 5),
                max_tokens=tokens["conversation"],
                compress_threshold=profile.get("compress_threshold", 0.6),
            )
            if conv_context:
                context_parts.append(("CONVERSATION HISTORY", conv_context))

        # Layer 4: Shared context (filtered by relevance)
        if tokens["shared_context"] > 0:
            shared = self.shared_context.get_compressed_context(
                agent=agent_name, max_tokens=tokens["shared_context"]
            )
            if shared:
                context_parts.append(("SHARED CONTEXT", shared))

        return self._format_context(context_parts)

    def _allocate_tokens(
        self, profile: dict[str, Any], max_tokens: int
    ) -> dict[str, int]:
        """Allocate tokens based on profile.

        Args:
            profile: Agent profile
            max_tokens: Maximum tokens available

        Returns:
            Dictionary with token allocation per layer
        """
        allocation = profile.get(
            "token_allocation",
            {
                "agents_md": 0.25,
                "skills": 0.25,
                "conversation": 0.25,
                "shared_context": 0.25,
            },
        )

        return {
            "agents_md": int(max_tokens * allocation.get("agents_md", 0.25)),
            "skills": int(max_tokens * allocation.get("skills", 0.25)),
            "conversation": int(max_tokens * allocation.get("conversation", 0.25)),
            "shared_context": int(max_tokens * allocation.get("shared_context", 0.25)),
        }

    def _get_project_context(self, max_tokens: int) -> str:
        """Get project context from AGENTS.md.

        Args:
            max_tokens: Maximum tokens for project context

        Returns:
            Formatted project context
        """
        if not self.agents_md.config:
            return ""

        prompt = self.agents_md.to_system_prompt()

        # Truncate if over token limit
        max_chars = max_tokens * 4  # Rough: 4 chars per token
        if len(prompt) > max_chars:
            prompt = prompt[:max_chars] + "..."

        return prompt

    def _get_skills_context(
        self, query: str, priorities: list[str], max_tokens: int
    ) -> str:
        """Get skills context prioritized by agent needs.

        Args:
            query: User query
            priorities: Priority keywords for skill selection
            max_tokens: Maximum tokens for skills

        Returns:
            Formatted skills context
        """
        # Discover skills
        skill_adapters = AgentSkillAdapter.discover_skills(self.project_root)

        matching_adapter = None

        # Find matching skill by trigger
        query_lower = query.lower()
        for adapter in skill_adapters:
            if adapter.parsed and hasattr(adapter.parsed, "triggers"):
                for trigger in adapter.parsed.triggers:
                    if trigger.lower() in query_lower or query_lower in trigger.lower():
                        matching_adapter = adapter
                        break
            if matching_adapter:
                break

        if not matching_adapter:
            # Try to find skill matching priorities
            for adapter in skill_adapters:
                if adapter.parsed:
                    description = adapter.parsed.description.lower()
                    if any(p.lower() in description for p in priorities):
                        matching_adapter = adapter
                        break

        if not matching_adapter:
            return ""

        skill_prompt = matching_adapter.to_system_prompt()

        # Truncate if over token limit
        max_chars = max_tokens * 4
        if len(skill_prompt) > max_chars:
            skill_prompt = skill_prompt[:max_chars] + "..."

        return skill_prompt

    def _format_context(self, context_parts: list[tuple[str, str]]) -> str:
        """Format context parts into final context string.

        Args:
            context_parts: List of (section_name, content) tuples

        Returns:
            Formatted context string
        """
        if not context_parts:
            return ""

        sections = []
        for section_name, content in context_parts:
            sections.append(f"# {section_name}")
            sections.append(content)
            sections.append("")  # Empty line between sections

        return "\n".join(sections)

    def _apply_adjustments(self, profile: dict[str, Any], adjustments: dict[str, Any]):
        """Apply adjustments to profile in-place.

        Args:
            profile: Profile to adjust
            adjustments: Adjustments to apply
        """
        # Handle token allocation adjustments
        if "token_allocation" in adjustments:
            if "token_allocation" not in profile:
                profile["token_allocation"] = {}
            profile["token_allocation"].update(adjustments["token_allocation"])

        # Handle other direct updates
        for key, value in adjustments.items():
            if key != "token_allocation":
                profile[key] = value

    def get_profile_summary(self, agent_name: str) -> dict[str, Any]:
        """Get summary of agent's context profile.

        Args:
            agent_name: Name of agent

        Returns:
            Profile summary dictionary
        """
        profile = self.get_profile(agent_name)

        return {
            "agent": agent_name,
            "token_allocation": profile.get("token_allocation", {}),
            "history_depth": profile.get("history_depth", 5),
            "compress_threshold": profile.get("compress_threshold", 0.6),
            "priorities": profile.get("priority", []),
            "is_custom": agent_name in self.custom_profiles,
        }

    def reset_profile(self, agent_name: str):
        """Reset agent to default profile.

        Args:
            agent_name: Name of agent
        """
        if agent_name in self.custom_profiles:
            del self.custom_profiles[agent_name]
