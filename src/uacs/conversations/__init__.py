"""Conversational message tracking for UACS.

This module provides structured conversation tracking with semantic embeddings,
replacing the generic add_to_context API with type-specific message methods.
"""

from uacs.conversations.models import (
    AssistantMessage,
    ToolUse,
    UserMessage,
)

__all__ = [
    "UserMessage",
    "AssistantMessage",
    "ToolUse",
]
