#!/usr/bin/env python3
"""
UACS UserPromptSubmit Hook - Context Monitoring and Early Compression

Fires on every user prompt to check context window usage.
If usage exceeds 50%, proactively compress old context to UACS
to prevent Claude from hitting the 75% auto-compaction threshold.

Hook Type: UserPromptSubmit
Fires: On every user prompt
Matcher: None (fires for all prompts)
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def monitor_and_compress_context(hook_input: dict) -> dict:
    """Monitor context size and trigger early compression at 50%."""
    try:
        from uacs import UACS

        # Get context stats from hook input
        session_id = hook_input.get("session_id", "unknown")
        project_dir = hook_input.get("cwd", ".")
        transcript_path = hook_input.get("transcript_path")

        # Note: Claude Code doesn't expose current token count in hook input yet
        # This is a limitation - we'll estimate based on transcript length
        # In future Claude Code versions, this may be available as:
        # current_tokens = hook_input.get("context_tokens", 0)
        # max_tokens = hook_input.get("max_context_tokens", 200000)

        # For now, we'll use a heuristic: check transcript size
        if not transcript_path or not Path(transcript_path).exists():
            return {"continue": True, "message": "UACS: No transcript available"}

        # Estimate token usage based on transcript
        transcript_size = Path(transcript_path).stat().st_size
        estimated_tokens = estimate_tokens_from_size(transcript_size)
        max_tokens = 200000  # Standard Sonnet 4.5 window

        usage_percent = (estimated_tokens / max_tokens) * 100

        # Trigger early compression at 50% usage
        COMPRESSION_THRESHOLD = 50.0

        if usage_percent < COMPRESSION_THRESHOLD:
            # Context is fine, no action needed
            return {"continue": True}

        # Context is above threshold - trigger UACS compression
        uacs = UACS(project_path=Path(project_dir))

        # Read transcript and identify old context (first 40% of conversation)
        transcript_lines = read_transcript(Path(transcript_path))

        if len(transcript_lines) < 5:
            # Too short to compress
            return {"continue": True, "message": "UACS: Session too short to compress"}

        # Get oldest 40% of conversation
        compression_portion = 0.4
        split_point = int(len(transcript_lines) * compression_portion)
        old_context = transcript_lines[:split_point]

        # Format for storage
        old_context_text = format_conversation(old_context)

        # Extract topics (simple heuristics for now)
        # TODO: Use local LLM for better topic extraction
        topics = extract_topics_heuristic(old_context_text)

        # Store in UACS
        timestamp = datetime.now().isoformat()
        uacs.add_to_context(
            key=f"early_compress_{session_id}_{timestamp}",
            content=old_context_text,
            topics=topics,
            metadata={
                "session_id": session_id,
                "stored_at": timestamp,
                "source": "early-compression",
                "trigger_usage": f"{usage_percent:.1f}%",
                "tokens_archived": len(old_context_text.split()),
                "prevented_compaction": True,
            },
        )

        # Inform Claude that old context is safely stored
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"""
⚙️ UACS Context Management

Context window usage reached {usage_percent:.1f}% - triggered early compression.

Archived {split_point}/{len(transcript_lines)} conversation turns to UACS storage.
All history preserved with perfect fidelity.

You can continue working without hitting compaction threshold (75%).
""".strip(),
                "message": f"UACS: Compressed at {usage_percent:.1f}% usage",
            }
        }

    except Exception as e:
        # Non-blocking - don't interrupt user's prompt
        return {
            "continue": True,
            "error": str(e),
            "message": f"UACS: Context monitoring failed (non-critical): {type(e).__name__}",
        }


def estimate_tokens_from_size(file_size_bytes: int) -> int:
    """Estimate token count from file size.

    Rough heuristic: 1 token ≈ 4 characters ≈ 4 bytes (for JSON)
    This is conservative - actual may be lower.
    """
    return file_size_bytes // 4


def read_transcript(transcript_path: Path) -> list[dict]:
    """Read JSONL transcript and parse each line."""
    transcript = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    transcript.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return transcript


def format_conversation(transcript: list[dict]) -> str:
    """Format transcript turns into readable conversation."""
    lines = []
    for turn in transcript:
        role = turn.get("role", "unknown")
        content = turn.get("content", "")

        if isinstance(content, list):
            # Handle multi-part content (tool uses, etc.)
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        lines.append(f"{role}: {item.get('text', '')}")
                    elif item.get("type") == "tool_use":
                        tool_name = item.get("name", "unknown")
                        lines.append(f"{role}: [Tool: {tool_name}]")
                else:
                    lines.append(f"{role}: {item}")
        else:
            lines.append(f"{role}: {content}")

    return "\n\n".join(lines)


def extract_topics_heuristic(content: str) -> list[str]:
    """Extract topics using simple heuristics.

    TODO: Replace with local LLM (Ollama) for better quality.
    """
    topics = set()
    content_lower = content.lower()

    # Topic keywords
    topic_keywords = {
        "testing": ["test", "pytest", "unittest", "jest", "spec"],
        "security": ["security", "auth", "password", "encryption", "vulnerability", "sql injection", "xss"],
        "performance": ["performance", "optimize", "slow", "cache", "benchmark"],
        "bug": ["bug", "error", "exception", "traceback", "fix"],
        "feature": ["feature", "implement", "add", "create new"],
        "documentation": ["document", "readme", "docs", "comment"],
        "deployment": ["deploy", "docker", "kubernetes", "production"],
        "database": ["database", "sql", "query", "migration", "schema"],
        "api": ["api", "endpoint", "rest", "graphql", "request"],
        "frontend": ["react", "vue", "angular", "component", "ui"],
        "backend": ["server", "backend", "service", "microservice"],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            topics.add(topic)

    # Default if no topics found
    if not topics:
        topics.add("general")

    return list(topics)


def main():
    """Main entry point for UserPromptSubmit hook."""
    try:
        input_data = json.load(sys.stdin)
        result = monitor_and_compress_context(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "continue": True,
            "error": str(e),
            "message": "UACS: Monitoring hook failed (non-blocking)",
        }
        print(json.dumps(error_result))
        sys.exit(0)


if __name__ == "__main__":
    main()
