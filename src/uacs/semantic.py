"""Unified semantic UACS API (v0.3.0).

This module provides a unified interface for UACS with semantic capabilities,
combining conversations, knowledge, and embeddings into a single cohesive API.
"""

import logging
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

from uacs.conversations.manager import ConversationManager
from uacs.conversations.models import AssistantMessage, ToolUse, UserMessage
from uacs.embeddings.manager import EmbeddingManager, SearchResult
from uacs.knowledge.manager import KnowledgeManager
from uacs.knowledge.models import Artifact, Convention, Decision, Learning

logger = logging.getLogger(__name__)


class SemanticUACS:
    """Unified semantic UACS API.

    This class provides structured conversation and knowledge tracking with
    semantic search capabilities. It integrates:

    - ConversationManager: User/assistant messages and tool uses
    - KnowledgeManager: Conventions, decisions, learnings, artifacts
    - EmbeddingManager: Semantic search across all content

    Example:
        ```python
        from uacs.semantic import SemanticUACS

        uacs = SemanticUACS()  # Auto-initializes in .state/

        # Track conversation
        uacs.add_user_message(
            content="Help me implement auth",
            turn=1,
            session_id="session_123"
        )

        uacs.add_assistant_message(
            content="I'll help you with JWT...",
            turn=1,
            session_id="session_123"
        )

        # Capture knowledge
        uacs.add_decision(
            question="Which auth method?",
            decision="Use JWT tokens",
            rationale="Stateless, scales well",
            session_id="session_123"
        )

        # Search everything semantically
        results = uacs.search("how did we handle authentication?")
        ```
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize semantic UACS.

        Args:
            storage_path: Optional storage directory (defaults to .state/)
        """
        # Determine storage path
        if storage_path is None:
            storage_path = Path.cwd() / ".state"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing semantic UACS at {self.storage_path}")

        # Initialize embedding manager (shared across all components)
        embeddings_path = self.storage_path / "embeddings"
        self.embedding_manager = EmbeddingManager(embeddings_path)

        # Initialize managers
        conversations_path = self.storage_path / "conversations"
        self.conversation_manager = ConversationManager(
            conversations_path, self.embedding_manager
        )

        knowledge_path = self.storage_path / "knowledge"
        self.knowledge_manager = KnowledgeManager(
            knowledge_path, self.embedding_manager
        )

        logger.info("Semantic UACS initialized successfully")

    # ====== Conversation Methods ======

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

    # ====== Knowledge Methods ======

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
        """
        return self.knowledge_manager.add_artifact(
            type=type,
            path=path,
            description=description,
            created_in_session=created_in_session,
            topics=topics or [],
        )

    # ====== Search Methods ======

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
            min_confidence: Minimum confidence threshold
            session_id: Optional filter by session
            limit: Maximum results to return

        Returns:
            List of SearchResult objects sorted by relevance
        """
        results = []

        # Determine which managers to search based on types filter
        search_conversations = not types or any(
            t in ["user_message", "assistant_message", "tool_use"] for t in types
        )
        search_knowledge = not types or any(
            t in ["convention", "decision", "learning", "artifact"] for t in types
        )

        # Search conversations
        if search_conversations:
            conv_types = (
                [t for t in types if t in ["user_message", "assistant_message", "tool_use"]]
                if types
                else None
            )
            conv_results = self.conversation_manager.search(
                query=query,
                types=conv_types,
                session_id=session_id,
                k=limit,
                threshold=min_confidence,
            )
            results.extend(conv_results)

        # Search knowledge
        if search_knowledge:
            knowledge_types = (
                [t for t in types if t in ["convention", "decision", "learning", "artifact"]]
                if types
                else None
            )
            knowledge_results = self.knowledge_manager.search(
                query=query,
                types=knowledge_types,
                min_confidence=min_confidence,
                limit=limit,
            )
            results.extend(knowledge_results)

        # Sort all results by relevance and limit
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:limit]

    # ====== Statistics ======

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics.

        Returns:
            Dictionary with stats from all managers
        """
        return {
            "conversations": self.conversation_manager.get_stats(),
            "knowledge": self.knowledge_manager.get_stats(),
            "embeddings": self.embedding_manager.get_stats(),
        }

    # ====== Backward Compatibility (Deprecated) ======

    def add_to_context(
        self,
        key: str,
        content: str,
        topics: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add generic context (DEPRECATED).

        This method is deprecated. Use structured methods instead:
        - add_user_message() for user prompts
        - add_assistant_message() for responses
        - add_convention() for project patterns
        - add_decision() for architectural decisions

        Args:
            key: Context key (ignored in semantic API)
            content: Content to add
            topics: Optional topic tags
            metadata: Optional metadata
        """
        warnings.warn(
            "add_to_context() is deprecated. Use structured methods like "
            "add_user_message(), add_convention(), add_decision() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Fallback: treat as a convention with low confidence
        self.add_convention(
            content=content,
            topics=topics or [],
            confidence=0.5,  # Lower confidence for unstructured content
        )
