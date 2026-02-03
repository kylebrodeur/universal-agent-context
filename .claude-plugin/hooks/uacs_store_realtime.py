#!/usr/bin/env python3
"""
UACS PostToolUse Hook - Real-Time Storage (v0.3.0)

Fires after each tool execution to store conversation turns incrementally.
This is MORE RELIABLE than SessionEnd because it survives crashes.

Hook Type: PostToolUse (async)
Fires: After each Bash, Edit, Write, Read, etc.

v0.3.0: Updated to use semantic API (add_tool_use instead of add_to_context)
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def store_tool_use(hook_input: dict) -> dict:
    """Store tool usage in UACS incrementally using semantic API."""
    try:
        from uacs import UACS

        # Get hook inputs
        tool_name = hook_input.get("tool_name")
        tool_input_data = hook_input.get("tool_input", {})
        tool_response = hook_input.get("tool_response", "")
        session_id = hook_input.get("session_id", "unknown")
        project_dir = hook_input.get("project_dir", ".")
        turn = hook_input.get("turn", 0)
        latency_ms = hook_input.get("latency_ms")
        success = hook_input.get("success", True)

        # Only store meaningful tools
        if tool_name not in ["Bash", "Edit", "Write", "Read", "Grep", "Glob"]:
            return {"continue": True, "message": f"UACS: Skipped {tool_name}"}

        # Initialize UACS
        uacs = UACS(project_path=Path(project_dir))

        # Use new semantic API
        uacs.add_tool_use(
            tool_name=tool_name,
            tool_input=tool_input_data,
            tool_response=tool_response[:1000] if tool_response else None,  # Truncate long responses
            turn=turn,
            session_id=session_id,
            latency_ms=latency_ms,
            success=success,
        )

        return {
            "continue": True,
            "message": f"UACS v0.3.0: Stored {tool_name} (semantic API)",
        }

    except Exception as e:
        return {
            "continue": True,
            "error": str(e),
            "message": f"UACS: Storage failed (non-critical): {type(e).__name__}",
        }


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
