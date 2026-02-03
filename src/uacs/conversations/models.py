"""Data models for conversational messages in UACS.

These models represent structured conversation events: user prompts,
assistant responses, and tool executions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserMessage(BaseModel):
    """A user prompt/message in a conversation.

    Attributes:
        content: The user's prompt text
        turn: Turn number in the conversation (1-indexed)
        session_id: Session identifier
        topics: Optional topic tags for categorization
        timestamp: When the message was sent
    """

    content: str = Field(..., min_length=1, description="User prompt text")
    turn: int = Field(..., ge=1, description="Turn number (1-indexed)")
    session_id: str = Field(..., min_length=1, description="Session identifier")
    topics: List[str] = Field(default_factory=list, description="Topic tags")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Message timestamp"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "Help me implement JWT authentication",
                    "turn": 1,
                    "session_id": "session_abc123",
                    "topics": ["security", "auth"],
                }
            ]
        }
    }


class AssistantMessage(BaseModel):
    """An assistant response in a conversation.

    Attributes:
        content: The assistant's response text
        turn: Turn number in the conversation (1-indexed)
        session_id: Session identifier
        tokens_in: Number of input tokens (prompt)
        tokens_out: Number of output tokens (response)
        model: Model identifier (e.g., "claude-sonnet-4")
        timestamp: When the response was generated
    """

    content: str = Field(..., min_length=1, description="Assistant response text")
    turn: int = Field(..., ge=1, description="Turn number (1-indexed)")
    session_id: str = Field(..., min_length=1, description="Session identifier")
    tokens_in: Optional[int] = Field(None, ge=0, description="Input token count")
    tokens_out: Optional[int] = Field(None, ge=0, description="Output token count")
    model: Optional[str] = Field(None, description="Model identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "I'll help you implement JWT. First, let's...",
                    "turn": 1,
                    "session_id": "session_abc123",
                    "tokens_in": 42,
                    "tokens_out": 156,
                    "model": "claude-sonnet-4",
                }
            ]
        }
    }


class ToolUse(BaseModel):
    """A tool execution in a conversation.

    Attributes:
        tool_name: Name of the tool executed
        tool_input: Input parameters to the tool
        tool_response: Tool execution result
        turn: Turn number in the conversation (1-indexed)
        session_id: Session identifier
        latency_ms: Tool execution time in milliseconds
        success: Whether tool execution succeeded
        timestamp: When the tool was executed
    """

    tool_name: str = Field(..., min_length=1, description="Tool name")
    tool_input: Dict[str, Any] = Field(
        default_factory=dict, description="Tool input parameters"
    )
    tool_response: Optional[str] = Field(None, description="Tool response")
    turn: int = Field(..., ge=1, description="Turn number (1-indexed)")
    session_id: str = Field(..., min_length=1, description="Session identifier")
    latency_ms: Optional[int] = Field(None, ge=0, description="Execution time (ms)")
    success: bool = Field(True, description="Whether execution succeeded")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Execution timestamp"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tool_name": "Edit",
                    "tool_input": {"file": "auth.py", "changes": "..."},
                    "tool_response": "Successfully edited auth.py",
                    "turn": 2,
                    "session_id": "session_abc123",
                    "latency_ms": 2300,
                    "success": True,
                }
            ]
        }
    }
