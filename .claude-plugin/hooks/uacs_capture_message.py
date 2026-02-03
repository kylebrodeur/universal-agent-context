#!/usr/bin/env python3
"""
UACS UserPromptSubmit Hook - Message Capture (v0.3.0)

Captures user messages using semantic API for perfect conversation tracking.

Hook Type: UserPromptSubmit (async)
Fires: On every user prompt
Matcher: None (fires for all prompts)

v0.3.0: Uses add_user_message() from semantic API
"""

import json
import sys
from pathlib import Path


def capture_user_message(hook_input: dict) -> dict:
    """Capture user messages using semantic API."""
    try:
        from uacs import UACS

        # Get hook inputs
        prompt = hook_input.get("prompt", "")
        session_id = hook_input.get("session_id", "unknown")
        project_dir = hook_input.get("cwd", ".")
        turn = hook_input.get("turn", 1)

        if not prompt or len(prompt.strip()) < 3:
            return {"continue": True, "message": "UACS: Prompt too short to store"}

        # Initialize UACS
        uacs = UACS(project_path=Path(project_dir))

        # Extract topics using heuristics
        topics = extract_topics_heuristic(prompt)

        # Use semantic API to store user message
        uacs.add_user_message(
            content=prompt,
            turn=turn,
            session_id=session_id,
            topics=topics,
        )

        return {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "message": f"UACS v0.3.0: Captured message with {len(topics)} topics",
            }
        }

    except Exception as e:
        # Non-blocking - don't interrupt user's prompt
        return {
            "continue": True,
            "error": str(e),
            "message": f"UACS: Capture failed (non-critical): {type(e).__name__}",
        }


def extract_topics_heuristic(prompt: str) -> list[str]:
    """Extract topics from prompt using keyword matching."""
    topics = set()
    prompt_lower = prompt.lower()

    # Topic keywords
    topic_keywords = {
        "testing": ["test", "pytest", "unittest", "jest", "spec", "coverage"],
        "security": ["security", "auth", "password", "encryption", "vulnerability"],
        "performance": ["performance", "optimize", "slow", "cache", "speed"],
        "bug-fix": ["bug", "error", "exception", "fix", "crash"],
        "feature": ["feature", "implement", "add", "create"],
        "documentation": ["document", "readme", "docs", "comment"],
        "deployment": ["deploy", "docker", "kubernetes", "production"],
        "database": ["database", "sql", "query", "migration"],
        "api": ["api", "endpoint", "rest", "graphql"],
        "frontend": ["react", "vue", "component", "ui"],
        "backend": ["server", "backend", "service"],
        "refactoring": ["refactor", "clean", "reorganize"],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            topics.add(topic)

    # Default if no topics found
    if not topics:
        topics.add("general")

    return list(topics)[:4]  # Limit to 4 topics


def main():
    """Main entry point for UserPromptSubmit hook."""
    try:
        input_data = json.load(sys.stdin)
        result = capture_user_message(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "continue": True,
            "error": str(e),
            "message": "UACS: Message capture hook failed (non-blocking)",
        }
        print(json.dumps(error_result))
        sys.exit(0)


if __name__ == "__main__":
    main()
