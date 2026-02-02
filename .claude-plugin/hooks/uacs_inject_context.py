#!/usr/bin/env python3
"""
UACS SessionStart Hook - Context Injection

When resuming a session, automatically inject relevant past context
from UACS into Claude's initial context.

Hook Type: SessionStart
Fires: When session starts (especially on resume)
Matcher: "resume" - only fires when resuming, not new sessions
"""

import json
import sys


def inject_context_on_resume(hook_input: dict) -> dict:
    """Inject UACS context when resuming a session."""
    try:
        from uacs import UACS

        # Get hook inputs
        source = hook_input.get("source", "")
        project_dir = hook_input.get("cwd", ".")

        # Only inject on resume (not new sessions)
        if source != "resume":
            return {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "message": "New session - no context injection needed"
                }
            }

        # Initialize UACS
        uacs = UACS(project_path=project_dir)

        # Get recent context (last 5 sessions or 2000 tokens)
        recent_context = uacs.shared_context.get_compressed_context(
            max_tokens=2000, min_quality=0.7
        )

        if not recent_context or len(recent_context.strip()) == 0:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "message": "No previous context found"
                }
            }

        # Get topics from recent conversations
        topics = set()
        for entry in list(uacs.shared_context.entries.values())[-10:]:
            if entry.topics:
                topics.update(entry.topics)

        # Format context for injection
        context_summary = f"""
## Previous Session Context (from UACS)

You have access to context from previous sessions in this project:

**Recent Topics:** {', '.join(sorted(topics)) if topics else 'None'}

**Recent Conversations:**
{recent_context[:1000]}...

Use this context to maintain continuity. The user may reference previous discussions.
""".strip()

        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context_summary,
                "message": f"Injected {len(topics)} topics from previous sessions"
            }
        }

    except Exception as e:
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "error": str(e),
                "message": f"Context injection failed: {type(e).__name__}"
            }
        }


def main():
    """Main entry point for SessionStart hook."""
    try:
        input_data = json.load(sys.stdin)
        result = inject_context_on_resume(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "error": str(e)
            }
        }
        print(json.dumps(error_result))
        sys.exit(0)


if __name__ == "__main__":
    main()
