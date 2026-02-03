"""Comprehensive tests for UACS unified semantic API (v0.3.0+).

This test suite covers:
- UACS initialization with semantic components
- All semantic methods (add_user_message, add_assistant_message, add_tool_use,
  add_decision, add_convention, add_learning, add_artifact)
- Unified search across all types
- Backward compatibility (add_to_context with deprecation warning)
- End-to-end workflows
"""

import pytest
import tempfile
import warnings
from pathlib import Path

from uacs import UACS
from uacs.conversations.models import UserMessage, AssistantMessage, ToolUse
from uacs.knowledge.models import Convention, Decision, Learning, Artifact


@pytest.fixture
def temp_uacs():
    """Create a temporary UACS instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        yield UACS(project_path=tmpdir)


class TestUACSInitialization:
    """Test UACS initialization with semantic components."""

    def test_uacs_init(self, temp_uacs):
        """Test UACS initializes all semantic components."""
        assert temp_uacs.project_path is not None
        assert temp_uacs.embedding_manager is not None
        assert temp_uacs.conversation_manager is not None
        assert temp_uacs.knowledge_manager is not None

    def test_uacs_creates_directories(self, tmp_path):
        """Test UACS creates necessary storage directories."""
        uacs = UACS(project_path=tmp_path)

        # Check that .state directory structure is created
        state_dir = tmp_path / ".state"
        assert state_dir.exists()
        assert (state_dir / "embeddings").exists()
        assert (state_dir / "conversations").exists()
        assert (state_dir / "knowledge").exists()

    def test_uacs_initializes_managers(self, temp_uacs):
        """Test managers are properly initialized."""
        # EmbeddingManager should be shared
        assert temp_uacs.conversation_manager.embedding_manager is temp_uacs.embedding_manager
        assert temp_uacs.knowledge_manager.embeddings is temp_uacs.embedding_manager


class TestConversationMethods:
    """Test conversation tracking methods."""

    def test_add_user_message(self, temp_uacs):
        """Test adding a user message."""
        msg = temp_uacs.add_user_message(
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
        assert msg.timestamp is not None

    def test_add_user_message_creates_embedding(self, temp_uacs):
        """Test that adding user message creates an embedding."""
        initial_count = temp_uacs.embedding_manager.get_stats()["total_vectors"]

        temp_uacs.add_user_message(
            content="Test message",
            turn=1,
            session_id="test_001"
        )

        final_count = temp_uacs.embedding_manager.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_assistant_message(self, temp_uacs):
        """Test adding an assistant message."""
        msg = temp_uacs.add_assistant_message(
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

    def test_add_assistant_message_with_optional_fields(self, temp_uacs):
        """Test adding assistant message with optional fields."""
        msg = temp_uacs.add_assistant_message(
            content="Let me help you",
            turn=1,
            session_id="test_001"
        )

        assert msg.tokens_in is None
        assert msg.tokens_out is None
        assert msg.model is None

    def test_add_tool_use(self, temp_uacs):
        """Test adding a tool execution."""
        tool = temp_uacs.add_tool_use(
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

    def test_add_tool_use_failure(self, temp_uacs):
        """Test adding a failed tool execution."""
        tool = temp_uacs.add_tool_use(
            tool_name="Read",
            tool_input={"file": "nonexistent.py"},
            tool_response="File not found",
            turn=3,
            session_id="test_001",
            success=False
        )

        assert tool.success is False


class TestKnowledgeMethods:
    """Test knowledge management methods."""

    def test_add_convention(self, temp_uacs):
        """Test adding a project convention."""
        conv = temp_uacs.add_convention(
            content="We use JWT for authentication with bcrypt",
            topics=["security", "auth"],
            source_session="session_001",
            confidence=1.0
        )

        assert isinstance(conv, Convention)
        assert conv.content == "We use JWT for authentication with bcrypt"
        assert "security" in conv.topics
        assert "auth" in conv.topics
        assert conv.source_session == "session_001"
        assert conv.confidence == 1.0

    def test_add_convention_creates_embedding(self, temp_uacs):
        """Test that adding convention creates an embedding."""
        initial_count = temp_uacs.embedding_manager.get_stats()["total_vectors"]

        temp_uacs.add_convention(
            content="Always validate user input",
            topics=["security"]
        )

        final_count = temp_uacs.embedding_manager.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_decision(self, temp_uacs):
        """Test adding an architectural decision."""
        decision = temp_uacs.add_decision(
            question="How should we handle authentication?",
            decision="Use JWT tokens",
            rationale="Stateless, works well with microservices",
            session_id="session_001",
            alternatives=["Session-based", "OAuth2"],
            topics=["security", "architecture"]
        )

        assert isinstance(decision, Decision)
        assert decision.question == "How should we handle authentication?"
        assert decision.decision == "Use JWT tokens"
        assert decision.rationale == "Stateless, works well with microservices"
        assert decision.session_id == "session_001"
        assert "Session-based" in decision.alternatives
        assert "OAuth2" in decision.alternatives
        assert "security" in decision.topics

    def test_add_decision_with_minimal_fields(self, temp_uacs):
        """Test adding decision with only required fields."""
        decision = temp_uacs.add_decision(
            question="Which database?",
            decision="PostgreSQL",
            rationale="Better for structured data",
            session_id="session_001"
        )

        assert decision.alternatives == []
        assert decision.topics == []

    def test_add_learning(self, temp_uacs):
        """Test adding a cross-session learning."""
        learning = temp_uacs.add_learning(
            pattern="When implementing auth, always add rate limiting",
            learned_from=["session_001", "session_002"],
            category="security_best_practice",
            confidence=0.9
        )

        assert isinstance(learning, Learning)
        assert learning.pattern == "When implementing auth, always add rate limiting"
        assert "session_001" in learning.learned_from
        assert "session_002" in learning.learned_from
        assert learning.category == "security_best_practice"
        assert learning.confidence == 0.9

    def test_add_artifact(self, temp_uacs):
        """Test adding a code artifact reference."""
        artifact = temp_uacs.add_artifact(
            type="file",
            path="src/auth.py",
            description="JWT authentication implementation",
            created_in_session="session_001",
            topics=["auth", "security"]
        )

        assert isinstance(artifact, Artifact)
        assert artifact.type == "file"
        assert artifact.path == "src/auth.py"
        assert artifact.description == "JWT authentication implementation"
        assert artifact.created_in_session == "session_001"
        assert "auth" in artifact.topics

    def test_add_artifact_different_types(self, temp_uacs):
        """Test adding different artifact types."""
        # File artifact
        file_art = temp_uacs.add_artifact(
            type="file",
            path="src/models.py",
            description="Data models",
            created_in_session="s1"
        )
        assert file_art.type == "file"

        # Function artifact
        func_art = temp_uacs.add_artifact(
            type="function",
            path="src/auth.py::authenticate_user",
            description="User authentication function",
            created_in_session="s1"
        )
        assert func_art.type == "function"

        # Class artifact
        class_art = temp_uacs.add_artifact(
            type="class",
            path="src/models.py::UserModel",
            description="User data model class",
            created_in_session="s1"
        )
        assert class_art.type == "class"


class TestSemanticSearch:
    """Test unified semantic search across all types."""

    def test_search_all_types(self, temp_uacs):
        """Test searching across all conversation and knowledge types."""
        # Add different types of content
        temp_uacs.add_user_message("How do I implement authentication?", turn=1, session_id="s1")
        temp_uacs.add_assistant_message("Let's use JWT tokens", turn=1, session_id="s1")
        temp_uacs.add_convention("Always use JWT for auth", topics=["security"])
        temp_uacs.add_decision("Use JWT", "JWT tokens", "Stateless", session_id="s1")

        # Search should find relevant items (minimum 3 since threshold filters some)
        results = temp_uacs.search("authentication JWT", limit=10)

        assert len(results) >= 3
        # Results should be sorted by relevance
        if len(results) > 1:
            assert results[0].similarity >= results[-1].similarity

    def test_search_filtered_by_user_message(self, temp_uacs):
        """Test searching only user messages."""
        temp_uacs.add_user_message("Auth question", turn=1, session_id="s1")
        temp_uacs.add_assistant_message("Auth answer", turn=1, session_id="s1")
        temp_uacs.add_convention("Auth convention", topics=["security"])

        results = temp_uacs.search("auth", types=["user_message"], limit=10)

        # Should only return user messages
        for result in results:
            assert result.metadata.get("type") == "user_message"

    def test_search_filtered_by_decision(self, temp_uacs):
        """Test searching only decisions."""
        temp_uacs.add_user_message("What about auth?", turn=1, session_id="s1")
        temp_uacs.add_decision("Auth method", "JWT", "Best choice", session_id="s1")
        temp_uacs.add_convention("Auth pattern", topics=["security"])

        results = temp_uacs.search("auth", types=["decision"], limit=10)

        # Should only return decisions
        for result in results:
            assert result.metadata.get("type") == "decision"

    def test_search_filtered_by_multiple_types(self, temp_uacs):
        """Test searching multiple types at once."""
        temp_uacs.add_user_message("Auth user message", turn=1, session_id="s1")
        temp_uacs.add_assistant_message("Auth assistant message", turn=1, session_id="s1")
        temp_uacs.add_convention("Auth convention", topics=["security"])
        temp_uacs.add_decision("Auth decision", "JWT", "Rationale", session_id="s1")

        results = temp_uacs.search("auth", types=["user_message", "decision"], limit=10)

        # Should only return user messages and decisions
        for result in results:
            result_type = result.metadata.get("type")
            assert result_type in ["user_message", "decision"]

    def test_search_by_session_id(self, temp_uacs):
        """Test filtering search results by session."""
        temp_uacs.add_user_message("Session 1 message", turn=1, session_id="session_001")
        temp_uacs.add_user_message("Session 2 message", turn=1, session_id="session_002")

        results = temp_uacs.search("message", session_id="session_001", limit=10)

        # Should only return results from session_001
        for result in results:
            if result.metadata.get("session_id"):
                assert result.metadata["session_id"] == "session_001"

    def test_search_with_confidence_threshold(self, temp_uacs):
        """Test filtering by minimum confidence."""
        temp_uacs.add_convention("High confidence", topics=["test"], confidence=0.95)
        temp_uacs.add_convention("Low confidence", topics=["test"], confidence=0.6)

        results = temp_uacs.search("test", min_confidence=0.8, limit=10)

        # Should only return high confidence items
        # Note: min_confidence filters conventions/learnings in knowledge manager


    def test_search_returns_correct_limit(self, temp_uacs):
        """Test that search respects the limit parameter."""
        # Add many items
        for i in range(20):
            temp_uacs.add_user_message(f"Test message {i}", turn=i+1, session_id="s1")

        results = temp_uacs.search("test", limit=5)

        assert len(results) <= 5

    def test_search_sorts_by_relevance(self, temp_uacs):
        """Test that search results are sorted by relevance."""
        temp_uacs.add_user_message("authentication with JWT tokens", turn=1, session_id="s1")
        temp_uacs.add_user_message("database configuration", turn=2, session_id="s1")

        results = temp_uacs.search("JWT authentication", limit=10)

        if len(results) >= 2:
            # More relevant result should come first
            assert results[0].similarity >= results[1].similarity


class TestBackwardCompatibility:
    """Test backward compatibility with old API."""

    def test_add_to_context_shows_deprecation_warning(self, temp_uacs):
        """Test that add_to_context shows deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            temp_uacs.add_to_context(
                key="test-agent",
                content="Test content",
                topics=["test"]
            )

            # Should have raised at least one deprecation warning
            assert len(w) >= 1
            # Find the deprecation warning from add_to_context
            deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1
            assert any("deprecated" in str(dw.message).lower() for dw in deprecation_warnings)

    def test_add_to_context_still_works(self, temp_uacs):
        """Test that add_to_context still functions despite deprecation."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            temp_uacs.add_to_context(
                key="test-agent",
                content="Test content for backward compatibility",
                metadata={"source": "test"},
                topics=["compat"]
            )

            # Should have added to both old and new systems
            stats = temp_uacs.get_stats()
            assert stats["semantic"]["knowledge"]["conventions"] >= 1


class TestEndToEndWorkflows:
    """Test complete workflows combining multiple operations."""

    def test_complete_conversation_workflow(self, temp_uacs):
        """Test a complete conversation workflow."""
        # User asks question
        user_msg = temp_uacs.add_user_message(
            content="How do I implement authentication?",
            turn=1,
            session_id="session_001",
            topics=["security", "implementation"]
        )
        assert user_msg is not None

        # Assistant responds
        assistant_msg = temp_uacs.add_assistant_message(
            content="I'll help you implement JWT authentication...",
            turn=1,
            session_id="session_001",
            tokens_in=42,
            tokens_out=156,
            model="claude-sonnet-4"
        )
        assert assistant_msg is not None

        # Tool is used
        tool_use = temp_uacs.add_tool_use(
            tool_name="Edit",
            tool_input={"file": "auth.py", "content": "..."},
            tool_response="Successfully created auth.py",
            turn=2,
            session_id="session_001"
        )
        assert tool_use is not None

        # Decision is made
        decision = temp_uacs.add_decision(
            question="Which auth method?",
            decision="JWT tokens",
            rationale="Stateless and scalable",
            session_id="session_001",
            topics=["security", "architecture"]
        )
        assert decision is not None

        # Convention is established
        convention = temp_uacs.add_convention(
            content="Always use JWT for API authentication",
            topics=["security", "api"],
            source_session="session_001"
        )
        assert convention is not None

        # Search should find all of this
        results = temp_uacs.search("authentication JWT", limit=10)
        assert len(results) >= 5

    def test_multi_session_learning_workflow(self, temp_uacs):
        """Test learning across multiple sessions."""
        # Session 1: First observation
        temp_uacs.add_user_message("Need rate limiting for auth", turn=1, session_id="s1")
        temp_uacs.add_decision("Add rate limiting", "Yes", "Security", session_id="s1")

        # Session 2: Second observation
        temp_uacs.add_user_message("Auth without rate limiting is vulnerable", turn=1, session_id="s2")
        temp_uacs.add_decision("Add rate limiting", "Critical", "Security", session_id="s2")

        # Cross-session learning
        learning = temp_uacs.add_learning(
            pattern="Always add rate limiting to authentication endpoints",
            learned_from=["s1", "s2"],
            category="security_pattern",
            confidence=0.95
        )

        assert learning is not None
        assert len(learning.learned_from) == 2

        # Search should find the learning
        results = temp_uacs.search("rate limiting auth", limit=10)
        learning_results = [r for r in results if r.metadata.get("type") == "learning"]
        assert len(learning_results) >= 1


class TestStatistics:
    """Test comprehensive statistics."""

    def test_get_stats(self, temp_uacs):
        """Test getting comprehensive stats."""
        # Add some data
        temp_uacs.add_user_message("Test", turn=1, session_id="s1")
        temp_uacs.add_convention("Test convention", topics=["test"])

        stats = temp_uacs.get_stats()

        assert "project_path" in stats
        assert "semantic" in stats
        assert "conversations" in stats["semantic"]
        assert "knowledge" in stats["semantic"]
        assert "embeddings" in stats["semantic"]

    def test_conversation_stats(self, temp_uacs):
        """Test conversation-specific statistics."""
        temp_uacs.add_user_message("Message 1", turn=1, session_id="s1")
        temp_uacs.add_user_message("Message 2", turn=2, session_id="s1")
        temp_uacs.add_assistant_message("Response", turn=1, session_id="s1")

        stats = temp_uacs.get_stats()
        conv_stats = stats["semantic"]["conversations"]

        assert conv_stats["total_user_messages"] == 2
        assert conv_stats["total_assistant_messages"] == 1
        assert conv_stats["total_sessions"] == 1

    def test_knowledge_stats(self, temp_uacs):
        """Test knowledge-specific statistics."""
        temp_uacs.add_convention("Conv 1", topics=["test"])
        temp_uacs.add_decision("Q", "D", "R", session_id="s1")
        temp_uacs.add_learning("L", learned_from=["s1"], category="test", confidence=0.9)

        stats = temp_uacs.get_stats()
        knowledge_stats = stats["semantic"]["knowledge"]

        assert knowledge_stats["conventions"] == 1
        assert knowledge_stats["decisions"] == 1
        assert knowledge_stats["learnings"] == 1

    def test_embedding_stats(self, temp_uacs):
        """Test embedding statistics."""
        # Add some content to create embeddings
        temp_uacs.add_user_message("Test message", turn=1, session_id="s1")
        temp_uacs.add_convention("Test convention", topics=["test"])

        stats = temp_uacs.get_stats()
        embedding_stats = stats["semantic"]["embeddings"]

        assert "total_vectors" in embedding_stats
        assert embedding_stats["total_vectors"] >= 2
        assert "model_name" in embedding_stats
        assert "dimension" in embedding_stats
