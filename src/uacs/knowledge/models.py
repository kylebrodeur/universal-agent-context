"""Pydantic models for UACS v0.3.0 Semantic Knowledge Layer.

This module defines structured data models for managing project knowledge including
conventions, decisions, learnings, artifacts, and search results.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Convention(BaseModel):
    """Project conventions and patterns discovered across sessions.

    Conventions represent coding standards, architectural patterns, and best practices
    that have been established or observed in the project.
    """

    content: str = Field(
        ...,
        description="Description of the convention or pattern",
        min_length=1,
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Topics or areas this convention applies to (e.g., 'testing', 'api')",
    )
    source_session: Optional[str] = Field(
        default=None,
        description="Session ID where this convention was established",
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence score for this convention (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this convention was created",
    )
    last_verified: Optional[datetime] = Field(
        default=None,
        description="When this convention was last verified or observed",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "Use Pydantic models for all data validation",
                    "topics": ["validation", "data-models"],
                    "source_session": "session_2024_01_15",
                    "confidence": 0.95,
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_verified": "2024-01-20T14:45:00Z",
                }
            ]
        }
    }


class Decision(BaseModel):
    """Architectural decisions made during development.

    Records important technical decisions, their rationale, and alternatives
    considered, following the Architecture Decision Record (ADR) pattern.
    """

    question: str = Field(
        ...,
        description="The question or problem that needed a decision",
        min_length=1,
    )
    decision: str = Field(
        ...,
        description="The decision that was made",
        min_length=1,
    )
    rationale: str = Field(
        ...,
        description="Why this decision was made",
        min_length=1,
    )
    alternatives: List[str] = Field(
        default_factory=list,
        description="Alternative approaches that were considered",
    )
    decided_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this decision was made",
    )
    decided_by: str = Field(
        ...,
        description="Model name or identifier that made the decision",
        min_length=1,
    )
    session_id: str = Field(
        ...,
        description="Session ID where this decision was made",
        min_length=1,
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Topics or areas this decision affects",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "How should we handle API authentication?",
                    "decision": "Use JWT tokens with refresh token rotation",
                    "rationale": "Provides good security balance and is stateless",
                    "alternatives": [
                        "Session-based authentication",
                        "OAuth2 only",
                        "API keys",
                    ],
                    "decided_at": "2024-01-15T10:30:00Z",
                    "decided_by": "claude-opus-4-5-20251101",
                    "session_id": "session_2024_01_15",
                    "topics": ["authentication", "api", "security"],
                }
            ]
        }
    }


class Learning(BaseModel):
    """Cross-session learnings and insights.

    Captures patterns and insights that emerge across multiple sessions,
    building institutional knowledge over time.
    """

    pattern: str = Field(
        ...,
        description="Description of the learned pattern or insight",
        min_length=1,
    )
    confidence: float = Field(
        ...,
        description="Confidence score for this learning (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    learned_from: List[str] = Field(
        default_factory=list,
        description="Session IDs where this pattern was observed",
    )
    category: str = Field(
        ...,
        description="Category of learning (e.g., 'performance', 'usability')",
        min_length=1,
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this learning was first recorded",
    )

    @field_validator("learned_from")
    @classmethod
    def validate_learned_from(cls, v: List[str]) -> List[str]:
        """Ensure learned_from is not empty for confidence tracking."""
        if not v:
            raise ValueError("Learning must be derived from at least one session")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "pattern": "Users prefer inline validation over submit-time validation",
                    "confidence": 0.85,
                    "learned_from": [
                        "session_2024_01_10",
                        "session_2024_01_12",
                        "session_2024_01_15",
                    ],
                    "category": "usability",
                    "created_at": "2024-01-15T10:30:00Z",
                }
            ]
        }
    }


class Artifact(BaseModel):
    """Code artifacts created or modified in sessions.

    Tracks important code artifacts like files, functions, classes, and their
    relationships to sessions and topics.
    """

    type: str = Field(
        ...,
        description="Type of artifact (file, function, class, module, etc.)",
        min_length=1,
    )
    path: str = Field(
        ...,
        description="Path or identifier for the artifact",
        min_length=1,
    )
    description: str = Field(
        ...,
        description="Human-readable description of what this artifact does",
        min_length=1,
    )
    created_in_session: str = Field(
        ...,
        description="Session ID where this artifact was created",
        min_length=1,
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Topics or areas this artifact relates to",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "class",
                    "path": "src/uacs/knowledge/models.py::Convention",
                    "description": "Pydantic model for project conventions",
                    "created_in_session": "session_2024_01_15",
                    "topics": ["knowledge", "data-models", "conventions"],
                }
            ]
        }
    }


class SearchResult(BaseModel):
    """Semantic search result from the knowledge layer.

    Represents a single result from semantic search across conventions,
    decisions, learnings, conversations, and artifacts.
    """

    type: str = Field(
        ...,
        description="Type of result (convention, decision, learning, conversation, artifact)",
        min_length=1,
    )
    content: str = Field(
        ...,
        description="The content or text of the search result",
        min_length=1,
    )
    relevance_score: float = Field(
        ...,
        description="Relevance score for this result (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    source_session: Optional[str] = Field(
        default=None,
        description="Session ID where this content originated",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata specific to the result type",
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is one of the known result types."""
        valid_types = {
            "convention",
            "decision",
            "learning",
            "conversation",
            "artifact",
        }
        if v not in valid_types:
            raise ValueError(
                f"Invalid result type: {v}. Must be one of {valid_types}"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "convention",
                    "content": "Use Pydantic models for all data validation",
                    "relevance_score": 0.92,
                    "source_session": "session_2024_01_15",
                    "metadata": {
                        "topics": ["validation", "data-models"],
                        "confidence": 0.95,
                    },
                }
            ]
        }
    }
