"""Universal Agent Context System - Main API

See docs/uacs/README.md for details.
"""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

from uacs.adapters.agent_skill_adapter import AgentSkillAdapter
from uacs.adapters.agents_md_adapter import AgentsMDAdapter
from uacs.context.shared_context import SharedContextManager
from uacs.context.unified_context import UnifiedContextAdapter
from uacs.conversations.manager import ConversationManager
from uacs.conversations.models import AssistantMessage, ToolUse, UserMessage
from uacs.embeddings.manager import EmbeddingManager, SearchResult
from uacs.knowledge.manager import KnowledgeManager
from uacs.knowledge.models import Artifact, Convention, Decision, Learning
from uacs.packages import PackageManager


class UACS:
    """Universal Agent Context System

    Provides unified context management across:
    - Packages (Local package management)
    - Adapters (Format translation)
    - Context (Shared memory + compression)
    - Project metadata (AGENTS.md)
    - Semantic conversations and knowledge (v0.3.0+)

    Example:
        >>> uacs = UACS(project_path=Path("."))
        >>> uacs.install_package("owner/repo")
        >>> context = uacs.build_context(query="...", agent="claude")

        # New in v0.3.0: Structured conversation tracking
        >>> uacs.add_user_message("Help with auth", turn=1, session_id="s1")
        >>> uacs.add_decision("Use JWT", rationale="Stateless", session_id="s1")
        >>> results = uacs.search("how did we implement authentication?")
    """

    def __init__(
        self,
        project_path: Path,
    ):
        """Initialize UACS.

        Args:
            project_path: Path to the project root
        """
        self.project_path = project_path

        # Initialize components
        self.packages = PackageManager(project_path)

        # Detect and load project format adapters
        agents_md_path = project_path / "AGENTS.md"

        # Modern Agent Skills support (.agent/skills/)
        self.agent_skills = AgentSkillAdapter.discover_skills(project_path)

        self.agents_md = (
            AgentsMDAdapter(agents_md_path) if agents_md_path.exists() else None
        )

        # Initialize shared context and unified adapter (v0.2.0)
        self.shared_context = SharedContextManager(project_path / ".state" / "context")
        self.unified_context = UnifiedContextAdapter(
            agents_md_path=agents_md_path if agents_md_path.exists() else None,
            context_storage=project_path / ".state" / "context",
        )

        # Initialize semantic components (v0.3.0+)
        # Shared embedding manager for all semantic operations
        embeddings_path = project_path / ".state" / "embeddings"
        self.embedding_manager = EmbeddingManager(embeddings_path)

        # Conversation tracking
        conversations_path = project_path / ".state" / "conversations"
        self.conversation_manager = ConversationManager(
            conversations_path, self.embedding_manager
        )

        # Knowledge management
        knowledge_path = project_path / ".state" / "knowledge"
        self.knowledge_manager = KnowledgeManager(
            knowledge_path, self.embedding_manager
        )

    def install_package(
        self,
        source: str,
        validate: bool = True,
        force: bool = False,
    ) -> Any:
        """Install a package from GitHub, Git URL, or local path.

        Args:
            source: Package source (owner/repo, git URL, or local path)
            validate: Whether to validate before installing
            force: Whether to overwrite existing package

        Returns:
            Installed package information
        """
        return self.packages.install(source, validate=validate, force=force)

    def list_packages(self) -> list[Any]:
        """List installed packages.

        Returns:
            List of installed packages
        """
        return self.packages.list_installed()

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
        """Add content to shared context (DEPRECATED in v0.3.0).

        DEPRECATED: Use structured methods instead:
        - add_user_message() for user prompts
        - add_assistant_message() for responses
        - add_tool_use() for tool executions
        - add_convention() for project patterns
        - add_decision() for architectural decisions

        Args:
            key: Context key (used as agent name)
            content: Content to store
            metadata: Optional metadata
            topics: Optional topics for semantic filtering

        Example (deprecated):
            uacs.add_to_context(
                "claude",
                "Reviewed auth.py, found SQL injection",
                topics=["code-review", "security"]
            )

        Example (preferred):
            uacs.add_convention(
                content="Always validate SQL inputs",
                topics=["code-review", "security"]
            )
        """
        # Show deprecation warning
        warnings.warn(
            "add_to_context() is deprecated in v0.3.0. Use structured methods like "
            "add_user_message(), add_convention(), add_decision() for better semantic search.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Maintain backward compatibility: add to both old and new systems
        # Old system (v0.2.0)
        self.shared_context.add_entry(
            content=content,
            agent=key,
            metadata=metadata,
            topics=topics,
        )

        # New system (v0.3.0): treat as a convention with lower confidence
        self.knowledge_manager.add_convention(
            content=content,
            topics=topics or [],
            confidence=0.5,  # Lower confidence for unstructured content
        )

    # ====== Semantic Conversation Methods (v0.3.0+) ======

    def add_user_message(
        self,
        content: str,
        turn: int,
        session_id: str,
        topics: Optional[List[str]] = None,
    ) -> UserMessage:
        """Add a user message to conversation history.

        Args:
            content: User prompt text
            turn: Turn number (1-indexed)
            session_id: Session identifier
            topics: Optional topic tags

        Returns:
            Created UserMessage

        Example:
            >>> uacs.add_user_message(
            ...     content="Help me implement JWT authentication",
            ...     turn=1,
            ...     session_id="session_001",
            ...     topics=["security", "auth"]
            ... )
        """
        return self.conversation_manager.add_user_message(
            content=content, turn=turn, session_id=session_id, topics=topics
        )

    def add_assistant_message(
        self,
        content: str,
        turn: int,
        session_id: str,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        model: Optional[str] = None,
    ) -> AssistantMessage:
        """Add an assistant response to conversation history.

        Args:
            content: Assistant response text
            turn: Turn number (1-indexed)
            session_id: Session identifier
            tokens_in: Optional input token count
            tokens_out: Optional output token count
            model: Optional model identifier

        Returns:
            Created AssistantMessage

        Example:
            >>> uacs.add_assistant_message(
            ...     content="I'll help you implement JWT...",
            ...     turn=1,
            ...     session_id="session_001",
            ...     tokens_in=42,
            ...     tokens_out=156,
            ...     model="claude-sonnet-4"
            ... )
        """
        return self.conversation_manager.add_assistant_message(
            content=content,
            turn=turn,
            session_id=session_id,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=model,
        )

    def add_tool_use(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_response: Optional[str],
        turn: int,
        session_id: str,
        latency_ms: Optional[int] = None,
        success: bool = True,
    ) -> ToolUse:
        """Add a tool execution to conversation history.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters
            tool_response: Tool response text
            turn: Turn number (1-indexed)
            session_id: Session identifier
            latency_ms: Optional execution time
            success: Whether execution succeeded

        Returns:
            Created ToolUse

        Example:
            >>> uacs.add_tool_use(
            ...     tool_name="Edit",
            ...     tool_input={"file": "auth.py", "changes": "..."},
            ...     tool_response="Successfully edited auth.py",
            ...     turn=2,
            ...     session_id="session_001",
            ...     latency_ms=2300
            ... )
        """
        return self.conversation_manager.add_tool_use(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_response=tool_response,
            turn=turn,
            session_id=session_id,
            latency_ms=latency_ms,
            success=success,
        )

    # ====== Semantic Knowledge Methods (v0.3.0+) ======

    def add_convention(
        self,
        content: str,
        topics: Optional[List[str]] = None,
        source_session: Optional[str] = None,
        confidence: float = 1.0,
    ) -> Convention:
        """Add a project convention or pattern.

        Args:
            content: Convention description
            topics: Optional topic tags
            source_session: Session where convention was established
            confidence: Confidence score (0.0-1.0)

        Returns:
            Created Convention

        Example:
            >>> uacs.add_convention(
            ...     content="We use JWT for authentication with bcrypt",
            ...     topics=["security", "auth"],
            ...     source_session="session_001"
            ... )
        """
        return self.knowledge_manager.add_convention(
            content=content,
            topics=topics or [],
            source_session=source_session,
            confidence=confidence,
        )

    def add_decision(
        self,
        question: str,
        decision: str,
        rationale: str,
        session_id: str,
        alternatives: Optional[List[str]] = None,
        decided_by: str = "claude-sonnet-4",
        topics: Optional[List[str]] = None,
    ) -> Decision:
        """Add an architectural decision.

        Args:
            question: The question or problem addressed
            decision: The decision made
            rationale: Reasoning behind the decision
            session_id: Session where decision was made
            alternatives: Optional alternative approaches considered
            decided_by: Who/what made the decision
            topics: Optional topic tags

        Returns:
            Created Decision

        Example:
            >>> uacs.add_decision(
            ...     question="How should we handle authentication?",
            ...     decision="Use JWT tokens",
            ...     rationale="Stateless, works well with microservices",
            ...     session_id="session_001",
            ...     alternatives=["Session-based", "OAuth2"]
            ... )
        """
        return self.knowledge_manager.add_decision(
            question=question,
            decision=decision,
            rationale=rationale,
            alternatives=alternatives or [],
            decided_by=decided_by,
            session_id=session_id,
            topics=topics or [],
        )

    def add_learning(
        self,
        pattern: str,
        learned_from: List[str],
        category: str = "general",
        confidence: float = 1.0,
    ) -> Learning:
        """Add a cross-session learning.

        Args:
            pattern: The learned pattern or insight
            learned_from: List of session IDs that contributed to this learning
            category: Category of learning
            confidence: Confidence score (0.0-1.0)

        Returns:
            Created Learning

        Example:
            >>> uacs.add_learning(
            ...     pattern="When implementing auth, always add rate limiting",
            ...     learned_from=["session_001", "session_002"],
            ...     category="security_best_practice"
            ... )
        """
        return self.knowledge_manager.add_learning(
            pattern=pattern,
            learned_from=learned_from,
            category=category,
            confidence=confidence,
        )

    def add_artifact(
        self,
        type: str,
        path: str,
        description: str,
        created_in_session: str,
        topics: Optional[List[str]] = None,
    ) -> Artifact:
        """Add a code artifact reference.

        Args:
            type: Artifact type (file, function, class, etc.)
            path: File path or identifier
            description: Artifact description
            created_in_session: Session where artifact was created
            topics: Optional topic tags

        Returns:
            Created Artifact

        Example:
            >>> uacs.add_artifact(
            ...     type="file",
            ...     path="src/auth.py",
            ...     description="JWT authentication implementation",
            ...     created_in_session="session_001",
            ...     topics=["auth", "security"]
            ... )
        """
        return self.knowledge_manager.add_artifact(
            type=type,
            path=path,
            description=description,
            created_in_session=created_in_session,
            topics=topics or [],
        )

    # ====== Semantic Search (v0.3.0+) ======

    def search(
        self,
        query: str,
        types: Optional[List[str]] = None,
        min_confidence: float = 0.7,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[SearchResult]:
        """Search across conversations and knowledge with natural language.

        Args:
            query: Natural language search query
            types: Optional filter by type (user_message, assistant_message,
                   tool_use, convention, decision, learning, artifact)
            min_confidence: Minimum confidence threshold (0.0-1.0)
            session_id: Optional filter by session
            limit: Maximum results to return

        Returns:
            List of SearchResult objects sorted by relevance

        Raises:
            ValueError: If types contains invalid type names

        Example:
            >>> results = uacs.search("how did we implement authentication?")
            >>> for result in results:
            ...     print(f"{result.type}: {result.text[:50]}...")
        """
        # Handle empty queries gracefully
        if not query or not query.strip():
            return []

        # Validate types
        valid_types = {
            "user_message", "assistant_message", "tool_use",
            "convention", "decision", "learning", "artifact"
        }
        if types:
            invalid_types = set(types) - valid_types
            if invalid_types:
                raise ValueError(
                    f"Invalid search types: {invalid_types}. "
                    f"Valid types: {valid_types}"
                )

        results = []

        # Define type categories
        conv_types_set = {"user_message", "assistant_message", "tool_use"}
        knowledge_types_set = {"convention", "decision", "learning", "artifact"}

        # Determine which managers to search based on types filter
        search_conversations = not types or bool(set(types) & conv_types_set)
        search_knowledge = not types or bool(set(types) & knowledge_types_set)

        # Search conversations
        if search_conversations:
            conv_filter = [t for t in (types or []) if t in conv_types_set] or None
            conv_results = self.conversation_manager.search(
                query=query,
                types=conv_filter,
                session_id=session_id,
                k=limit,
                threshold=min_confidence,
            )
            results.extend(conv_results)

        # Search knowledge
        if search_knowledge:
            knowledge_filter = [t for t in (types or []) if t in knowledge_types_set] or None
            knowledge_results = self.knowledge_manager.search(
                query=query,
                types=knowledge_filter,
                min_confidence=min_confidence,
                limit=limit,
            )
            results.extend(knowledge_results)

        # Sort all results by relevance and limit
        # Handle both SearchResult types (embeddings use 'similarity', knowledge uses 'relevance_score')
        results.sort(
            key=lambda r: getattr(r, 'similarity', None) or getattr(r, 'relevance_score', 0),
            reverse=True
        )
        return results[:limit]

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
        graph = self.shared_context.get_context_graph()
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
            "packages": {
                "installed_count": len(self.packages.list_installed()),
                "skills_dir": str(self.project_path / ".agent" / "skills"),
            },
            "context": token_stats,
            "capabilities": self.get_capabilities(),
            # Semantic components (v0.3.0+)
            "semantic": {
                "conversations": self.conversation_manager.get_stats(),
                "knowledge": self.knowledge_manager.get_stats(),
                "embeddings": self.embedding_manager.get_stats(),
            },
        }

        return stats


__all__ = ["UACS"]
