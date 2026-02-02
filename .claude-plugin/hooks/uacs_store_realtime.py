#!/usr/bin/env python3
"""
UACS PostToolUse Hook - Real-Time Storage

Fires after each tool execution to store conversation turns incrementally.
This is MORE RELIABLE than SessionEnd because it survives crashes.

Hook Type: PostToolUse (async)
Fires: After each Bash, Edit, Write, Read, etc.
"""

import json
import sys
from datetime import datetime


def store_tool_use(hook_input: dict) -> dict:
    """Store tool usage in UACS incrementally."""
    try:
        from uacs import UACS

        # Get hook inputs
        tool_name = hook_input.get("tool_name")
        tool_input = hook_input.get("tool_input", {})
        tool_response = hook_input.get("tool_response", "")
        session_id = hook_input.get("session_id", "unknown")
        project_dir = hook_input.get("project_dir", ".")

        # Only store meaningful tools
        if tool_name not in ["Bash", "Edit", "Write", "Read", "Grep", "Glob"]:
            return {"continue": True, "message": f"UACS: Skipped {tool_name}"}

        # Initialize UACS
        uacs = UACS(project_path=project_dir)

        # Format content
        content_parts = [f"Tool: {tool_name}"]

        # Add tool input
        if isinstance(tool_input, dict):
            if "command" in tool_input:
                content_parts.append(f"Command: {tool_input['command']}")
            if "file_path" in tool_input:
                content_parts.append(f"File: {tool_input['file_path']}")
            if "pattern" in tool_input:
                content_parts.append(f"Pattern: {tool_input['pattern']}")

        # Add response preview (truncated)
        if tool_response:
            preview = str(tool_response)[:500]
            if len(str(tool_response)) > 500:
                preview += "... (truncated)"
            content_parts.append(f"Result: {preview}")

        content = "\n".join(content_parts)

        # Extract topics from tool usage
        topics = extract_topics_from_tool(tool_name, tool_input)

        # Store incrementally
        uacs.add_to_context(
            key=f"tool_{session_id}_{datetime.now().timestamp()}",
            content=content,
            topics=topics,
            metadata={
                "session_id": session_id,
                "tool_name": tool_name,
                "stored_at": datetime.now().isoformat(),
                "source": "claude-code-posttooluse",
                "incremental": True,
            },
        )

        return {
            "continue": True,
            "message": f"UACS: Stored {tool_name} (incremental)",
        }

    except Exception as e:
        return {
            "continue": True,
            "error": str(e),
            "message": f"UACS: Storage failed (non-critical): {type(e).__name__}",
        }


def extract_topics_from_tool(tool_name: str, tool_input: dict) -> list[str]:
    """Extract topics based on tool usage patterns."""
    topics = set()

    # File operations
    if tool_name in ["Edit", "Write", "Read"]:
        file_path = tool_input.get("file_path", "")
        if "test" in file_path:
            topics.add("testing")
        if ".md" in file_path or "README" in file_path:
            topics.add("documentation")
        if "security" in file_path or "auth" in file_path:
            topics.add("security")

    # Command execution
    if tool_name == "Bash":
        command = tool_input.get("command", "").lower()
        if any(kw in command for kw in ["test", "pytest", "npm test"]):
            topics.add("testing")
        if any(kw in command for kw in ["git", "commit", "push"]):
            topics.add("version-control")
        if any(kw in command for kw in ["deploy", "docker", "build"]):
            topics.add("deployment")
        if any(kw in command for kw in ["npm", "pip", "install"]):
            topics.add("dependencies")

    # Search operations
    if tool_name in ["Grep", "Glob"]:
        pattern = tool_input.get("pattern", "").lower()
        if any(kw in pattern for kw in ["test", "spec"]):
            topics.add("testing")
        if any(kw in pattern for kw in ["security", "auth", "password"]):
            topics.add("security")

    # Default
    if not topics:
        topics.add("general")

    return list(topics)


def main():
    """Main entry point for PostToolUse hook."""
    try:
        input_data = json.load(sys.stdin)
        result = store_tool_use(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "continue": True,
            "error": str(e),
            "message": "UACS: Critical error (non-blocking)",
        }
        print(json.dumps(error_result))
        sys.exit(0)


if __name__ == "__main__":
    main()
