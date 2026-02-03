"""Comprehensive tests for ConversationManager (v0.3.0+).

This test suite covers:
- User message storage and retrieval
- Assistant message storage and retrieval
- Tool use tracking
- Conversation search functionality
- Session-based filtering
- Statistics and metadata
"""

import pytest
import tempfile
from pathlib import Path

from uacs.conversations.manager import ConversationManager, ConversationManagerError
from uacs.conversations.models import UserMessage, AssistantMessage, ToolUse
from uacs.embeddings.manager import EmbeddingManager


@pytest.fixture
def managers():
    """Create temporary managers for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        embeddings_path = tmpdir / "embeddings"
        conversations_path = tmpdir / "conversations"

        embedding_manager = EmbeddingManager(embeddings_path)
        conversation_manager = ConversationManager(
            conversations_path, embedding_manager
        )

        yield conversation_manager


class TestUserMessages:
    """Test user message operations."""

    def test_add_user_message(self, managers):
        """Test adding a user message."""
        msg = managers.add_user_message(
            content="Help me implement authentication",
            turn=1,
            session_id="test_001",
            topics=["security", "feature"]
        )

        assert isinstance(msg, UserMessage)
        assert msg.content == "Help me implement authentication"
        assert msg.turn == 1
        assert msg.session_id == "test_001"
        assert "security" in msg.topics
        assert "feature" in msg.topics

    def test_add_user_message_with_topics(self, managers):
        """Test adding user message with multiple topics."""
        msg = managers.add_user_message(
            content="Fix the bug in auth module",
            turn=1,
            session_id="test_001",
            topics=["bug", "security", "urgent"]
        )

        assert len(msg.topics) == 3
        assert "bug" in msg.topics
        assert "security" in msg.topics
        assert "urgent" in msg.topics

    def test_add_user_message_creates_embedding(self, managers):
        """Test that adding message creates embedding."""
        initial_count = managers.embedding_manager.get_stats()["total_vectors"]

        managers.add_user_message(
            content="Test message",
            turn=1,
            session_id="test_001"
        )

        final_count = managers.embedding_manager.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_user_message_without_topics(self, managers):
        """Test adding user message without topics."""
        msg = managers.add_user_message(
            content="Simple question",
            turn=1,
            session_id="test_001"
        )

        assert msg.topics == []


class TestAssistantMessages:
    """Test assistant message operations."""

    def test_add_assistant_message(self, managers):
        """Test adding an assistant message."""
        msg = managers.add_assistant_message(
            content="I'll help you implement JWT authentication",
            turn=1,
            session_id="test_001",
            tokens_in=42,
            tokens_out=156,
            model="claude-sonnet-4"
        )

        assert isinstance(msg, AssistantMessage)
        assert msg.content == "I'll help you implement JWT authentication"
        assert msg.turn == 1
        assert msg.session_id == "test_001"
        assert msg.tokens_in == 42
        assert msg.tokens_out == 156
        assert msg.model == "claude-sonnet-4"

    def test_add_assistant_message_with_tokens(self, managers):
        """Test tracking token usage."""
        msg = managers.add_assistant_message(
            content="Response",
            turn=1,
            session_id="test_001",
            tokens_in=100,
            tokens_out=200
        )

        assert msg.tokens_in == 100
        assert msg.tokens_out == 200

    def test_add_assistant_message_with_model(self, managers):
        """Test recording model information."""
        msg = managers.add_assistant_message(
            content="Response",
            turn=1,
            session_id="test_001",
            model="claude-opus-4"
        )

        assert msg.model == "claude-opus-4"

    def test_add_assistant_message_creates_embedding(self, managers):
        """Test that assistant message creates embedding."""
        initial_count = managers.embedding_manager.get_stats()["total_vectors"]

        managers.add_assistant_message(
            content="Test response",
            turn=1,
            session_id="test_001"
        )

        final_count = managers.embedding_manager.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_assistant_message_optional_fields(self, managers):
        """Test assistant message with optional fields."""
        msg = managers.add_assistant_message(
            content="Response without metadata",
            turn=1,
            session_id="test_001"
        )

        assert msg.tokens_in is None
        assert msg.tokens_out is None
        assert msg.model is None


class TestToolUses:
    """Test tool use tracking."""

    def test_add_tool_use(self, managers):
        """Test adding a tool execution."""
        tool = managers.add_tool_use(
            tool_name="Edit",
            tool_input={"file": "auth.py", "changes": "..."},
            tool_response="Successfully edited auth.py",
            turn=2,
            session_id="test_001",
            latency_ms=2300,
            success=True
        )

        assert isinstance(tool, ToolUse)
        assert tool.tool_name == "Edit"
        assert tool.tool_input["file"] == "auth.py"
        assert tool.tool_response == "Successfully edited auth.py"
        assert tool.turn == 2
        assert tool.session_id == "test_001"
        assert tool.latency_ms == 2300
        assert tool.success is True

    def test_add_tool_use_with_latency(self, managers):
        """Test recording tool latency."""
        tool = managers.add_tool_use(
            tool_name="Read",
            tool_input={"file": "config.yaml"},
            tool_response="...",
            turn=1,
            session_id="test_001",
            latency_ms=150
        )

        assert tool.latency_ms == 150

    def test_add_tool_use_with_success_false(self, managers):
        """Test recording failed tool execution."""
        tool = managers.add_tool_use(
            tool_name="Delete",
            tool_input={"file": "temp.txt"},
            tool_response="File not found",
            turn=1,
            session_id="test_001",
            success=False
        )

        assert tool.success is False

    def test_add_tool_use_creates_embedding(self, managers):
        """Test that tool use creates embedding."""
        initial_count = managers.embedding_manager.get_stats()["total_vectors"]

        managers.add_tool_use(
            tool_name="Test",
            tool_input={"param": "value"},
            tool_response="Result",
            turn=1,
            session_id="test_001"
        )

        final_count = managers.embedding_manager.get_stats()["total_vectors"]
        assert final_count == initial_count + 1


class TestConversationSearch:
    """Test search functionality."""

    def test_search_user_messages(self, managers):
        """Test searching user messages."""
        managers.add_user_message("Question about authentication", turn=1, session_id="s1")
        managers.add_user_message("How does JWT work?", turn=2, session_id="s1")

        results = managers.search("authentication JWT", k=10, threshold=0.6)

        assert len(results) >= 1
        # Check that results contain user messages
        user_msg_results = [r for r in results if r.metadata.get("type") == "user_message"]
        assert len(user_msg_results) >= 1

    def test_search_assistant_messages(self, managers):
        """Test searching assistant messages."""
        managers.add_assistant_message("JWT uses tokens for auth", turn=1, session_id="s1")
        managers.add_assistant_message("OAuth is another option", turn=2, session_id="s1")

        results = managers.search("JWT tokens authentication", k=10, threshold=0.6)

        assert len(results) >= 1
        # Check that results contain assistant messages
        asst_msg_results = [r for r in results if r.metadata.get("type") == "assistant_message"]
        assert len(asst_msg_results) >= 1

    def test_search_tool_uses(self, managers):
        """Test searching tool uses."""
        managers.add_tool_use(
            tool_name="Edit",
            tool_input={"file": "auth.py"},
            tool_response="Added JWT authentication",
            turn=1,
            session_id="s1"
        )

        results = managers.search("JWT authentication", k=10, threshold=0.6)

        assert len(results) >= 1
        # Check that results contain tool uses
        tool_results = [r for r in results if r.metadata.get("type") == "tool_use"]
        assert len(tool_results) >= 1

    def test_search_by_session_id(self, managers):
        """Test filtering search by session."""
        managers.add_user_message("Session 1 message", turn=1, session_id="session_1")
        managers.add_user_message("Session 2 message", turn=1, session_id="session_2")

        results = managers.search("message", session_id="session_1", k=10, threshold=0.6)

        # All results should be from session_1
        for result in results:
            assert result.metadata.get("session_id") == "session_1"

    def test_search_with_type_filter(self, managers):
        """Test filtering search by message type."""
        managers.add_user_message("User message about auth", turn=1, session_id="s1")
        managers.add_assistant_message("Assistant response about auth", turn=1, session_id="s1")

        # Search only user messages
        results = managers.search("auth", types=["user_message"], k=10, threshold=0.6)

        # All results should be user messages
        for result in results:
            assert result.metadata.get("type") == "user_message"

    def test_search_threshold(self, managers):
        """Test search similarity threshold."""
        managers.add_user_message("Authentication with JWT tokens", turn=1, session_id="s1")
        managers.add_user_message("Database configuration", turn=2, session_id="s1")

        # High threshold should return fewer results
        results_high = managers.search("JWT auth", k=10, threshold=0.9)
        results_low = managers.search("JWT auth", k=10, threshold=0.5)

        # Lower threshold should return more results
        assert len(results_low) >= len(results_high)


class TestSessionRetrieval:
    """Test retrieving session data."""

    def test_get_session_messages(self, managers):
        """Test retrieving all messages for a session."""
        # Add messages to session
        managers.add_user_message("Question", turn=1, session_id="session_abc")
        managers.add_assistant_message("Answer", turn=1, session_id="session_abc")
        managers.add_tool_use("Edit", {"file": "test.py"}, "Success", turn=2, session_id="session_abc")

        # Add message to different session
        managers.add_user_message("Other", turn=1, session_id="session_xyz")

        # Retrieve session messages
        session_data = managers.get_session_messages("session_abc")

        assert len(session_data["user_messages"]) == 1
        assert len(session_data["assistant_messages"]) == 1
        assert len(session_data["tool_uses"]) == 1

        # Verify content
        assert session_data["user_messages"][0].content == "Question"
        assert session_data["assistant_messages"][0].content == "Answer"
        assert session_data["tool_uses"][0].tool_name == "Edit"


class TestStatistics:
    """Test conversation statistics."""

    def test_get_stats(self, managers):
        """Test getting conversation statistics."""
        # Add various messages
        managers.add_user_message("Message 1", turn=1, session_id="s1")
        managers.add_user_message("Message 2", turn=2, session_id="s1")
        managers.add_assistant_message("Response", turn=1, session_id="s1")
        managers.add_tool_use("Edit", {}, "Success", turn=2, session_id="s1")

        stats = managers.get_stats()

        assert stats["total_user_messages"] == 2
        assert stats["total_assistant_messages"] == 1
        assert stats["total_tool_uses"] == 1
        assert stats["total_sessions"] == 1

    def test_stats_per_session(self, managers):
        """Test statistics with multiple sessions."""
        managers.add_user_message("M1", turn=1, session_id="s1")
        managers.add_user_message("M2", turn=1, session_id="s2")
        managers.add_assistant_message("R1", turn=1, session_id="s1")
        managers.add_assistant_message("R2", turn=1, session_id="s2")

        stats = managers.get_stats()

        assert stats["total_user_messages"] == 2
        assert stats["total_assistant_messages"] == 2
        assert stats["total_sessions"] == 2


class TestPersistence:
    """Test data persistence."""

    def test_data_persists_across_instances(self):
        """Test that data is saved and loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            embeddings_path = tmpdir / "embeddings"
            conversations_path = tmpdir / "conversations"

            embedding_manager = EmbeddingManager(embeddings_path)

            # First instance: add data
            manager1 = ConversationManager(conversations_path, embedding_manager)
            manager1.add_user_message("Test message", turn=1, session_id="s1")
            manager1.add_assistant_message("Test response", turn=1, session_id="s1")

            # Second instance: should load existing data
            manager2 = ConversationManager(conversations_path, embedding_manager)
            stats = manager2.get_stats()

            assert stats["total_user_messages"] == 1
            assert stats["total_assistant_messages"] == 1
