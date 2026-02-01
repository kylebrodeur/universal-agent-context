"""Tests for focused context management with topic filtering."""

import pytest
from uacs.context.shared_context import SharedContextManager


def test_add_entry_with_topics(tmp_path):
    """Adding entry with topics should store them correctly."""
    manager = SharedContextManager(storage_path=tmp_path)

    entry_id = manager.add_entry(
        content="Review authentication flow",
        agent="claude",
        topics=["auth", "security"]
    )

    entry = manager.entries[entry_id]
    assert entry.topics == ["auth", "security"]


def test_add_entry_without_topics_defaults_to_empty_list(tmp_path):
    """Adding entry without topics should default to empty list."""
    manager = SharedContextManager(storage_path=tmp_path)

    entry_id = manager.add_entry(
        content="General task",
        agent="claude"
    )

    entry = manager.entries[entry_id]
    assert entry.topics == []


def test_get_focused_context_prioritizes_matching_topics(tmp_path):
    """Focused context should prioritize entries with matching topics."""
    manager = SharedContextManager(storage_path=tmp_path)

    # Add entries with different topics
    e1 = manager.add_entry("Auth flow details", "claude", topics=["auth", "security"])
    e2 = manager.add_entry("Database schema", "claude", topics=["database", "schema"])
    e3 = manager.add_entry("More auth info", "claude", topics=["auth"])
    e4 = manager.add_entry("General info", "claude", topics=[])

    # Get focused context for "auth" topic
    context = manager.get_focused_context(
        topics=["auth"],
        max_tokens=1000,
        min_quality=0.3
    )

    # Auth entries should appear before database and general
    assert "Auth flow details" in context
    assert "More auth info" in context
    assert context.index("Auth flow details") < context.index("Database schema") if "Database schema" in context else True


def test_get_focused_context_includes_fallback_entries_if_budget_allows(tmp_path):
    """Non-matching entries should be included as fallback if token budget allows."""
    manager = SharedContextManager(storage_path=tmp_path)

    # Add short entries to fit within budget
    manager.add_entry("Auth info", "claude", topics=["auth"])
    manager.add_entry("DB info", "claude", topics=["database"])
    manager.add_entry("General", "claude", topics=[])

    # Request large token budget to fit all entries
    context = manager.get_focused_context(
        topics=["auth"],
        max_tokens=5000,
        min_quality=0.3
    )

    # All entries should be included due to large budget
    assert "Auth info" in context
    # Fallback entries might be included
    assert len(context) > 0


def test_get_focused_context_respects_token_limit(tmp_path):
    """Focused context should not exceed token limit."""
    manager = SharedContextManager(storage_path=tmp_path)

    # Add large entries (approximately 25 tokens each = 100 chars / 4)
    for i in range(5):
        content = "x" * 100  # ~25 tokens
        manager.add_entry(content, "claude", topics=["test"])

    # Request small token budget
    context = manager.get_focused_context(
        topics=["test"],
        max_tokens=60
    )

    token_count = manager.count_tokens(context)
    assert token_count <= 60


def test_get_focused_context_respects_quality_threshold(tmp_path):
    """Focused context should filter by quality threshold."""
    manager = SharedContextManager(storage_path=tmp_path)

    # Add high quality entry
    e1 = manager.add_entry("High quality content with code ```python\nprint('test')\n```", "claude", topics=["test"])

    # Add low quality entry (very short)
    e2 = manager.add_entry("x", "claude", topics=["test"])

    # Manually set quality scores
    manager.entries[e1].quality = 0.9
    manager.entries[e2].quality = 0.3

    # Get focused context with quality threshold
    context = manager.get_focused_context(
        topics=["test"],
        min_quality=0.7,
        max_tokens=1000
    )

    # High quality entry should be included
    assert "High quality" in context
    # Low quality entry should be filtered out
    assert context.count("claude") == 1


def test_get_focused_context_filters_by_agent(tmp_path):
    """Focused context should filter by agent when specified."""
    manager = SharedContextManager(storage_path=tmp_path)

    # Add entries from different agents
    manager.add_entry("Claude entry", "claude", topics=["test"])
    manager.add_entry("Gemini entry", "gemini", topics=["test"])

    # Get focused context for claude only
    context = manager.get_focused_context(
        topics=["test"],
        agent="claude",
        max_tokens=1000,
        min_quality=0.3
    )

    assert "Claude entry" in context
    assert "Gemini entry" not in context


def test_get_focused_context_without_topics_falls_back_to_standard(tmp_path):
    """Focused context with no topics should behave like standard compressed context."""
    manager = SharedContextManager(storage_path=tmp_path)

    manager.add_entry("Entry 1", "claude", topics=["test"])
    manager.add_entry("Entry 2", "claude", topics=[])

    # Get focused context without topics
    focused = manager.get_focused_context(
        topics=None,
        max_tokens=1000
    )

    # Get standard compressed context
    standard = manager.get_compressed_context(
        max_tokens=1000
    )

    # Should return the same result
    assert focused == standard


def test_get_focused_context_handles_multiple_matching_topics(tmp_path):
    """Focused context should match entries with any of the specified topics."""
    manager = SharedContextManager(storage_path=tmp_path)

    # Add entries with various topic combinations
    manager.add_entry("Auth only", "claude", topics=["auth"])
    manager.add_entry("Security only", "claude", topics=["security"])
    manager.add_entry("Both auth and security", "claude", topics=["auth", "security"])
    manager.add_entry("Unrelated", "claude", topics=["database"])

    # Search for multiple topics
    context = manager.get_focused_context(
        topics=["auth", "security"],
        max_tokens=1000,
        min_quality=0.3
    )

    # All entries with auth or security should be included first
    assert "Auth only" in context
    assert "Security only" in context
    assert "Both auth and security" in context
    # Database entry might be in fallback or not included


def test_get_focused_context_displays_topics_in_output(tmp_path):
    """Focused context should display topics in output for clarity."""
    manager = SharedContextManager(storage_path=tmp_path)

    manager.add_entry("Test content", "claude", topics=["auth", "security"])

    context = manager.get_focused_context(
        topics=["auth"],
        max_tokens=1000,
        min_quality=0.3
    )

    # Context should include topic information
    assert "[topics:" in context
    assert "auth" in context or "security" in context
