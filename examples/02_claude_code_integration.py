#!/usr/bin/env python3
"""
Example 2: Claude Code Integration

Demonstrates how UACS v0.3.0 integrates with Claude Code through hooks:
- Automatic conversation tracking via UserPromptSubmit hook
- Real-time tool execution tracking via PostToolUse hook
- Knowledge extraction via SessionEnd hook

This shows the "killer use case" - zero-effort context capture!

Run: uv run python examples/02_claude_code_integration.py
"""

from pathlib import Path
from uacs import UACS


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def simulate_claude_code_session():
    """
    Simulate what happens during a real Claude Code session with hooks enabled.

    In reality, the hooks run automatically. This demonstrates what they capture.
    """

    demo_dir = Path(__file__).parent / ".demo_state"
    demo_dir.mkdir(exist_ok=True)
    uacs = UACS(project_path=demo_dir)

    session_id = "claude_code_session_042"

    print("Simulating Claude Code session...")
    print(f"Session ID: {session_id}\n")

    # ========================================================================
    # Hook 1: UserPromptSubmit (captures user messages automatically)
    # ========================================================================
    print("📝 UserPromptSubmit hook triggers:")
    print("   User types: 'Refactor the auth module to use dependency injection'\n")

    uacs.add_user_message(
        content="Refactor the auth module to use dependency injection",
        turn=1,
        session_id=session_id,
        topics=["refactoring", "architecture", "dependency-injection"]
    )
    print("   ✅ User message automatically captured by hook\n")

    # ========================================================================
    # Hook 2: PostToolUse (captures tool executions in real-time)
    # ========================================================================
    print("🔧 PostToolUse hook triggers after each tool:")
    print("   Claude uses Read tool on auth.py...")

    uacs.add_tool_use(
        tool_name="Read",
        tool_input={"file_path": "auth.py"},
        tool_response="[File contents: 450 lines]",
        turn=2,
        session_id=session_id,
        latency_ms=125,
        success=True
    )
    print("   ✅ Read tool execution captured\n")

    print("   Claude uses Edit tool to refactor...")
    uacs.add_tool_use(
        tool_name="Edit",
        tool_input={"file_path": "auth.py", "old_string": "...", "new_string": "..."},
        tool_response="Successfully refactored auth module",
        turn=3,
        session_id=session_id,
        latency_ms=850,
        success=True
    )
    print("   ✅ Edit tool execution captured\n")

    print("   Claude uses Bash tool to run tests...")
    uacs.add_tool_use(
        tool_name="Bash",
        tool_input={"command": "pytest tests/test_auth.py -v"},
        tool_response="All 12 tests passed",
        turn=4,
        session_id=session_id,
        latency_ms=2450,
        success=True
    )
    print("   ✅ Bash tool execution captured\n")

    # ========================================================================
    # Hook 3: SessionEnd (extracts knowledge from conversation)
    # ========================================================================
    print("🧠 SessionEnd hook triggers (extracts decisions and conventions):\n")

    # The hook would analyze the conversation and extract these automatically
    uacs.add_decision(
        question="How should we refactor the auth module?",
        decision="Use dependency injection pattern with FastAPI's Depends()",
        rationale="Makes testing easier, reduces coupling, follows FastAPI best practices",
        session_id=session_id,
        alternatives=[
            "Global singleton pattern (harder to test)",
            "Service locator (more magic, less explicit)"
        ],
        decided_by="assistant",
        topics=["refactoring", "architecture", "dependency-injection"]
    )
    print("   ✅ Extracted decision: Use dependency injection\n")

    uacs.add_convention(
        content="Auth dependencies should be injected via FastAPI Depends() for testability",
        topics=["architecture", "testing", "fastapi"],
        source_session=session_id,
        confidence=0.9
    )
    print("   ✅ Extracted convention: Use FastAPI Depends()\n")

    uacs.add_artifact(
        type="file",
        path="auth.py",
        description="Refactored authentication module using dependency injection",
        created_in_session=session_id,
        topics=["authentication", "refactoring"]
    )
    print("   ✅ Tracked artifact: auth.py\n")

    return uacs, session_id


def main():
    print_section("UACS v0.3.0: Claude Code Integration")

    print("This example shows how Claude Code hooks automatically capture:")
    print("  1. User messages (UserPromptSubmit hook)")
    print("  2. Tool executions (PostToolUse hook)")
    print("  3. Decisions & conventions (SessionEnd hook)")
    print()

    # Simulate a Claude Code session
    uacs, session_id = simulate_claude_code_session()

    # ========================================================================
    # Query the captured data
    # ========================================================================
    print_section("Querying Captured Data")

    print("🔍 Searching: 'how did we refactor the auth module?'\n")
    results = uacs.search(
        query="how did we refactor the auth module?",
        session_id=session_id,
        limit=5
    )

    print(f"   Found {len(results)} results from this session:\n")
    for i, result in enumerate(results, 1):
        # Handle both SearchResult types (embeddings.SearchResult and knowledge.SearchResult)
        result_type = result.metadata.get('type', 'unknown') if hasattr(result, 'metadata') and result.metadata else getattr(result, 'type', 'unknown')
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        preview = text[:100] + "..." if len(text) > 100 else text

        print(f"   {i}. [{result_type}] {similarity:.0f}% match")
        print(f"      {preview}\n")

    # ========================================================================
    # Show statistics
    # ========================================================================
    print_section("Session Statistics")

    stats = uacs.get_stats()

    print(f"📊 This session captured:")
    print(f"   User messages: {stats['semantic']['conversations']['total_user_messages']}")
    print(f"   Tool executions: {stats['semantic']['conversations']['total_tool_uses']}")
    print(f"   Decisions: {stats['semantic']['knowledge']['decisions']}")
    print(f"   Conventions: {stats['semantic']['knowledge']['conventions']}")
    print(f"   Artifacts: {stats['semantic']['knowledge']['artifacts']}")

    # ========================================================================
    # How to enable hooks
    # ========================================================================
    print_section("✅ How to Enable Hooks")

    print("To enable automatic capture in real Claude Code sessions:\n")

    print("1. Install the semantic plugin:")
    print("   cp .claude-plugin/plugin-semantic.json ~/.claude/plugin.json")
    print("   cp .claude-plugin/hooks/*.py ~/.claude/hooks/")
    print("   chmod +x ~/.claude/hooks/*.py\n")

    print("2. The hooks will automatically:")
    print("   ✅ Capture every user message you type")
    print("   ✅ Track every tool Claude uses (Read, Edit, Bash, etc.)")
    print("   ✅ Extract decisions and conventions at end of session")
    print("   ✅ Store everything with embeddings for semantic search\n")

    print("3. Query your session history:")
    print("   uacs search 'how did we implement X?'")
    print("   Or use the Web UI: uv run python examples/03_web_ui.py\n")

    print_section("✅ Complete!")

    print("You've learned:")
    print("  1. ✅ How UserPromptSubmit hook captures user messages")
    print("  2. ✅ How PostToolUse hook tracks tool executions in real-time")
    print("  3. ✅ How SessionEnd hook extracts knowledge automatically")
    print("  4. ✅ How to query captured session data")

    print("\n📖 Next steps:")
    print("  - Run 03_web_ui.py to visualize captured data")
    print("  - Install hooks: .claude-plugin/HOOKS_GUIDE.md")
    print("  - Run 04_search_and_knowledge.py for advanced patterns")

    print("\n📚 Documentation:")
    print("  - Hooks Guide: .claude-plugin/HOOKS_GUIDE.md")
    print("  - API Reference: docs/API_REFERENCE.md")
    print()


if __name__ == "__main__":
    main()
