"""Tests for enhanced context management."""

import pytest
from pathlib import Path
from uacs.context.shared_context import SharedContextManager


@pytest.fixture
def context_mgr(tmp_project):
    """Create SharedContextManager instance."""
    return SharedContextManager(tmp_project / ".state" / "context")


def test_context_manager_init(context_mgr):
    """Test context manager initialization."""
    assert context_mgr.storage_path.exists()
    assert isinstance(context_mgr.entries, dict)
    assert isinstance(context_mgr.summaries, dict)


def test_add_entry_with_quality(context_mgr):
    """Test adding entry with quality scoring."""
    entry_id = context_mgr.add_entry(
        content="This is a substantial code example with ```python\nprint('hello')\n```",
        agent="test-agent",
        metadata={"source": "test"}
    )

    assert entry_id in context_mgr.entries
    entry = context_mgr.entries[entry_id]
    assert entry.quality > 0
    assert entry.quality <= 1.0


def test_quality_scoring_short_content(context_mgr):
    """Test quality scoring penalizes short content."""
    entry_id = context_mgr.add_entry(
        content="Short",
        agent="test-agent"
    )

    entry = context_mgr.entries[entry_id]
    assert entry.quality < 1.0  # Should be penalized


def test_quality_scoring_code_blocks(context_mgr):
    """Test quality scoring rewards code blocks."""
    entry_id = context_mgr.add_entry(
        content="Here's a good example:\n```python\ndef hello():\n    print('world')\n```",
        agent="test-agent"
    )

    entry = context_mgr.entries[entry_id]
    # Should have higher quality due to code block
    assert entry.quality > 0.7


def test_quality_scoring_errors(context_mgr):
    """Test quality scoring penalizes error messages."""
    entry_id = context_mgr.add_entry(
        content="Error: Something failed terribly",
        agent="test-agent"
    )

    entry = context_mgr.entries[entry_id]
    assert entry.quality < 1.0  # Should be penalized for error


def test_count_tokens(context_mgr):
    """Test token counting."""
    text = "This is a test sentence with multiple words."
    count = context_mgr.count_tokens(text)

    assert count > 0
    # Should be roughly text length / 4 if tiktoken not available
    assert count > 5


def test_get_compressed_context_with_quality_filter(context_mgr):
    """Test getting context with quality filtering."""
    # Add high quality entry
    context_mgr.add_entry(
        content="This is a substantial high-quality entry with good code ```python\ncode()\n```",
        agent="test-agent"
    )

    # Add low quality entry
    context_mgr.add_entry(
        content="Err",
        agent="test-agent"
    )

    # Get context with quality filter
    context = context_mgr.get_compressed_context(
        agent="test-agent",
        max_tokens=1000,
        min_quality=0.7
    )

    assert isinstance(context, str)
    # Should contain high quality content
    assert "substantial" in context or len(context) > 0


def test_get_stats_includes_quality(context_mgr):
    """Test stats include quality metrics."""
    # Add some entries
    context_mgr.add_entry("Good content with code ```x```", "test")
    context_mgr.add_entry("Error occurred", "test")

    stats = context_mgr.get_stats()

    assert "avg_quality" in stats
    assert "high_quality_entries" in stats
    assert "low_quality_entries" in stats


def test_add_entry_with_metadata(context_mgr):
    """Test adding entry with custom metadata."""
    metadata = {
        "source": "user",
        "topic": "testing",
        "importance": "high"
    }

    entry_id = context_mgr.add_entry(
        content="Test content",
        agent="test-agent",
        metadata=metadata
    )

    entry = context_mgr.entries[entry_id]
    assert entry.metadata == metadata


def test_deduplication(context_mgr):
    """Test content deduplication."""
    content = "Duplicate content"

    id1 = context_mgr.add_entry(content, "agent1")
    id2 = context_mgr.add_entry(content, "agent2")

    # Should return same ID for duplicate content
    assert id1 == id2
    assert len(context_mgr.entries) == 1


def test_context_persistence(tmp_project):
    """Test context persists across instances."""
    storage_path = tmp_project / ".state" / "context"

    # Create first instance and add entry
    mgr1 = SharedContextManager(storage_path)
    entry_id = mgr1.add_entry("Persistent content", "test-agent")
    mgr1._save_context()

    # Create second instance and verify entry exists
    mgr2 = SharedContextManager(storage_path)
    assert entry_id in mgr2.entries
    assert mgr2.entries[entry_id].content == "Persistent content"


def test_get_compressed_context_respects_token_limit(context_mgr):
    """Test context respects token limit."""
    # Add multiple entries
    for i in range(10):
        context_mgr.add_entry(
            f"Entry {i}: " + "word " * 100,  # ~100 words each
            "test-agent"
        )

    # Get context with small token limit
    context = context_mgr.get_compressed_context(
        agent="test-agent",
        max_tokens=100
    )

    # Should be limited
    token_count = context_mgr.count_tokens(context)
    assert token_count <= 150  # Some buffer for formatting
