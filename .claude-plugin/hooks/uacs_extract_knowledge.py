#!/usr/bin/env python3
"""
UACS SessionEnd Hook - Knowledge Extraction (v0.3.0)

Extracts decisions, conventions, and learnings from the completed session.
Uses heuristics to identify decision points and patterns worth preserving.

Hook Type: SessionEnd (async)
Fires: When session ends (user exits, timeout, crash recovery)

v0.3.0: Uses semantic API (add_decision, add_convention, add_learning)
"""

import json
import re
import sys
from pathlib import Path


def extract_knowledge(hook_input: dict) -> dict:
    """Extract decisions, conventions, and learnings from session."""
    try:
        from uacs import UACS

        # Get hook inputs
        session_id = hook_input.get("session_id", "unknown")
        project_dir = hook_input.get("project_dir", ".")
        messages = hook_input.get("messages", [])

        if not messages:
            return {"continue": True, "message": "UACS: No messages to analyze"}

        # Initialize UACS
        uacs = UACS(project_path=Path(project_dir))

        # Extract knowledge from messages
        decisions_count = 0
        conventions_count = 0

        # Analyze assistant messages for decisions and conventions
        for i, msg in enumerate(messages):
            role = msg.get("role")
            content = msg.get("content", "")

            if role != "assistant":
                continue

            # Look for decision indicators
            decisions = extract_decisions_from_text(content)
            for decision_data in decisions:
                try:
                    uacs.add_decision(
                        question=decision_data["question"],
                        decision=decision_data["decision"],
                        rationale=decision_data["rationale"],
                        session_id=session_id,
                        alternatives=decision_data.get("alternatives", []),
                    )
                    decisions_count += 1
                except Exception:
                    pass  # Skip malformed decisions

            # Look for convention/pattern indicators
            conventions = extract_conventions_from_text(content)
            for convention_text in conventions:
                try:
                    uacs.add_convention(
                        content=convention_text,
                        source_session=session_id,
                        confidence=0.8,  # Heuristic extraction has lower confidence
                    )
                    conventions_count += 1
                except Exception:
                    pass  # Skip malformed conventions

        return {
            "continue": True,
            "message": f"UACS v0.3.0: Extracted {decisions_count} decisions, {conventions_count} conventions",
        }

    except Exception as e:
        return {
            "continue": True,
            "error": str(e),
            "message": f"UACS: Knowledge extraction failed (non-critical): {type(e).__name__}",
        }


def extract_decisions_from_text(text: str) -> list[dict]:
    """Extract decision points from assistant messages using heuristics.

    Looks for patterns like:
    - "We decided to use X because Y"
    - "I chose X over Y because Z"
    - "We'll use X since Y"
    """
    decisions = []

    # Pattern 1: "decided to use X because Y"
    decided_pattern = r"(?:decided|chose|selected|picked)\s+(?:to\s+)?(?:use\s+)?([^.!?]+?)\s+because\s+([^.!?]+)"
    for match in re.finditer(decided_pattern, text, re.IGNORECASE):
        decision_text = match.group(1).strip()
        rationale = match.group(2).strip()

        decisions.append({
            "question": f"What should we use?",
            "decision": decision_text,
            "rationale": rationale,
        })

    # Pattern 2: "We'll use X since Y"
    will_use_pattern = r"(?:we'll|we will|i'll|let's)\s+use\s+([^.!?]+?)\s+(?:since|as|given that)\s+([^.!?]+)"
    for match in re.finditer(will_use_pattern, text, re.IGNORECASE):
        decision_text = match.group(1).strip()
        rationale = match.group(2).strip()

        decisions.append({
            "question": f"What approach should we take?",
            "decision": decision_text,
            "rationale": rationale,
        })

    # Pattern 3: "X over Y because Z"
    over_pattern = r"(?:use|chose|prefer)\s+([^.!?]+?)\s+over\s+([^.!?]+?)\s+because\s+([^.!?]+)"
    for match in re.finditer(over_pattern, text, re.IGNORECASE):
        chosen = match.group(1).strip()
        alternative = match.group(2).strip()
        rationale = match.group(3).strip()

        decisions.append({
            "question": f"Which approach is better?",
            "decision": chosen,
            "rationale": rationale,
            "alternatives": [alternative],
        })

    return decisions


def extract_conventions_from_text(text: str) -> list[str]:
    """Extract conventions/patterns from assistant messages using heuristics.

    Looks for patterns like:
    - "We always X"
    - "The convention is to X"
    - "We should always X"
    - "Best practice is to X"
    """
    conventions = []

    # Pattern 1: "We always/should always/typically X"
    always_pattern = r"(?:we|you|the project)\s+(?:always|should always|typically|usually)\s+([^.!?]+)"
    for match in re.finditer(always_pattern, text, re.IGNORECASE):
        convention_text = match.group(1).strip()
        if len(convention_text) > 10 and len(convention_text) < 200:
            conventions.append(f"We {convention_text}")

    # Pattern 2: "The convention is to X"
    convention_pattern = r"(?:the\s+)?(?:convention|pattern|practice)\s+(?:is|here)\s+(?:to\s+)?([^.!?]+)"
    for match in re.finditer(convention_pattern, text, re.IGNORECASE):
        convention_text = match.group(1).strip()
        if len(convention_text) > 10 and len(convention_text) < 200:
            conventions.append(f"Convention: {convention_text}")

    # Pattern 3: "Best practice is to X"
    best_practice_pattern = r"best\s+practice\s+(?:is\s+)?(?:to\s+)?([^.!?]+)"
    for match in re.finditer(best_practice_pattern, text, re.IGNORECASE):
        convention_text = match.group(1).strip()
        if len(convention_text) > 10 and len(convention_text) < 200:
            conventions.append(f"Best practice: {convention_text}")

    return conventions


def main():
    """Main entry point for SessionEnd hook."""
    try:
        input_data = json.load(sys.stdin)
        result = extract_knowledge(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "continue": True,
            "error": str(e),
            "message": "UACS: Knowledge extraction hook failed (non-blocking)",
        }
        print(json.dumps(error_result))
        sys.exit(0)


if __name__ == "__main__":
    main()
