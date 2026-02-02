"""Data models for trace visualization.

Provides Session and Event models for LangSmith-style trace visualization.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of events in a session."""

    USER_PROMPT = "user_prompt"
    ASSISTANT_RESPONSE = "assistant_response"
    TOOL_USE = "tool_use"
    COMPRESSION = "compression"
    ERROR = "error"


class CompressionTrigger(str, Enum):
    """Types of compression triggers."""

    EARLY_COMPRESSION = "early_compression"  # Proactive at 50%
    PRECOMPACT = "precompact"  # Emergency before Claude compacts
    SESSIONEND = "sessionend"  # Final compression


class Event(BaseModel):
    """Single event in a session (tool use, prompt, compression, etc.)."""

    event_id: str
    session_id: str
    type: EventType
    timestamp: str  # ISO format

    # Tool use fields
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    tool_response: str | None = None
    latency_ms: int | None = None

    # Content fields
    content: str | None = None  # For prompts/responses

    # Compression fields
    compression_trigger: CompressionTrigger | None = None
    compression_usage: str | None = None  # e.g., "52.3%"
    tokens_before: int | None = None
    tokens_after: int | None = None
    tokens_saved: int | None = None
    compression_ratio: str | None = None
    turns_archived: int | None = None

    # Common fields
    topics: list[str] = Field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_cumulative: int = 0
    quality: float = 0.8
    metadata: dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    """Claude Code session with full trace."""

    session_id: str
    started_at: str  # ISO format
    ended_at: str | None = None
    duration_seconds: int | None = None

    # Counts
    turn_count: int = 0
    event_count: int = 0

    # Topics
    topics: list[str] = Field(default_factory=list)

    # Tokens
    total_tokens: int = 0
    compressed_tokens: int = 0
    compression_savings: int = 0
    compression_percentage: str = "0%"

    # Quality
    quality_avg: float = 0.8

    # Source
    source: str = "claude-code"  # claude-code-posttooluse, claude-code-sessionend

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Events (optional, loaded on demand)
    events: list[Event] = Field(default_factory=list)


class SessionList(BaseModel):
    """Paginated list of sessions."""

    sessions: list[Session]
    total: int
    skip: int
    limit: int


class EventList(BaseModel):
    """Paginated list of events."""

    events: list[Event]
    total: int
    skip: int
    limit: int


class TokenAnalytics(BaseModel):
    """Token usage analytics."""

    total_tokens: int
    compressed_tokens: int
    savings: int
    savings_percentage: str
    avg_per_session: int
    sessions_count: int

    # Breakdown by type
    user_prompt_tokens: int = 0
    assistant_response_tokens: int = 0
    tool_use_tokens: int = 0

    # Trend data (list of daily totals)
    trend_dates: list[str] = Field(default_factory=list)
    trend_values: list[int] = Field(default_factory=list)


class CompressionAnalytics(BaseModel):
    """Compression events analytics."""

    early_compression_count: int = 0
    early_compression_avg_savings: int = 0
    precompact_count: int = 0
    precompact_avg_savings: int = 0
    sessionend_count: int = 0
    sessionend_avg_savings: int = 0

    compaction_prevention_rate: str = "0%"
    compaction_prevention_count: int = 0
    compaction_prevention_total: int = 0


class TopicCluster(BaseModel):
    """Topic cluster with session references."""

    topic: str
    count: int
    session_ids: list[str] = Field(default_factory=list)
    total_tokens: int = 0
    avg_quality: float = 0.8


class TopicAnalytics(BaseModel):
    """Topic distribution analytics."""

    clusters: list[TopicCluster]
    total_topics: int


class QualityAnalytics(BaseModel):
    """Quality distribution analytics."""

    average: float
    high_quality_count: int  # >= 0.8
    medium_quality_count: int  # 0.5-0.8
    low_quality_count: int  # < 0.5

    distribution: list[dict[str, Any]] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Search request with filters."""

    query: str
    filters: dict[str, Any] = Field(default_factory=dict)
    skip: int = 0
    limit: int = 50


class SearchResults(BaseModel):
    """Search results with sessions and events."""

    query: str
    sessions: list[Session] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    total_results: int
