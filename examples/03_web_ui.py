#!/usr/bin/env python3
"""
Example 3: Web UI Visualization

Demonstrates how to:
- Populate UACS with sample data
- Start the FastAPI backend server
- Start the Next.js frontend
- Explore data in the Web UI

This shows the modern Next.js Web UI for browsing conversations and knowledge!

Run: uv run python examples/03_web_ui.py
"""

from pathlib import Path
from uacs import UACS


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def populate_sample_data():
    """Populate UACS with rich sample data for Web UI demonstration."""

    demo_dir = Path(__file__).parent / ".demo_state"
    demo_dir.mkdir(exist_ok=True)
    uacs = UACS(project_path=demo_dir)

    print("📝 Populating sample data for Web UI...\n")

    # ========================================================================
    # Session 1: Authentication Implementation
    # ========================================================================
    session1 = "auth_implementation_001"

    # Conversation
    uacs.add_user_message(
        content="Help me implement JWT authentication for my FastAPI app",
        turn=1,
        session_id=session1,
        topics=["authentication", "jwt", "fastapi"]
    )

    uacs.add_assistant_message(
        content="I'll help you implement JWT authentication using PyJWT. We'll use RS256 signing for better security.",
        turn=1,
        session_id=session1,
        tokens_in=45,
        tokens_out=120
    )

    uacs.add_tool_use(
        tool_name="Write",
        tool_input={"file_path": "auth/jwt.py"},
        tool_response="Created JWT implementation",
        turn=2,
        session_id=session1,
        latency_ms=350,
        success=True
    )

    # Knowledge
    uacs.add_decision(
        question="Which JWT signing algorithm should we use?",
        decision="RS256 (asymmetric)",
        rationale="More secure for production, easier key rotation, private key stays server-side",
        session_id=session1,
        alternatives=["HS256 (symmetric, simpler but less secure)", "ES256 (elliptic curve, overkill)"],
        topics=["security", "jwt"]
    )

    uacs.add_convention(
        content="JWT tokens expire after 15 minutes, use refresh tokens for longer sessions",
        topics=["security", "jwt"],
        source_session=session1,
        confidence=1.0
    )

    # ========================================================================
    # Session 2: Database Schema Design
    # ========================================================================
    session2 = "database_schema_002"

    uacs.add_user_message(
        content="Design a database schema for user management with roles and permissions",
        turn=1,
        session_id=session2,
        topics=["database", "schema", "users"]
    )

    uacs.add_assistant_message(
        content="I'll design a flexible RBAC schema with users, roles, permissions, and junction tables.",
        turn=1,
        session_id=session2,
        tokens_in=52,
        tokens_out=180
    )

    uacs.add_tool_use(
        tool_name="Write",
        tool_input={"file_path": "models/user.py"},
        tool_response="Created user model with RBAC",
        turn=2,
        session_id=session2,
        latency_ms=425,
        success=True
    )

    uacs.add_decision(
        question="Should we use role-based or attribute-based access control?",
        decision="Role-Based Access Control (RBAC)",
        rationale="Simpler to implement and maintain, sufficient for most use cases",
        session_id=session2,
        alternatives=["ABAC (more complex, overkill)", "Simple permissions (not flexible enough)"],
        topics=["database", "security", "rbac"]
    )

    uacs.add_artifact(
        type="file",
        path="models/user.py",
        description="User model with RBAC support - roles, permissions, and junction tables",
        created_in_session=session2,
        topics=["database", "models"]
    )

    # ========================================================================
    # Session 3: API Rate Limiting
    # ========================================================================
    session3 = "rate_limiting_003"

    uacs.add_user_message(
        content="Add rate limiting to our API endpoints",
        turn=1,
        session_id=session3,
        topics=["api", "rate-limiting", "security"]
    )

    uacs.add_assistant_message(
        content="I'll implement rate limiting using slowapi (FastAPI integration for slowapi). We'll use Redis for distributed rate limiting.",
        turn=1,
        session_id=session3,
        tokens_in=38,
        tokens_out=95
    )

    uacs.add_tool_use(
        tool_name="Edit",
        tool_input={"file_path": "main.py"},
        tool_response="Added rate limiting middleware",
        turn=2,
        session_id=session3,
        latency_ms=290,
        success=True
    )

    uacs.add_learning(
        pattern="API rate limiting should be per-user, not per-IP, to prevent bypass via proxies",
        learned_from=[session3],
        category="security_best_practice",
        confidence=0.95
    )

    uacs.add_convention(
        content="Rate limit: 100 requests/minute for authenticated users, 10/minute for anonymous",
        topics=["api", "rate-limiting"],
        source_session=session3,
        confidence=0.9
    )

    print("✅ Sample data populated!\n")
    print(f"   Sessions created: 3")
    print(f"   Conversations: 9 messages")
    print(f"   Decisions: 2")
    print(f"   Conventions: 2")
    print(f"   Learnings: 1")
    print(f"   Artifacts: 1")

    return uacs


def main():
    print_section("UACS v0.3.0: Web UI Visualization")

    # Populate sample data
    uacs = populate_sample_data()

    # ========================================================================
    # Starting the Web UI
    # ========================================================================
    print_section("Starting the Web UI")

    print("The UACS Web UI bundles everything into a single command!\n")

    print("🚀 Bundled Architecture:")
    print("   • FastAPI backend serves the semantic API (14 REST endpoints)")
    print("   • Next.js frontend (static export) bundled into the Python package")
    print("   • All served from one process on port 8081\n")

    print("To start the Web UI:\n")

    print("━━━ Single Command ━━━")
    print("uv run uacs web")
    print()
    print("# Or with custom options:")
    print("uv run uacs web --port 8081 --host localhost")
    print()

    print("━━━ Open Browser ━━━")
    print("open http://localhost:8081")
    print()

    print("💡 Tip: The bundled UI means no separate frontend server needed!")
    print("    Everything is served from the FastAPI backend.\n")

    # ========================================================================
    # Web UI Features
    # ========================================================================
    print_section("Web UI Features")

    print("Once the Web UI is running, you can:\n")

    print("🔍 Semantic Search (/):")
    print("   - Natural language queries: 'how did we implement JWT?'")
    print("   - Filter by 7 content types (messages, decisions, conventions, etc.)")
    print("   - View similarity scores (0-100%)")
    print("   - Expand results for full content\n")

    print("📅 Timeline (/timeline):")
    print("   - Select a session from dropdown")
    print("   - View chronological events")
    print("   - See user messages, assistant responses, tool executions")
    print("   - View latency for tool uses\n")

    print("📚 Knowledge Browser (/knowledge):")
    print("   - Decisions: Architectural decisions with rationale")
    print("   - Conventions: Project conventions with confidence")
    print("   - Learnings: Cross-session patterns")
    print("   - Artifacts: Code files/functions/classes\n")

    print("🔬 Session Traces (/sessions):")
    print("   - View all sessions with stats")
    print("   - Expand to see full event timeline")
    print("   - Track tokens, turns, messages")
    print("   - Click through to details\n")

    # ========================================================================
    # Quick Search Demo
    # ========================================================================
    print_section("Quick Search Demo (API)")

    print("While Web UI is loading, you can search via Python:\n")

    results = uacs.search("JWT authentication implementation", limit=3)

    print(f"🔍 Search: 'JWT authentication implementation'\n")
    print(f"   Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        # Handle both SearchResult types (embeddings.SearchResult and knowledge.SearchResult)
        result_type = result.metadata.get('type', 'unknown') if hasattr(result, 'metadata') and result.metadata else getattr(result, 'type', 'unknown')
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        preview = text[:80] + "..." if len(text) > 80 else text

        print(f"   {i}. [{result_type}] {similarity:.0f}% match")
        print(f"      {preview}\n")

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("✅ Complete!")

    print("You've learned:")
    print("  1. ✅ How to populate UACS with rich sample data")
    print("  2. ✅ How to start the FastAPI backend (port 8081)")
    print("  3. ✅ How to start the Next.js frontend (port 3000)")
    print("  4. ✅ What features the Web UI provides")

    print("\n📖 Next steps:")
    print("  - Run 'uv run uacs web' to start the UI and explore sample data")
    print("  - Run 04_search_and_knowledge.py for advanced patterns")
    print("  - Install Claude Code hooks for automatic capture")

    print("\n📚 Documentation:")
    print("  - Web UI README: uacs-web-ui/README.md")
    print("  - API Reference: docs/API_REFERENCE.md")
    print("  - CLI commands: uv run uacs --help")
    print()


if __name__ == "__main__":
    main()
