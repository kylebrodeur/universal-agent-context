"""Shared context management with compression for multi-agent communication.

This module provides token-efficient context sharing between agents using:
1. Semantic compression (summarization)
2. Deduplication
3. Reference-based storage
4. Progressive context building
"""

import hashlib
import json
import logging
import uuid
import zlib
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ContextEntry:
    """A single context entry with metadata."""

    id: str
    content: str
    compressed: bytes
    agent: str
    timestamp: str
    references: list[str]
    token_estimate: int
    hash: str
    quality: float = 1.0  # Quality score 0-1
    metadata: dict[str, Any] = None  # Additional metadata
    topics: list[str] = None  # Optional topic tags for focused retrieval

    def __post_init__(self):
        """Initialize default metadata and topics."""
        if self.metadata is None:
            self.metadata = {}
        if self.topics is None:
            self.topics = []


@dataclass
class ContextSummary:
    """A compressed summary of multiple context entries."""

    id: str
    summary: str
    entry_ids: list[str]
    token_savings: int
    created: str


class SharedContextManager:
    """Manages shared context between agents with compression."""

    def __init__(self, storage_path: Path | None = None):
        """Initialize context manager.

        Args:
            storage_path: Path to store context data
        """
        self.storage_path = storage_path or Path(".state/context")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.entries: dict[str, ContextEntry] = {}
        self.summaries: dict[str, ContextSummary] = {}
        self.dedup_index: dict[str, str] = {}  # hash -> entry_id

        # Initialize token encoder
        if TIKTOKEN_AVAILABLE:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoder = None

        self._load_context()

    def add_context(
        self, key: str, content: str, metadata: dict[str, Any] | None = None
    ) -> str:
        """Alias for add_entry with key parameter.

        Args:
            key: Context key (used as agent name)
            content: Content to store
            metadata: Optional metadata

        Returns:
            Entry ID
        """
        return self.add_entry(content, agent=key, metadata=metadata)

    def add_entry(
        self,
        content: str,
        agent: str,
        references: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        topics: list[str] | None = None,
    ) -> str:
        """Add context entry with automatic compression.

        Args:
            content: Context content
            agent: Agent that created this context
            references: IDs of referenced entries
            metadata: Optional additional metadata
            topics: Optional topic tags for focused retrieval

        Returns:
            Entry ID
        """
        # Check for duplicates
        content_hash = self._hash_content(content)
        if content_hash in self.dedup_index:
            return self.dedup_index[content_hash]

        # Create entry
        entry_id = self._generate_id()
        compressed = zlib.compress(content.encode("utf-8"))
        tokens = self.count_tokens(content)
        quality = self._calculate_quality(content)

        entry = ContextEntry(
            id=entry_id,
            content=content,
            compressed=compressed,
            agent=agent,
            timestamp=datetime.now().isoformat(),
            references=references or [],
            token_estimate=tokens,
            hash=content_hash,
            quality=quality,
            metadata=metadata or {},
            topics=topics or [],
        )

        self.entries[entry_id] = entry
        self.dedup_index[content_hash] = entry_id

        # Auto-compress if context is getting large
        if len(self.entries) > 10:
            self._auto_compress()

        self._save_entry(entry)

        return entry_id

    def get_entry(self, entry_id: str) -> str | None:
        """Get context entry by ID.

        Args:
            entry_id: Entry ID

        Returns:
            Entry content or None
        """
        entry = self.entries.get(entry_id)
        return entry.content if entry else None

    def get_compressed_context(
        self,
        agent: str | None = None,
        max_tokens: int = 4000,
        min_quality: float = 0.7,
    ) -> str:
        """Get compressed context suitable for agent prompts.

        Args:
            agent: Filter by agent (None for all)
            max_tokens: Maximum tokens to return
            min_quality: Minimum quality score (0-1)

        Returns:
            Compressed context string
        """
        # Collect relevant entries
        entries = [
            e
            for e in self.entries.values()
            if (agent is None or e.agent == agent) and e.quality >= min_quality
        ]

        # Sort by weighted combination of quality (70%) and recency (30%)
        entries.sort(
            key=lambda e: (
                e.quality * 0.7 + self._recency_score(e.timestamp) * 0.3,
                e.timestamp,
            ),
            reverse=True,
        )

        # Build context within token budget
        context_parts = []
        token_count = 0

        for entry in entries:
            if token_count + entry.token_estimate > max_tokens:
                break

            context_parts.append(f"[{entry.agent}] {entry.content}")
            token_count += entry.token_estimate

        # Include summaries if available
        for summary in self.summaries.values():
            summary_tokens = self._estimate_tokens(summary.summary)
            if token_count + summary_tokens <= max_tokens:
                context_parts.append(f"[Summary] {summary.summary}")
                token_count += summary_tokens

        return "\n\n".join(context_parts)

    def get_focused_context(
        self,
        topics: list[str] | None = None,
        agent: str | None = None,
        max_tokens: int = 4000,
        min_quality: float = 0.7,
    ) -> str:
        """Get focused context filtered by topics with fallback.

        Args:
            topics: List of topics to prioritize (None for all)
            agent: Filter by agent (None for all)
            max_tokens: Maximum tokens to return
            min_quality: Minimum quality score (0-1)

        Returns:
            Focused context string with topic-matched entries prioritized
        """
        # Collect relevant entries
        all_entries = [
            e
            for e in self.entries.values()
            if (agent is None or e.agent == agent) and e.quality >= min_quality
        ]

        if not topics:
            # No topics specified, use standard compressed context
            return self.get_compressed_context(
                agent=agent, max_tokens=max_tokens, min_quality=min_quality
            )

        # Separate entries by topic matching with boosted quality for multi-topic matches
        topic_set = set(topics)
        matching_entries = []
        fallback_entries = []

        for entry in all_entries:
            entry_topics = set(entry.topics) if entry.topics else set()
            matches = len(entry_topics & topic_set)  # Count topic matches
            if matches > 0:
                # Boost quality based on number of matching topics (20% per match, capped at 1.0)
                boosted_quality = min(entry.quality * (1 + 0.2 * matches), 1.0)
                matching_entries.append((entry, boosted_quality))
            else:
                fallback_entries.append(entry)

        # Sort matching entries by boosted quality (descending) then recency
        matching_entries.sort(key=lambda x: (x[1], x[0].timestamp), reverse=True)
        fallback_entries.sort(key=lambda e: (e.quality, e.timestamp), reverse=True)

        # Build context within token budget, prioritizing matching entries
        context_parts = []
        token_count = 0

        # Add matching entries first (now with boosted quality)
        for entry, boosted_quality in matching_entries:
            if token_count + entry.token_estimate > max_tokens:
                break

            topics_str = f" [topics: {', '.join(entry.topics)}]" if entry.topics else ""
            context_parts.append(f"[{entry.agent}]{topics_str} {entry.content}")
            token_count += entry.token_estimate

        # Add fallback entries if token budget allows
        for entry in fallback_entries:
            if token_count + entry.token_estimate > max_tokens:
                break

            topics_str = f" [topics: {', '.join(entry.topics)}]" if entry.topics else ""
            context_parts.append(f"[{entry.agent}]{topics_str} {entry.content}")
            token_count += entry.token_estimate

        # Include summaries if available and budget allows
        for summary in self.summaries.values():
            summary_tokens = self._estimate_tokens(summary.summary)
            if token_count + summary_tokens <= max_tokens:
                context_parts.append(f"[Summary] {summary.summary}")
                token_count += summary_tokens

        return "\n\n".join(context_parts)

    def create_summary(self, entry_ids: list[str], summary_content: str) -> str:
        """Create a summary of multiple entries.

        Args:
            entry_ids: IDs of entries to summarize
            summary_content: Summary text

        Returns:
            Summary ID
        """
        summary_id = self._generate_id()

        # Calculate token savings
        original_tokens = sum(
            self.entries[eid].token_estimate for eid in entry_ids if eid in self.entries
        )
        summary_tokens = self._estimate_tokens(summary_content)

        summary = ContextSummary(
            id=summary_id,
            summary=summary_content,
            entry_ids=entry_ids,
            token_savings=original_tokens - summary_tokens,
            created=datetime.now().isoformat(),
        )

        self.summaries[summary_id] = summary
        self._save_summary(summary)

        # Remove original entries to save space
        for eid in entry_ids:
            if eid in self.entries:
                del self.entries[eid]

        return summary_id

    def _auto_compress(self):
        """Automatically compress old context entries."""
        # Group old entries by agent
        old_entries = sorted(self.entries.values(), key=lambda e: e.timestamp)[
            :5
        ]  # Compress oldest 5

        if len(old_entries) < 3:
            return

        # Create summary
        entry_ids = [e.id for e in old_entries]
        summary_content = self._create_auto_summary(old_entries)

        self.create_summary(entry_ids, summary_content)

    def _create_auto_summary(self, entries: list[ContextEntry]) -> str:
        """Create automatic summary of entries.

        Args:
            entries: Entries to summarize

        Returns:
            Summary text
        """
        # Simple extractive summary (in production, use LLM)
        summaries = []

        for entry in entries:
            # Extract first sentence or first 100 chars
            content = entry.content
            first_sentence = content.split(".")[0][:100]
            summaries.append(f"[{entry.agent}]: {first_sentence}...")

        return " | ".join(summaries)

    def get_context_graph(self) -> dict[str, Any]:
        """Get context relationships as graph structure.

        Returns:
            Graph structure for visualization
        """
        nodes = []
        edges = []

        # Add entry nodes
        for entry in self.entries.values():
            nodes.append(
                {
                    "id": entry.id,
                    "type": "entry",
                    "agent": entry.agent,
                    "tokens": entry.token_estimate,
                    "timestamp": entry.timestamp,
                }
            )

            # Add reference edges
            for ref_id in entry.references:
                edges.append(
                    {"source": entry.id, "target": ref_id, "type": "reference"}
                )

        # Add summary nodes
        for summary in self.summaries.values():
            nodes.append(
                {
                    "id": summary.id,
                    "type": "summary",
                    "tokens_saved": summary.token_savings,
                    "entry_count": len(summary.entry_ids),
                }
            )

            # Add summary edges
            for entry_id in summary.entry_ids:
                edges.append(
                    {"source": summary.id, "target": entry_id, "type": "summarizes"}
                )

        return {"nodes": nodes, "edges": edges, "stats": self.get_stats()}

    def get_stats(self) -> dict[str, Any]:
        """Get context statistics.

        Returns:
            Statistics dictionary
        """
        total_tokens = sum(e.token_estimate for e in self.entries.values())
        total_saved = sum(s.token_savings for s in self.summaries.values())

        # Calculate quality statistics
        qualities = [e.quality for e in self.entries.values()]
        avg_quality = sum(qualities) / len(qualities) if qualities else 0
        high_quality_count = len([q for q in qualities if q >= 0.7])

        return {
            "entry_count": len(self.entries),
            "summary_count": len(self.summaries),
            "total_tokens": total_tokens,
            "tokens_saved": total_saved,
            "compression_ratio": f"{(total_saved / (total_tokens + total_saved) * 100):.1f}%"
            if total_tokens + total_saved > 0
            else "0%",
            "storage_size_mb": sum(len(e.compressed) for e in self.entries.values())
            / (1024 * 1024),
            "avg_quality": f"{avg_quality:.2f}",
            "high_quality_entries": high_quality_count,
            "low_quality_entries": len(qualities) - high_quality_count,
        }

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        Args:
            text: Text to count

        Returns:
            Token count
        """
        if self.encoder:
            return len(self.encoder.encode(text))
        # Fallback: rough estimate
        return len(text) // 4

    def _recency_score(self, timestamp_str: str) -> float:
        """Calculate recency bonus based on entry age.

        Args:
            timestamp_str: ISO format timestamp string

        Returns:
            Recency score (1.0 = now, 0.0 = 24h+ ago)
        """
        from datetime import datetime

        try:
            from dateutil.parser import parse

            timestamp = parse(timestamp_str)
        except (ImportError, ValueError):
            # Fallback: assume recent if parsing fails
            return 0.5

        age_hours = (datetime.now(timestamp.tzinfo) - timestamp).total_seconds() / 3600
        # Linear decay: 1.0 at 0 hours, 0.0 at 24+ hours
        return max(0.0, 1.0 - (age_hours / 24))

    def _calculate_quality(self, content: str) -> float:
        """Calculate content quality score (0-1).

        Args:
            content: Content to score

        Returns:
            Quality score between 0 and 1
        """
        score = 1.0
        content_lower = content.lower()

        # Penalize very short content
        if len(content) < 50:
            score *= 0.5

        # Penalize error messages (but they can still be important)
        if "error" in content_lower or "failed" in content_lower:
            score *= 0.7

        # Reward longer, detailed content
        if len(content) > 200:
            score *= 1.2
        if len(content) > 500:
            score *= 1.3

        # Reward code blocks (indicates technical content)
        if "```" in content:
            score *= 1.3

        # Reward content with questions (important for context)
        if "?" in content and len(content) > 100:
            score *= 1.2

        # Penalize very generic responses
        generic_phrases = ["you're welcome", "let me know", "happy to help"]
        if any(phrase in content_lower for phrase in generic_phrases):
            score *= 0.6

        # Reward technical content (has specific terms)
        technical_indicators = ["function", "class", "method", "error", "bug", "fix", "implement"]
        if any(term in content_lower for term in technical_indicators):
            score *= 1.2

        # Reward substantial token count
        token_count = self.count_tokens(content)
        if token_count > 100:
            score *= 1.1

        return min(score, 1.0)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (for backward compatibility).

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return self.count_tokens(text)

    def _hash_content(self, content: str) -> str:
        """Generate hash for content deduplication.

        Args:
            content: Content to hash

        Returns:
            Content hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _generate_id(self) -> str:
        """Generate unique ID.

        Returns:
            Unique ID string
        """
        return str(uuid.uuid4())[:8]

    def _save_entry(self, entry: ContextEntry):
        """Save entry to disk.

        Args:
            entry: Entry to save
        """
        entry_file = self.storage_path / f"{entry.id}.json"

        # Don't serialize compressed content in JSON
        entry_dict = asdict(entry)
        entry_dict["compressed"] = None

        entry_file.write_text(json.dumps(entry_dict, indent=2))

        # Save compressed separately
        compressed_file = self.storage_path / f"{entry.id}.zlib"
        compressed_file.write_bytes(entry.compressed)

    def _save_summary(self, summary: ContextSummary):
        """Save summary to disk.

        Args:
            summary: Summary to save
        """
        summary_file = self.storage_path / f"summary_{summary.id}.json"
        summary_file.write_text(json.dumps(asdict(summary), indent=2))

    def _load_context(self):
        """Load context from disk."""
        if not self.storage_path.exists():
            return

        # Load entries
        for entry_file in self.storage_path.glob("*.json"):
            if entry_file.name.startswith("summary_"):
                continue

            try:
                entry_dict = json.loads(entry_file.read_text())

                # Load compressed data
                compressed_file = self.storage_path / f"{entry_dict['id']}.zlib"
                if compressed_file.exists():
                    entry_dict["compressed"] = compressed_file.read_bytes()
                else:
                    entry_dict["compressed"] = b""

                entry = ContextEntry(**entry_dict)
                self.entries[entry.id] = entry
                self.dedup_index[entry.hash] = entry.id
            except Exception as e:
                logger.warning("Error loading entry %s: %s", entry_file, e)

    def _save_context(self):
        """Save all context entries to disk."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        for entry_id, entry in self.entries.items():
            entry_file = self.storage_path / f"{entry_id}.json"
            entry_dict = {
                "id": entry.id,
                "content": entry.content,
                "agent": entry.agent,
                "timestamp": entry.timestamp,
                "references": entry.references,
                "token_estimate": entry.token_estimate,
                "hash": entry.hash,
                "quality": entry.quality,
                "metadata": entry.metadata or {},
            }
            entry_file.write_text(json.dumps(entry_dict, indent=2))

            # Save compressed data separately
            if entry.compressed:
                compressed_file = self.storage_path / f"{entry_id}.zlib"
                compressed_file.write_bytes(entry.compressed)
            else:
                # Write empty bytes for None compressed
                compressed_file = self.storage_path / f"{entry_id}.zlib"
                compressed_file.write_bytes(b"")

        # Load summaries
        for summary_file in self.storage_path.glob("summary_*.json"):
            try:
                summary_dict = json.loads(summary_file.read_text())
                summary = ContextSummary(**summary_dict)
                self.summaries[summary.id] = summary
            except Exception as e:
                logger.warning("Error loading summary %s: %s", summary_file, e)
