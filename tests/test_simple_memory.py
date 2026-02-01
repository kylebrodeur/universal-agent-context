"""Tests for SimpleMemoryStore and memory CLI commands."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Memory CLI tests require MAOS integration - skip for now
# from multi_agent_cli.cli.memory import memory_app  # External dependency

from uacs.memory.simple_memory import MemoryEntry, SimpleMemoryStore

# Runner would be used for CLI tests
# from typer.testing import CliRunner
# runner = CliRunner()


@pytest.fixture
def project_root(tmp_path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    return root


@pytest.fixture
def global_root(tmp_path) -> Path:
    root = tmp_path / "global"
    root.mkdir()
    return root


@pytest.fixture
def store(project_root, global_root) -> SimpleMemoryStore:
    return SimpleMemoryStore(project_path=project_root, global_path=global_root)


def make_old_entry(store: SimpleMemoryStore, key: str, days_old: int) -> MemoryEntry:
    """Helper to create an entry with an older timestamp."""
    entry = store.store(key, {"note": "old"}, scope="project")
    old_timestamp = (
        datetime.now(timezone.utc) - timedelta(days=days_old)
    ).isoformat()
    payload = json.loads(entry.path.read_text())
    payload["_created"] = old_timestamp
    payload["_updated"] = old_timestamp
    entry.path.write_text(json.dumps(payload, indent=2))
    return entry


def test_init_creates_config_and_dirs(store: SimpleMemoryStore):
    project_dir = store.init_storage("project")
    global_dir = store.init_storage("global")

    assert project_dir.exists()
    assert global_dir.exists()
    assert (project_dir.parent / "config.json").exists()
    assert (global_dir.parent / "config.json").exists()


def test_store_and_retrieve_project_scope(store: SimpleMemoryStore):
    entry = store.store("notes", {"summary": "project data"}, scope="project")
    retrieved = store.retrieve("notes")

    assert retrieved is not None
    assert retrieved.data["summary"] == "project data"
    assert retrieved.scope == "project"
    assert entry.path.exists()


def test_retrieve_falls_back_to_global(store: SimpleMemoryStore):
    store.store("shared", {"detail": "global copy"}, scope="global")

    retrieved = store.retrieve("shared")
    assert retrieved is not None
    assert retrieved.scope == "global"
    assert retrieved.data["detail"] == "global copy"


def test_project_overrides_global_lookup(store: SimpleMemoryStore):
    store.store("topic", {"value": "global"}, scope="global")
    store.store("topic", {"value": "project"}, scope="project")

    retrieved = store.retrieve("topic")
    assert retrieved is not None
    assert retrieved.scope == "project"
    assert retrieved.data["value"] == "project"


def test_list_entries_scope_filter(store: SimpleMemoryStore):
    store.store("project-only", {"a": 1}, scope="project")
    store.store("global-only", {"b": 2}, scope="global")

    global_entries = store.list_entries("global")
    assert len(global_entries) == 1
    assert global_entries[0].key == "global-only"

    both_entries = store.list_entries("both")
    assert len(both_entries) == 2


def test_search_matches_key_and_values(store: SimpleMemoryStore):
    store.store("react-patterns", {"tags": ["React", "Hooks"]}, scope="project")
    results = store.search("hooks")

    assert len(results) == 1
    assert results[0].key == "react-patterns"


def test_search_is_case_insensitive(store: SimpleMemoryStore):
    store.store("CaseTest", {"Text": "MiXeD Case"}, scope="project")
    results = store.search("mixed")
    assert results


def test_delete_existing_entry(store: SimpleMemoryStore):
    store.store("temp", {"x": 1}, scope="project")
    deleted = store.delete("temp", scope="project")

    assert deleted is True
    assert store.retrieve("temp", scope="project") is None


def test_delete_missing_entry_returns_false(store: SimpleMemoryStore):
    assert store.delete("missing", scope="project") is False


def test_clean_removes_old_entries(store: SimpleMemoryStore):
    make_old_entry(store, "old-entry", days_old=60)
    removed = store.clean(older_than_days=30, scope="project")
    assert removed == 1


def test_clean_ignores_recent_entries(store: SimpleMemoryStore):
    store.store("recent", {"value": "keep"}, scope="project")
    removed = store.clean(older_than_days=1, scope="project")
    assert removed == 0
    assert store.retrieve("recent") is not None


def test_stats_handles_missing_dirs(store: SimpleMemoryStore):
    stats = store.get_stats()
    assert stats["project"]["entries"] == 0
    assert stats["global"]["entries"] == 0


def test_stats_reports_entry_counts(store: SimpleMemoryStore):
    store.store("one", {"a": 1}, scope="project")
    store.store("two", {"b": 2}, scope="global")

    stats = store.get_stats()
    assert stats["project"]["entries"] == 1
    assert stats["global"]["entries"] == 1
    assert stats["project"]["size_bytes"] > 0


def test_invalid_scope_raises(store: SimpleMemoryStore):
    with pytest.raises(ValueError):
        store.store("bad", {"x": 1}, scope="invalid")

    with pytest.raises(ValueError):
        store.list_entries("invalid")


def test_invalid_json_is_skipped(store: SimpleMemoryStore):
    dir_path = store.init_storage("project")
    bad_file = dir_path / "broken.json"
    bad_file.write_text("{not valid json")

    entries = store.list_entries("project")
    assert entries == []


def test_sanitizes_key_for_filename(store: SimpleMemoryStore):
    entry = store.store("React Patterns/Notes", {"k": "v"}, scope="project")
    assert entry.path.name.startswith("React-Patterns-Notes")
    assert entry.path.suffix == ".json"


def test_retrieve_returns_none_for_missing(store: SimpleMemoryStore):
    assert store.retrieve("does-not-exist") is None


def test_store_preserves_created_on_update(store: SimpleMemoryStore):
    first = store.store("update-me", {"v": 1}, scope="project")
    second = store.store("update-me", {"v": 2}, scope="project")

    assert first.created_at == second.created_at
    assert first.updated_at != second.updated_at
    assert store.retrieve("update-me").data["v"] == 2


def test_store_rejects_non_mapping(store: SimpleMemoryStore):
    with pytest.raises(ValueError):
        store.store("bad", "not-a-dict", scope="project")  # type: ignore[arg-type]


@pytest.mark.skip(reason="CLI tests require MAOS integration")
def test_cli_init_and_stats_with_custom_paths(tmp_path):
    pass


@pytest.mark.skip(reason="CLI tests require MAOS integration")
def test_cli_search_outputs_results(tmp_path):
    pass


@pytest.mark.skip(reason="CLI tests require MAOS integration")
def test_cli_clean_reports_deleted_count(tmp_path):
    pass
