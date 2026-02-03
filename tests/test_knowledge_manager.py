"""Comprehensive tests for KnowledgeManager (v0.3.0+).

This test suite covers:
- Convention storage and deduplication
- Decision recording
- Learning management with confidence decay
- Artifact tracking
- Knowledge search functionality
- Statistics
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from uacs.knowledge.manager import KnowledgeManager, KnowledgeManagerError
from uacs.knowledge.models import Convention, Decision, Learning, Artifact
from uacs.embeddings.manager import EmbeddingManager


@pytest.fixture
def manager():
    """Create temporary knowledge manager for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        embeddings_path = tmpdir / "embeddings"

        embedding_manager = EmbeddingManager(embeddings_path)
        knowledge_manager = KnowledgeManager(
            tmpdir, embedding_manager
        )

        yield knowledge_manager


class TestConventions:
    """Test convention management."""

    def test_add_convention(self, manager):
        """Test adding a convention."""
        conv = manager.add_convention(
            content="Always validate user input",
            topics=["security", "validation"],
            source_session="session_001",
            confidence=1.0
        )

        assert isinstance(conv, Convention)
        assert conv.content == "Always validate user input"
        assert "security" in conv.topics
        assert "validation" in conv.topics
        assert conv.source_session == "session_001"
        assert conv.confidence == 1.0

    def test_add_convention_with_topics(self, manager):
        """Test convention with multiple topics."""
        conv = manager.add_convention(
            content="Use Pydantic for data models",
            topics=["python", "validation", "data-modeling"]
        )

        assert len(conv.topics) == 3
        assert "python" in conv.topics
        assert "validation" in conv.topics
        assert "data-modeling" in conv.topics

    def test_add_convention_with_source_session(self, manager):
        """Test convention with source session."""
        conv = manager.add_convention(
            content="Convention text",
            topics=["test"],
            source_session="session_123"
        )

        assert conv.source_session == "session_123"

    def test_add_convention_with_confidence(self, manager):
        """Test convention with custom confidence."""
        conv = manager.add_convention(
            content="Experimental pattern",
            topics=["experimental"],
            confidence=0.7
        )

        assert conv.confidence == 0.7

    def test_add_convention_creates_embedding(self, manager):
        """Test that convention creates embedding."""
        initial_count = manager.embeddings.get_stats()["total_vectors"]

        manager.add_convention(
            content="Test convention",
            topics=["test"]
        )

        final_count = manager.embeddings.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_convention_deduplication(self, manager):
        """Test semantic deduplication of conventions."""
        # Add first convention
        conv1 = manager.add_convention(
            content="Always use JWT for authentication",
            topics=["security"],
            confidence=0.8
        )
        original_confidence = conv1.confidence  # Store original before it's updated

        # Try to add very similar convention
        conv2 = manager.add_convention(
            content="Always use JWT for authentication",  # Exact duplicate
            topics=["security"],
            confidence=0.9
        )

        # Should return the same convention with increased confidence
        # (deduplication logic increases confidence by 0.1)
        assert conv2.confidence > original_confidence
        assert conv2.confidence == 0.9  # 0.8 + 0.1 = 0.9
        # Check they're the same object
        assert conv1 is conv2

    def test_add_convention_empty_content_raises_error(self, manager):
        """Test that empty content raises error."""
        with pytest.raises(KnowledgeManagerError):
            manager.add_convention(content="", topics=["test"])


class TestDecisions:
    """Test decision management."""

    def test_add_decision(self, manager):
        """Test adding a decision."""
        decision = manager.add_decision(
            question="How should we handle authentication?",
            decision="Use JWT tokens",
            rationale="Stateless and scalable",
            decided_by="claude-sonnet-4",
            session_id="session_001",
            alternatives=["Session-based", "OAuth2"],
            topics=["security", "architecture"]
        )

        assert isinstance(decision, Decision)
        assert decision.question == "How should we handle authentication?"
        assert decision.decision == "Use JWT tokens"
        assert decision.rationale == "Stateless and scalable"
        assert decision.decided_by == "claude-sonnet-4"
        assert decision.session_id == "session_001"
        assert "Session-based" in decision.alternatives
        assert "OAuth2" in decision.alternatives
        assert "security" in decision.topics

    def test_add_decision_with_alternatives(self, manager):
        """Test decision with alternatives."""
        decision = manager.add_decision(
            question="Which database?",
            decision="PostgreSQL",
            rationale="Robust and scalable",
            decided_by="claude",
            session_id="s1",
            alternatives=["MySQL", "MongoDB", "SQLite"]
        )

        assert len(decision.alternatives) == 3
        assert "MySQL" in decision.alternatives
        assert "MongoDB" in decision.alternatives
        assert "SQLite" in decision.alternatives

    def test_add_decision_with_decided_by(self, manager):
        """Test recording who made the decision."""
        decision = manager.add_decision(
            question="Test question",
            decision="Test decision",
            rationale="Test rationale",
            decided_by="claude-opus-4",
            session_id="s1"
        )

        assert decision.decided_by == "claude-opus-4"

    def test_add_decision_with_topics(self, manager):
        """Test decision with topics."""
        decision = manager.add_decision(
            question="Q",
            decision="D",
            rationale="R",
            decided_by="claude",
            session_id="s1",
            topics=["performance", "optimization"]
        )

        assert len(decision.topics) == 2
        assert "performance" in decision.topics
        assert "optimization" in decision.topics

    def test_add_decision_creates_embedding(self, manager):
        """Test that decision creates embedding."""
        initial_count = manager.embeddings.get_stats()["total_vectors"]

        manager.add_decision(
            question="Test question",
            decision="Test decision",
            rationale="Test rationale",
            decided_by="claude",
            session_id="s1"
        )

        final_count = manager.embeddings.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_decision_missing_required_fields_raises_error(self, manager):
        """Test that missing required fields raises error."""
        with pytest.raises(KnowledgeManagerError):
            manager.add_decision(
                question="",  # Empty question
                decision="Test",
                rationale="Test",
                decided_by="claude",
                session_id="s1"
            )


class TestLearnings:
    """Test learning management."""

    def test_add_learning(self, manager):
        """Test adding a learning."""
        learning = manager.add_learning(
            pattern="Always add rate limiting to auth endpoints",
            confidence=0.9,
            learned_from=["session_001", "session_002"],
            category="security_pattern",
            topics=["security", "best_practice"]
        )

        assert isinstance(learning, Learning)
        assert learning.pattern == "Always add rate limiting to auth endpoints"
        assert learning.confidence == 0.9
        assert "session_001" in learning.learned_from
        assert "session_002" in learning.learned_from
        assert learning.category == "security_pattern"

    def test_add_learning_with_category(self, manager):
        """Test learning with category."""
        learning = manager.add_learning(
            pattern="Test pattern",
            confidence=0.8,
            learned_from=["s1"],
            category="performance_optimization"
        )

        assert learning.category == "performance_optimization"

    def test_add_learning_with_confidence(self, manager):
        """Test learning with custom confidence."""
        learning = manager.add_learning(
            pattern="Experimental pattern",
            confidence=0.6,
            learned_from=["s1"],
            category="experimental"
        )

        assert learning.confidence == 0.6

    def test_add_learning_creates_embedding(self, manager):
        """Test that learning creates embedding."""
        initial_count = manager.embeddings.get_stats()["total_vectors"]

        manager.add_learning(
            pattern="Test learning",
            confidence=0.9,
            learned_from=["s1"],
            category="test"
        )

        final_count = manager.embeddings.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_learning_deduplication(self, manager):
        """Test semantic deduplication of learnings."""
        # Add first learning
        learning1 = manager.add_learning(
            pattern="Always validate input data",
            confidence=0.8,
            learned_from=["s1"],
            category="validation"
        )

        # Add very similar learning
        learning2 = manager.add_learning(
            pattern="Always validate input data",  # Same pattern
            confidence=0.7,
            learned_from=["s2"],
            category="validation"
        )

        # Should merge sessions and increase confidence
        assert len(learning2.learned_from) == 2
        assert "s1" in learning2.learned_from
        assert "s2" in learning2.learned_from

    def test_add_learning_empty_pattern_raises_error(self, manager):
        """Test that empty pattern raises error."""
        with pytest.raises(KnowledgeManagerError):
            manager.add_learning(
                pattern="",
                confidence=0.9,
                learned_from=["s1"],
                category="test"
            )

    def test_add_learning_no_sessions_raises_error(self, manager):
        """Test that no learned_from sessions raises error."""
        with pytest.raises(KnowledgeManagerError):
            manager.add_learning(
                pattern="Test pattern",
                confidence=0.9,
                learned_from=[],  # Empty list
                category="test"
            )


class TestArtifacts:
    """Test artifact management."""

    def test_add_artifact(self, manager):
        """Test adding an artifact."""
        artifact = manager.add_artifact(
            type="file",
            path="src/auth.py",
            description="Authentication implementation",
            created_in_session="session_001",
            topics=["auth", "security"]
        )

        assert isinstance(artifact, Artifact)
        assert artifact.type == "file"
        assert artifact.path == "src/auth.py"
        assert artifact.description == "Authentication implementation"
        assert artifact.created_in_session == "session_001"
        assert "auth" in artifact.topics
        assert "security" in artifact.topics

    def test_add_artifact_file_type(self, manager):
        """Test adding a file artifact."""
        artifact = manager.add_artifact(
            type="file",
            path="src/models.py",
            description="Data models",
            created_in_session="s1"
        )

        assert artifact.type == "file"

    def test_add_artifact_function_type(self, manager):
        """Test adding a function artifact."""
        artifact = manager.add_artifact(
            type="function",
            path="src/auth.py::authenticate_user",
            description="User authentication function",
            created_in_session="s1"
        )

        assert artifact.type == "function"
        assert "::authenticate_user" in artifact.path

    def test_add_artifact_class_type(self, manager):
        """Test adding a class artifact."""
        artifact = manager.add_artifact(
            type="class",
            path="src/models.py::UserModel",
            description="User data model class",
            created_in_session="s1"
        )

        assert artifact.type == "class"
        assert "::UserModel" in artifact.path

    def test_add_artifact_creates_embedding(self, manager):
        """Test that artifact creates embedding."""
        initial_count = manager.embeddings.get_stats()["total_vectors"]

        manager.add_artifact(
            type="file",
            path="test.py",
            description="Test file",
            created_in_session="s1"
        )

        final_count = manager.embeddings.get_stats()["total_vectors"]
        assert final_count == initial_count + 1

    def test_add_artifact_missing_required_fields_raises_error(self, manager):
        """Test that missing required fields raises error."""
        with pytest.raises(KnowledgeManagerError):
            manager.add_artifact(
                type="",  # Empty type
                path="test.py",
                description="Test",
                created_in_session="s1"
            )


class TestKnowledgeSearch:
    """Test search functionality."""

    def test_search_conventions(self, manager):
        """Test searching conventions."""
        manager.add_convention("Use JWT for auth", topics=["security"])
        manager.add_convention("Validate all input", topics=["security"])

        results = manager.search("JWT authentication", limit=10)

        assert len(results) >= 1
        # Check that results contain conventions
        conv_results = [r for r in results if r.type == "convention"]
        assert len(conv_results) >= 1

    def test_search_decisions(self, manager):
        """Test searching decisions."""
        manager.add_decision(
            "Which auth method?",
            "JWT tokens",
            "Stateless",
            "claude",
            "s1"
        )

        results = manager.search("JWT authentication", limit=10)

        assert len(results) >= 1
        # Check that results contain decisions
        dec_results = [r for r in results if r.type == "decision"]
        assert len(dec_results) >= 1

    def test_search_learnings(self, manager):
        """Test searching learnings."""
        manager.add_learning(
            "Always add rate limiting",
            0.9,
            ["s1"],
            "security"
        )

        results = manager.search("rate limiting security", limit=10)

        assert len(results) >= 1
        # Check that results contain learnings
        learn_results = [r for r in results if r.type == "learning"]
        assert len(learn_results) >= 1

    def test_search_artifacts(self, manager):
        """Test searching artifacts."""
        manager.add_artifact(
            "file",
            "src/auth.py",
            "JWT authentication implementation",
            "s1"
        )

        results = manager.search("JWT authentication", limit=10)

        assert len(results) >= 1
        # Check that results contain artifacts
        art_results = [r for r in results if r.type == "artifact"]
        assert len(art_results) >= 1

    def test_search_by_type_filter(self, manager):
        """Test filtering search by type."""
        manager.add_convention("Convention about auth", topics=["security"])
        manager.add_decision("Q", "Use auth", "R", "claude", "s1")

        # Search only conventions
        results = manager.search("auth", types=["convention"], limit=10)

        # All results should be conventions
        for result in results:
            assert result.type == "convention"

    def test_search_min_confidence(self, manager):
        """Test filtering by minimum confidence."""
        manager.add_convention("High confidence", topics=["test"], confidence=0.95)
        manager.add_convention("Low confidence", topics=["test"], confidence=0.5)

        # Search with high confidence threshold
        results = manager.search("test", min_confidence=0.8, limit=10)

        # Only high confidence items should be returned
        for result in results:
            if result.type == "convention" or result.type == "learning":
                if result.metadata:
                    confidence = result.metadata.get("confidence", 0)
                    assert confidence >= 0.8


class TestStatistics:
    """Test knowledge statistics."""

    def test_get_stats(self, manager):
        """Test getting knowledge statistics."""
        manager.add_convention("Conv", topics=["test"])
        manager.add_decision("Q", "D", "R", "claude", "s1")
        manager.add_learning("L", 0.9, ["s1"], "test")
        manager.add_artifact("file", "test.py", "Test", "s1")

        stats = manager.get_stats()

        assert stats["conventions"] == 1
        assert stats["decisions"] == 1
        assert stats["learnings"] == 1
        assert stats["artifacts"] == 1
        assert stats["total_items"] == 4


class TestPersistence:
    """Test data persistence."""

    def test_knowledge_persists_across_instances(self):
        """Test that knowledge is saved and loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            embeddings_path = tmpdir / "embeddings"

            embedding_manager = EmbeddingManager(embeddings_path)

            # First instance: add data
            manager1 = KnowledgeManager(tmpdir, embedding_manager)
            manager1.add_convention("Test convention", topics=["test"])
            manager1.add_decision("Q", "D", "R", "claude", "s1")

            # Second instance: should load existing data
            manager2 = KnowledgeManager(tmpdir, embedding_manager)
            stats = manager2.get_stats()

            assert stats["conventions"] == 1
            assert stats["decisions"] == 1
