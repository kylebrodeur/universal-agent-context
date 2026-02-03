"""Simple JSON-based memory store with project/global hierarchy.

.. deprecated:: 0.3.0
    SimpleMemoryStore is deprecated in favor of the Semantic API.
    Use ``UACS.add_decision()``, ``UACS.add_convention()``, etc. for structured
    memory with semantic search and rich metadata.
    SimpleMemoryStore will be removed in v1.0.0.
"""

from __future__ import annotations

import json
import re
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

VALID_SCOPES = {"project", "global"}


def _utcnow_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def _sanitize_key(key: str) -> str:
    """Convert arbitrary keys into safe filenames."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", key.strip())
    return cleaned or "memory-entry"


@dataclass
class MemoryEntry:
    """Structured representation of a memory entry."""

    key: str
    scope: str
    data: dict[str, Any]
    created_at: str
    updated_at: str
    path: Path

    @classmethod
    def from_file(cls, path: Path, scope: str) -> MemoryEntry | None:
        """Load a memory entry from a JSON file."""
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError:
            return None

        data_field = raw.get("data")
        if data_field is None:
            data_field = {k: v for k, v in raw.items() if not k.startswith("_")}

        return cls(
            key=raw.get("_key", path.stem),
            scope=raw.get("_scope", scope),
            data=data_field if isinstance(data_field, dict) else {},
            created_at=raw.get("_created", raw.get("_timestamp", _utcnow_iso())),
            updated_at=raw.get("_updated", raw.get("_timestamp", _utcnow_iso())),
            path=path,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize entry to dictionary for JSON storage."""
        return {
            "_key": self.key,
            "_scope": self.scope,
            "_created": self.created_at,
            "_updated": self.updated_at,
            "data": self.data,
        }


class SimpleMemoryStore:
    """Simple JSON-based key-value memory with scoped lookup.
    
    .. deprecated:: 0.3.0
        SimpleMemoryStore is deprecated. Use the UACS Semantic API instead:
        
        .. code-block:: python
        
            from uacs import UACS
            uacs = UACS(project_path=Path("."))
            
            # Instead of store("key", {"note": "value"})
            uacs.add_convention(
                content="Your content here",
                topics=["topic1", "topic2"],
                confidence=0.9
            )
        
        The Semantic API provides:
        - Structured Pydantic models with validation
        - Semantic search with embeddings
        - Rich metadata (topics, confidence, provenance)
        - Type-specific storage (decisions, conventions, learnings)
        
        SimpleMemoryStore will be removed in v1.0.0.
    """

    def __init__(
        self,
        project_path: Path,
        global_path: Path | None = None,
    ):
        warnings.warn(
            "SimpleMemoryStore is deprecated as of v0.3.0 and will be removed in v1.0.0. "
            "Use the UACS Semantic API (UACS.add_decision, UACS.add_convention, etc.) "
            "for structured memory with semantic search and rich metadata. "
            "See https://github.com/kylebrodeur/universal-agent-context for migration guide.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.project_root = project_path / ".state" / "memory"
        self.global_root = global_path or Path.home() / ".multi-agent" / "memory"

    def init_storage(self, scope: str = "project") -> Path:
        """Initialize storage directories and config for a scope."""
        resolved_scope = self._validate_scope(scope)
        scope_dir = self._scope_dir(resolved_scope)
        scope_dir.mkdir(parents=True, exist_ok=True)

        config_path = scope_dir.parent / "config.json"
        if not config_path.exists():
            payload = {
                "storage": "simple",
                "version": "1.0",
                "initialized_at": _utcnow_iso(),
                "scope": resolved_scope,
            }
            config_path.write_text(json.dumps(payload, indent=2))

        return scope_dir

    def store(
        self,
        key: str,
        value: Mapping[str, Any],
        scope: str = "project",
    ) -> MemoryEntry:
        """Store a memory entry and return the created entry."""
        resolved_scope = self._validate_scope(scope)
        sanitized_key = _sanitize_key(key)
        scope_dir = self.init_storage(resolved_scope)

        file_path = scope_dir / f"{sanitized_key}.json"
        now = _utcnow_iso()
        created_at = now

        if not isinstance(value, Mapping):
            raise ValueError("Memory value must be a mapping")

        existing_entry = self._load_entry(file_path, resolved_scope)
        if existing_entry:
            created_at = existing_entry.created_at

        entry = MemoryEntry(
            key=key,
            scope=resolved_scope,
            data=dict(value),
            created_at=created_at,
            updated_at=now,
            path=file_path,
        )

        file_path.write_text(json.dumps(entry.to_dict(), indent=2))
        return entry

    def retrieve(self, key: str, scope: str = "both") -> MemoryEntry | None:
        """Retrieve entry by key honoring project→global lookup."""
        scopes = (
            ("project", "global") if scope == "both" else (self._validate_scope(scope),)
        )

        for current_scope in scopes:
            file_path = self._scope_dir(current_scope) / f"{_sanitize_key(key)}.json"
            entry = self._load_entry(file_path, current_scope)
            if entry:
                return entry

        return None

    def delete(self, key: str, scope: str = "project") -> bool:
        """Delete entry for a specific scope."""
        resolved_scope = self._validate_scope(scope)
        file_path = self._scope_dir(resolved_scope) / f"{_sanitize_key(key)}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def list_entries(self, scope: str = "both") -> list[MemoryEntry]:
        """List all entries for the provided scope."""
        entries: list[MemoryEntry] = []
        scopes = (
            ("project", "global") if scope == "both" else (self._validate_scope(scope),)
        )

        for current_scope in scopes:
            scope_dir = self._scope_dir(current_scope)
            if not scope_dir.exists():
                continue
            for file_path in scope_dir.glob("*.json"):
                entry = self._load_entry(file_path, current_scope)
                if entry:
                    entries.append(entry)
        return entries

    def search(self, query: str, scope: str = "both") -> list[MemoryEntry]:
        """Search entries by substring match."""
        needle = query.lower()
        results = []
        for entry in self.list_entries(scope):
            haystack = json.dumps(entry.data).lower()
            if needle in entry.key.lower() or needle in haystack:
                results.append(entry)
        return results

    def clean(self, older_than_days: int = 30, scope: str = "project") -> int:
        """Remove entries older than provided days. Returns deleted count."""
        resolved_scope = self._validate_scope(scope)
        cutoff = datetime.now(UTC) - timedelta(days=older_than_days)
        deleted = 0

        for entry in self.list_entries(resolved_scope):
            try:
                created_time = datetime.fromisoformat(entry.created_at)
            except ValueError:
                created_time = datetime.utcfromtimestamp(entry.path.stat().st_mtime)

            if created_time.tzinfo is None:
                created_time = created_time.replace(tzinfo=UTC)

            if created_time < cutoff and entry.path.exists():
                entry.path.unlink()
                deleted += 1

        return deleted

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Return statistics for project and global scopes."""
        stats = {}
        for scope in ("project", "global"):
            scope_dir = self._scope_dir(scope)
            entry_files = list(scope_dir.glob("*.json")) if scope_dir.exists() else []
            size_bytes = sum(f.stat().st_size for f in entry_files)

            latest_updated = None
            entry_count = 0
            for entry in (self._load_entry(f, scope) for f in entry_files):
                if not entry:
                    continue
                entry_count += 1
                try:
                    updated_time = datetime.fromisoformat(entry.updated_at)
                except ValueError:
                    updated_time = datetime.utcfromtimestamp(entry.path.stat().st_mtime)
                if updated_time.tzinfo is None:
                    updated_time = updated_time.replace(tzinfo=UTC)
                if latest_updated is None or updated_time > latest_updated:
                    latest_updated = updated_time

            stats[scope] = {
                "entries": entry_count,
                "size_bytes": size_bytes,
                "last_updated": latest_updated.isoformat() if latest_updated else None,
                "path": str(scope_dir),
            }

        return stats

    def _scope_dir(self, scope: str) -> Path:
        """Return the directory for a scope (always within knowledge/)."""
        base = self.project_root if scope == "project" else self.global_root
        return base / "knowledge"

    def _load_entry(self, file_path: Path, scope: str) -> MemoryEntry | None:
        """Load entry from file; skip invalid JSON."""
        if not file_path.exists():
            return None
        return MemoryEntry.from_file(file_path, scope)

    def _validate_scope(self, scope: str) -> str:
        """Ensure scope is recognized."""
        if scope not in VALID_SCOPES:
            allowed = ", ".join(sorted(VALID_SCOPES))
            raise ValueError(f"Invalid scope: {scope}. Use one of: {allowed}")
        return scope


__all__ = ["MemoryEntry", "SimpleMemoryStore"]
