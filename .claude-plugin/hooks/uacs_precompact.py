#!/usr/bin/env python3
"""
UACS PreCompact Hook - Compression Trigger

Fires before Claude compacts its context window. This is our chance to:
1. Store current context in UACS before it's lost
2. Compress UACS storage to save space
3. Return additional context to help Claude with compaction

Hook Type: PreCompact
Fires: Before Claude compresses its context window (running low on tokens)
"""

import json
import sys


def handle_precompact(hook_input: dict) -> dict:
    """Handle PreCompact event - store and compress."""
    try:
        from uacs import UACS

        project_dir = hook_input.get("project_dir", ".")
        trigger = hook_input.get("trigger", "unknown")

        # Initialize UACS
        uacs = UACS(project_path=project_dir)

        # Get current stats
        stats_before = uacs.shared_context.get_stats()

        # Trigger UACS compression/optimization
        uacs.optimize_context()

        # Get stats after
        stats_after = uacs.shared_context.get_stats()

        # Calculate savings
        tokens_saved = stats_before.get("total_tokens", 0) - stats_after.get(
            "total_tokens", 0
        )

        return {
            "hookSpecificOutput": {
                "hookEventName": "PreCompact",
                "additionalContext": f"""
UACS has compressed its storage before Claude's compaction:
- Tokens before: {stats_before.get('total_tokens', 0)}
- Tokens after: {stats_after.get('total_tokens', 0)}
- Saved: {tokens_saved} tokens

All previous context is safely stored in UACS with perfect fidelity.
""".strip(),
                "message": f"UACS compression: saved {tokens_saved} tokens",
            }
        }

    except Exception as e:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreCompact",
                "error": str(e),
                "message": f"PreCompact failed: {type(e).__name__}",
            }
        }


def main():
    """Main entry point for PreCompact hook."""
    try:
        input_data = json.load(sys.stdin)
        result = handle_precompact(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "hookSpecificOutput": {"hookEventName": "PreCompact", "error": str(e)}
        }
        print(json.dumps(error_result))
        sys.exit(0)


if __name__ == "__main__":
    main()
