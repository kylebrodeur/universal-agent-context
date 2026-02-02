"""Storage layer for trace visualization.

Stores sessions and events in JSONL format for simple, append-only storage.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from uacs.visualization.models import Event, EventType, Session, CompressionTrigger


class TraceStorage:
    """Storage for session traces."""

    def __init__(self, storage_path: Path):
        """Initialize trace storage.

        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = Path(storage_path)
        self.sessions_file = self.storage_path / "sessions.jsonl"
        self.events_file = self.storage_path / "events.jsonl"

        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Ensure files exist
        self.sessions_file.touch(exist_ok=True)
        self.events_file.touch(exist_ok=True)

    def add_session(self, session: Session) -> None:
        """Add or update a session.

        Args:
            session: Session to add
        """
        # Append to file (JSONL format)
        with open(self.sessions_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(session.model_dump()) + "\n")

    def add_event(self, event: Event) -> None:
        """Add an event.

        Args:
            event: Event to add
        """
        # Append to file (JSONL format)
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.model_dump()) + "\n")

    def get_session(self, session_id: str) -> Session | None:
        """Get a specific session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise
        """
        # Read sessions file and find by ID (latest version wins)
        session_data = None

        with open(self.sessions_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if data.get("session_id") == session_id:
                        session_data = data

        if session_data:
            return Session(**session_data)
        return None

    def get_sessions(
        self,
        skip: int = 0,
        limit: int = 20,
        topic: str | None = None,
        sort_by: str = "started_at",
        sort_desc: bool = True,
    ) -> tuple[list[Session], int]:
        """Get paginated list of sessions.

        Args:
            skip: Number of sessions to skip
            limit: Maximum sessions to return
            topic: Filter by topic
            sort_by: Field to sort by
            sort_desc: Sort in descending order

        Returns:
            Tuple of (sessions, total_count)
        """
        # Load all sessions (deduplicate by session_id, keeping latest)
        sessions_dict: dict[str, dict] = {}

        with open(self.sessions_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    sessions_dict[data["session_id"]] = data

        # Convert to Session objects
        sessions = [Session(**data) for data in sessions_dict.values()]

        # Filter by topic if specified
        if topic:
            sessions = [s for s in sessions if topic in s.topics]

        # Sort
        sessions.sort(
            key=lambda s: getattr(s, sort_by, ""), reverse=sort_desc
        )

        total = len(sessions)

        # Paginate
        sessions = sessions[skip : skip + limit]

        return sessions, total

    def get_events(
        self,
        session_id: str | None = None,
        event_type: EventType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Event], int]:
        """Get paginated list of events.

        Args:
            session_id: Filter by session ID
            event_type: Filter by event type
            skip: Number of events to skip
            limit: Maximum events to return

        Returns:
            Tuple of (events, total_count)
        """
        events = []

        with open(self.events_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)

                    # Apply filters
                    if session_id and data.get("session_id") != session_id:
                        continue
                    if event_type and data.get("type") != event_type:
                        continue

                    events.append(Event(**data))

        total = len(events)

        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)

        # Paginate
        events = events[skip : skip + limit]

        return events, total

    def get_event(self, event_id: str) -> Event | None:
        """Get a specific event by ID.

        Args:
            event_id: Event ID

        Returns:
            Event if found, None otherwise
        """
        with open(self.events_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if data.get("event_id") == event_id:
                        return Event(**data)
        return None

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 50,
    ) -> tuple[list[Session], list[Event]]:
        """Search across sessions and events.

        Args:
            query: Search query (searches in content, topics, tool names)
            filters: Additional filters (topics, date_from, date_to, quality_min)
            limit: Maximum results per type

        Returns:
            Tuple of (matching_sessions, matching_events)
        """
        query_lower = query.lower()
        filters = filters or {}

        # Search sessions
        matching_sessions = []
        sessions_dict: dict[str, dict] = {}

        with open(self.sessions_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    sessions_dict[data["session_id"]] = data

        for data in sessions_dict.values():
            # Check query match
            topics_str = " ".join(data.get("topics", [])).lower()
            metadata_str = json.dumps(data.get("metadata", {})).lower()

            if query_lower in topics_str or query_lower in metadata_str:
                # Apply filters
                if "topics" in filters and not any(
                    t in data.get("topics", []) for t in filters["topics"]
                ):
                    continue

                if "quality_min" in filters and data.get("quality_avg", 0) < filters["quality_min"]:
                    continue

                matching_sessions.append(Session(**data))

        # Search events
        matching_events = []

        with open(self.events_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)

                    # Check query match
                    content = data.get("content", "")
                    tool_name = data.get("tool_name", "")
                    topics_str = " ".join(data.get("topics", []))

                    searchable = f"{content} {tool_name} {topics_str}".lower()

                    if query_lower in searchable:
                        # Apply filters
                        if "topics" in filters and not any(
                            t in data.get("topics", []) for t in filters["topics"]
                        ):
                            continue

                        matching_events.append(Event(**data))

        # Sort by timestamp (newest first)
        matching_sessions.sort(key=lambda s: s.started_at, reverse=True)
        matching_events.sort(key=lambda e: e.timestamp, reverse=True)

        # Limit results
        matching_sessions = matching_sessions[:limit]
        matching_events = matching_events[:limit]

        return matching_sessions, matching_events

    def get_token_analytics(self, days: int = 30) -> dict[str, Any]:
        """Get token usage analytics.

        Args:
            days: Number of days to analyze

        Returns:
            Token analytics dictionary
        """
        # Load all sessions
        sessions_dict: dict[str, dict] = {}

        with open(self.sessions_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    sessions_dict[data["session_id"]] = data

        sessions = [Session(**data) for data in sessions_dict.values()]

        # Calculate totals
        total_tokens = sum(s.total_tokens for s in sessions)
        compressed_tokens = sum(s.compressed_tokens for s in sessions)
        savings = total_tokens - compressed_tokens
        avg_per_session = total_tokens // len(sessions) if sessions else 0

        return {
            "total_tokens": total_tokens,
            "compressed_tokens": compressed_tokens,
            "savings": savings,
            "savings_percentage": f"{(savings / total_tokens * 100):.1f}%" if total_tokens > 0 else "0%",
            "avg_per_session": avg_per_session,
            "sessions_count": len(sessions),
        }

    def get_topic_analytics(self) -> dict[str, Any]:
        """Get topic distribution analytics.

        Returns:
            Topic analytics dictionary
        """
        # Load all sessions
        sessions_dict: dict[str, dict] = {}

        with open(self.sessions_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    sessions_dict[data["session_id"]] = data

        # Count topics
        topic_counts: dict[str, int] = {}
        topic_sessions: dict[str, list[str]] = {}

        for session_id, data in sessions_dict.items():
            for topic in data.get("topics", []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
                if topic not in topic_sessions:
                    topic_sessions[topic] = []
                topic_sessions[topic].append(session_id)

        # Create clusters
        clusters = []
        for topic, count in topic_counts.items():
            clusters.append({
                "topic": topic,
                "count": count,
                "session_ids": topic_sessions[topic],
            })

        # Sort by count
        clusters.sort(key=lambda x: x["count"], reverse=True)

        return {
            "clusters": clusters,
            "total_topics": len(clusters),
        }

    def get_compression_analytics(self) -> dict[str, Any]:
        """Get compression events analytics.

        Returns:
            Compression analytics dictionary
        """
        # Count compression events by type
        early_count = 0
        early_savings_total = 0
        precompact_count = 0
        precompact_savings_total = 0
        sessionend_count = 0
        sessionend_savings_total = 0

        compaction_prevented = 0
        total_sessions = 0

        with open(self.events_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)

                    if data.get("type") == EventType.COMPRESSION:
                        trigger = data.get("compression_trigger")
                        savings = data.get("tokens_saved", 0)

                        if trigger == CompressionTrigger.EARLY_COMPRESSION:
                            early_count += 1
                            early_savings_total += savings
                        elif trigger == CompressionTrigger.PRECOMPACT:
                            precompact_count += 1
                            precompact_savings_total += savings
                        elif trigger == CompressionTrigger.SESSIONEND:
                            sessionend_count += 1
                            sessionend_savings_total += savings

                        # Check if compaction was prevented
                        if data.get("metadata", {}).get("prevented_compaction"):
                            compaction_prevented += 1

        # Count total sessions
        sessions_dict: dict[str, dict] = {}
        with open(self.sessions_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    sessions_dict[data["session_id"]] = data
        total_sessions = len(sessions_dict)

        return {
            "early_compression_count": early_count,
            "early_compression_avg_savings": early_savings_total // early_count if early_count > 0 else 0,
            "precompact_count": precompact_count,
            "precompact_avg_savings": precompact_savings_total // precompact_count if precompact_count > 0 else 0,
            "sessionend_count": sessionend_count,
            "sessionend_avg_savings": sessionend_savings_total // sessionend_count if sessionend_count > 0 else 0,
            "compaction_prevention_rate": f"{(compaction_prevented / total_sessions * 100):.1f}%" if total_sessions > 0 else "0%",
            "compaction_prevention_count": compaction_prevented,
            "compaction_prevention_total": total_sessions,
        }
