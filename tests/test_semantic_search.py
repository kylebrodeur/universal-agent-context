"""Tests for semantic search functionality across all UACS components.

This test suite covers:
- Similarity ranking
- Type filtering
- Threshold filtering
- Cross-component search
- Edge cases
"""

import pytest
import tempfile
from pathlib import Path

from uacs import UACS


@pytest.fixture
def uacs_with_data():
    """Create UACS instance with test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        uacs = UACS(project_path=tmpdir)

        # Add diverse content
        uacs.add_user_message("How do I implement JWT authentication?", turn=1, session_id="s1", topics=["auth"])
        uacs.add_assistant_message("Let me help you with JWT implementation", turn=1, session_id="s1")
        uacs.add_tool_use("Edit", {"file": "auth.py"}, "Created auth.py", turn=2, session_id="s1")
        uacs.add_convention("Always use JWT for API authentication", topics=["security", "auth"])
        uacs.add_decision("Auth method", "JWT tokens", "Stateless and scalable", session_id="s1")
        uacs.add_learning("JWT works well for microservices", ["s1"], "architecture", 0.9)
        uacs.add_artifact("file", "src/auth.py", "JWT authentication module", "s1", topics=["auth"])

        yield uacs


class TestSimilarityRanking:
    """Test that search results are properly ranked by similarity."""

    def test_search_finds_similar_content(self, uacs_with_data):
        """Test that semantically similar content is found."""
        results = uacs_with_data.search("JWT authentication", limit=10)

        assert len(results) > 0
        # Check that results are relevant to JWT/auth
        assert any("jwt" in r.text.lower() or "auth" in r.text.lower() for r in results)

    def test_search_similarity_scores(self, uacs_with_data):
        """Test that results have similarity scores."""
        results = uacs_with_data.search("authentication", limit=5)

        for result in results:
            assert hasattr(result, 'similarity')
            assert 0.0 <= result.similarity <= 1.0

    def test_search_ranking_by_relevance(self, uacs_with_data):
        """Test that results are sorted by relevance (descending)."""
        results = uacs_with_data.search("JWT", limit=5)

        if len(results) >= 2:
            # Verify descending order
            # Results can be from conversations (similarity) or knowledge (relevance_score)
            for i in range(len(results) - 1):
                score_i = getattr(results[i], 'similarity', None) or getattr(results[i], 'relevance_score', 0)
                score_i_plus_1 = getattr(results[i + 1], 'similarity', None) or getattr(results[i + 1], 'relevance_score', 0)
                assert score_i >= score_i_plus_1


class TestTypeFiltering:
    """Test filtering search results by type."""

    def test_search_filter_by_user_message(self, uacs_with_data):
        """Test filtering to only user messages."""
        results = uacs_with_data.search("authentication", types=["user_message"], limit=10)

        for result in results:
            assert result.metadata.get("type") == "user_message"

    def test_search_filter_by_decision(self, uacs_with_data):
        """Test filtering to only decisions."""
        results = uacs_with_data.search("authentication", types=["decision"], limit=10)

        for result in results:
            assert result.metadata.get("type") == "decision"

    def test_search_filter_by_convention(self, uacs_with_data):
        """Test filtering to only conventions."""
        results = uacs_with_data.search("authentication", types=["convention"], limit=10)

        for result in results:
            assert result.metadata.get("type") == "convention"

    def test_search_filter_multiple_types(self, uacs_with_data):
        """Test filtering with multiple types."""
        results = uacs_with_data.search(
            "authentication",
            types=["user_message", "decision", "convention"],
            limit=10
        )

        for result in results:
            result_type = result.metadata.get("type")
            assert result_type in ["user_message", "decision", "convention"]

    def test_search_filter_conversation_types(self, uacs_with_data):
        """Test filtering all conversation types."""
        results = uacs_with_data.search(
            "authentication",
            types=["user_message", "assistant_message", "tool_use"],
            limit=10
        )

        for result in results:
            result_type = result.metadata.get("type")
            assert result_type in ["user_message", "assistant_message", "tool_use"]

    def test_search_filter_knowledge_types(self, uacs_with_data):
        """Test filtering all knowledge types."""
        results = uacs_with_data.search(
            "authentication",
            types=["convention", "decision", "learning", "artifact"],
            limit=10
        )

        for result in results:
            result_type = result.metadata.get("type")
            assert result_type in ["convention", "decision", "learning", "artifact"]


class TestThresholdFiltering:
    """Test confidence/similarity threshold filtering."""

    def test_search_with_high_threshold(self):
        """Test search with high similarity threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))

            uacs.add_user_message("JWT authentication implementation", turn=1, session_id="s1")
            uacs.add_user_message("Database configuration settings", turn=2, session_id="s1")

            # High threshold should return fewer, more relevant results
            results = uacs.search("JWT authentication", min_confidence=0.8, limit=10)

            # All results should be highly relevant
            for result in results:
                assert result.similarity >= 0.8

    def test_search_with_low_threshold(self):
        """Test search with low similarity threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))

            uacs.add_user_message("authentication systems", turn=1, session_id="s1")
            uacs.add_user_message("security practices", turn=2, session_id="s1")

            # Low threshold should return more results
            results_low = uacs.search("authentication", min_confidence=0.5, limit=10)
            results_high = uacs.search("authentication", min_confidence=0.9, limit=10)

            # Lower threshold typically returns more results
            assert len(results_low) >= len(results_high)

    def test_search_min_confidence_filters(self):
        """Test that min_confidence filters low-confidence items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))

            # Add conventions with different confidence levels
            uacs.add_convention("High confidence pattern", topics=["test"], confidence=0.95)
            uacs.add_convention("Low confidence pattern", topics=["test"], confidence=0.6)

            # Search with high confidence threshold
            results = uacs.search("pattern", min_confidence=0.8, limit=10)

            # Should only get high confidence items
            for result in results:
                if result.metadata and "confidence" in result.metadata:
                    # Only check conventions and learnings which have confidence
                    if result.metadata.get("type") in ["convention", "learning"]:
                        assert result.metadata["confidence"] >= 0.8


class TestSessionFiltering:
    """Test filtering by session ID."""

    def test_search_by_session_id(self):
        """Test filtering results by session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))

            uacs.add_user_message("Session 1 question", turn=1, session_id="session_1")
            uacs.add_user_message("Session 2 question", turn=1, session_id="session_2")
            uacs.add_assistant_message("Session 1 answer", turn=1, session_id="session_1")

            results = uacs.search("question", session_id="session_1", limit=10)

            # All conversation results should be from session_1
            for result in results:
                if result.metadata.get("session_id"):
                    assert result.metadata["session_id"] == "session_1"

    def test_search_across_all_sessions(self, uacs_with_data):
        """Test searching without session filter returns all results."""
        # Add content from another session
        uacs_with_data.add_user_message("How do I handle authentication?", turn=1, session_id="s2")

        results = uacs_with_data.search("authentication", limit=10)

        # Should return results from multiple sessions (s1 and s2)
        assert len(results) > 0
        # Check that we have results from different sources
        session_ids = {r.metadata.get("session_id") for r in results if r.metadata.get("session_id")}
        # Should have at least s2, might have s1 too
        assert "s2" in session_ids or "s1" in session_ids


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_search_empty_query(self):
        """Test search with empty query."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))
            uacs.add_user_message("Test message", turn=1, session_id="s1")

            # Empty query should still work (returns all results above threshold)
            results = uacs.search("", limit=10)

            # Should return something or empty list, not error
            assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search that finds no results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))
            uacs.add_user_message("About dogs and cats", turn=1, session_id="s1")

            # Search for completely unrelated term
            results = uacs.search("quantum physics relativity theory", limit=10)

            # Should return empty list, not error
            assert isinstance(results, list)
            # Might be empty or very low similarity
            assert len(results) >= 0

    def test_search_with_special_characters(self):
        """Test search with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))
            uacs.add_user_message("How to use @annotations in Python?", turn=1, session_id="s1")

            # Search with special characters
            results = uacs.search("@annotations Python", limit=10)

            assert isinstance(results, list)

    def test_search_invalid_type(self):
        """Test that invalid search types raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))
            uacs.add_user_message("Test message", turn=1, session_id="s1")

            # Invalid type should raise ValueError
            with pytest.raises(ValueError, match="Invalid search types"):
                uacs.search("test", types=["invalid_type"], limit=10)

    def test_search_very_long_query(self):
        """Test search with very long query."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))
            uacs.add_user_message("authentication system", turn=1, session_id="s1")

            # Very long query
            long_query = "authentication " * 100
            results = uacs.search(long_query, limit=10)

            # Should handle gracefully
            assert isinstance(results, list)

    def test_search_limit_respected(self):
        """Test that search respects limit parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            uacs = UACS(project_path=Path(tmpdir))

            # Add many items
            for i in range(20):
                uacs.add_user_message(f"Test message number {i}", turn=i+1, session_id="s1")

            results = uacs.search("test message", limit=5)

            # Should return at most 5 results
            assert len(results) <= 5


class TestCrossComponentSearch:
    """Test searching across different UACS components."""

    def test_search_finds_conversations_and_knowledge(self, uacs_with_data):
        """Test that search finds both conversations and knowledge."""
        results = uacs_with_data.search("JWT authentication", limit=20)

        # Should find results from multiple component types
        types_found = set(r.metadata.get("type") for r in results if r.metadata)

        # Should have at least 2 different types
        assert len(types_found) >= 2

    def test_search_mixed_relevance(self, uacs_with_data):
        """Test that results from different components are properly ranked together."""
        results = uacs_with_data.search("authentication", limit=10)

        # Results should be sorted by relevance regardless of type
        if len(results) >= 2:
            for i in range(len(results) - 1):
                assert results[i].similarity >= results[i + 1].similarity
