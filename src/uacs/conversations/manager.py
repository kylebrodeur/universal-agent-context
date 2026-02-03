"""Conversation manager with semantic search for UACS.

This module provides structured conversation tracking with semantic embeddings.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from uacs.conversations.models import AssistantMessage, ToolUse, UserMessage
from uacs.embeddings.manager import EmbeddingManager, SearchResult

logger = logging.getLogger(__name__)


class ConversationManagerError(Exception):
    """Raised when conversation management operations fail."""

    pass


class ConversationManager:
    """Manages conversations with semantic search.

    Stores user messages, assistant responses, and tool uses with semantic
    embeddings for natural language search across conversations.
    """

    def __init__(self, storage_path: Path, embedding_manager: EmbeddingManager):
        """Initialize the conversation manager.

        Args:
            storage_path: Path to conversation storage directory
            embedding_manager: EmbeddingManager for semantic operations
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.embedding_manager = embedding_manager

        # Storage files
        self.user_messages_file = self.storage_path / "user_messages.json"
        self.assistant_messages_file = self.storage_path / "assistant_messages.json"
        self.tool_uses_file = self.storage_path / "tool_uses.json"

        # In-memory caches
        self._user_messages: List[UserMessage] = []
        self._assistant_messages: List[AssistantMessage] = []
        self._tool_uses: List[ToolUse] = []

        # Load existing data
        self._load_data()

    def _load_data(self) -> None:
        """Load conversation data from storage."""
        try:
            if self.user_messages_file.exists():
                with open(self.user_messages_file) as f:
                    data = json.load(f)
                    self._user_messages = [UserMessage(**msg) for msg in data]

            if self.assistant_messages_file.exists():
                with open(self.assistant_messages_file) as f:
                    data = json.load(f)
                    self._assistant_messages = [
                        AssistantMessage(**msg) for msg in data
                    ]

            if self.tool_uses_file.exists():
                with open(self.tool_uses_file) as f:
                    data = json.load(f)
                    self._tool_uses = [ToolUse(**tool) for tool in data]

            logger.info(
                f"Loaded {len(self._user_messages)} user messages, "
                f"{len(self._assistant_messages)} assistant messages, "
                f"{len(self._tool_uses)} tool uses"
            )

        except Exception as e:
            logger.error(f"Failed to load conversation data: {e}")
            raise ConversationManagerError(f"Failed to load data: {e}") from e

    def _save_data(self) -> None:
        """Save conversation data to storage."""
        try:
            with open(self.user_messages_file, "w") as f:
                json.dump(
                    [msg.model_dump(mode="json") for msg in self._user_messages],
                    f,
                    indent=2,
                    default=str,
                )

            with open(self.assistant_messages_file, "w") as f:
                json.dump(
                    [msg.model_dump(mode="json") for msg in self._assistant_messages],
                    f,
                    indent=2,
                    default=str,
                )

            with open(self.tool_uses_file, "w") as f:
                json.dump(
                    [tool.model_dump(mode="json") for tool in self._tool_uses],
                    f,
                    indent=2,
                    default=str,
                )

            logger.debug("Saved conversation data")

        except Exception as e:
            logger.error(f"Failed to save conversation data: {e}")
            raise ConversationManagerError(f"Failed to save data: {e}") from e

    def add_user_message(
        self,
        content: str,
        turn: int,
        session_id: str,
        topics: Optional[List[str]] = None,
    ) -> UserMessage:
        """Add a user message to the conversation history.

        Args:
            content: User prompt text
            turn: Turn number (1-indexed)
            session_id: Session identifier
            topics: Optional topic tags

        Returns:
            Created UserMessage
        """
        try:
            message = UserMessage(
                content=content,
                turn=turn,
                session_id=session_id,
                topics=topics or [],
            )

            # Add to in-memory cache
            self._user_messages.append(message)

            # Index content for semantic search
            msg_id = f"user_{session_id}_{turn}"
            self.embedding_manager.add_to_index(
                id=msg_id,
                text=content,
                metadata={
                    "type": "user_message",
                    "session_id": session_id,
                    "turn": turn,
                    "topics": topics or [],
                },
            )

            # Save to disk
            self._save_data()

            logger.debug(f"Added user message: {session_id} turn {turn}")
            return message

        except Exception as e:
            raise ConversationManagerError(
                f"Failed to add user message: {e}"
            ) from e

    def add_assistant_message(
        self,
        content: str,
        turn: int,
        session_id: str,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        model: Optional[str] = None,
    ) -> AssistantMessage:
        """Add an assistant response to the conversation history.

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
        try:
            message = AssistantMessage(
                content=content,
                turn=turn,
                session_id=session_id,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                model=model,
            )

            # Add to in-memory cache
            self._assistant_messages.append(message)

            # Index content for semantic search
            msg_id = f"assistant_{session_id}_{turn}"
            self.embedding_manager.add_to_index(
                id=msg_id,
                text=content,
                metadata={
                    "type": "assistant_message",
                    "session_id": session_id,
                    "turn": turn,
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "model": model,
                },
            )

            # Save to disk
            self._save_data()

            logger.debug(f"Added assistant message: {session_id} turn {turn}")
            return message

        except Exception as e:
            raise ConversationManagerError(
                f"Failed to add assistant message: {e}"
            ) from e

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
        """Add a tool execution to the conversation history.

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
        try:
            tool_use = ToolUse(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_response=tool_response,
                turn=turn,
                session_id=session_id,
                latency_ms=latency_ms,
                success=success,
            )

            # Add to in-memory cache
            self._tool_uses.append(tool_use)

            # Index tool description for semantic search
            # Combine tool name, input summary, and response for searchability
            input_summary = json.dumps(tool_input, default=str)[:200]
            searchable_text = (
                f"{tool_name}: {input_summary} -> {tool_response or 'no response'}"
            )

            tool_id = f"tool_{session_id}_{turn}_{tool_name}"
            self.embedding_manager.add_to_index(
                id=tool_id,
                text=searchable_text,
                metadata={
                    "type": "tool_use",
                    "tool_name": tool_name,
                    "session_id": session_id,
                    "turn": turn,
                    "success": success,
                },
            )

            # Save to disk
            self._save_data()

            logger.debug(f"Added tool use: {tool_name} in {session_id} turn {turn}")
            return tool_use

        except Exception as e:
            raise ConversationManagerError(f"Failed to add tool use: {e}") from e

    def search(
        self,
        query: str,
        types: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        k: int = 10,
        threshold: float = 0.7,
    ) -> List[SearchResult]:
        """Search conversations with natural language.

        Args:
            query: Natural language search query
            types: Optional filter by message type (user_message, assistant_message, tool_use)
            session_id: Optional filter by session
            k: Maximum results to return
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of SearchResult objects sorted by relevance
        """
        try:
            # Search embeddings
            results = self.embedding_manager.search(query, k=k, threshold=threshold)

            # Filter by type if specified
            if types:
                results = [r for r in results if r.metadata.get("type") in types]

            # Filter by session if specified
            if session_id:
                results = [
                    r for r in results if r.metadata.get("session_id") == session_id
                ]

            return results

        except Exception as e:
            raise ConversationManagerError(f"Search failed: {e}") from e

    def get_session_messages(
        self, session_id: str
    ) -> Dict[str, List[UserMessage | AssistantMessage | ToolUse]]:
        """Get all messages for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with user_messages, assistant_messages, and tool_uses lists
        """
        return {
            "user_messages": [
                msg for msg in self._user_messages if msg.session_id == session_id
            ],
            "assistant_messages": [
                msg
                for msg in self._assistant_messages
                if msg.session_id == session_id
            ],
            "tool_uses": [
                tool for tool in self._tool_uses if tool.session_id == session_id
            ],
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics.

        Returns:
            Dictionary with stats about conversations
        """
        return {
            "total_user_messages": len(self._user_messages),
            "total_assistant_messages": len(self._assistant_messages),
            "total_tool_uses": len(self._tool_uses),
            "total_sessions": len(
                {
                    msg.session_id
                    for msg in self._user_messages + self._assistant_messages
                }
            ),
        }
