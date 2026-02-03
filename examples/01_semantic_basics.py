#!/usr/bin/env python3
"""
Example 1: Semantic API Basics

Demonstrates the core v0.3.0 semantic API:
- Tracking conversations (user messages, assistant responses, tool uses)
- Capturing knowledge (decisions, conventions, learnings, artifacts)
- Semantic search across all stored data

This is the foundation of UACS v0.3.0 - start here!

Run: uv run python examples/01_semantic_basics.py
"""

from pathlib import Path
from uacs import UACS


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def main():
    print_section("UACS v0.3.0: Semantic API Basics")

    # Initialize UACS
    demo_dir = Path(__file__).parent / ".demo_state"
    demo_dir.mkdir(exist_ok=True)
    uacs = UACS(project_path=demo_dir)

    print("✅ Initialized UACS")
    print(f"   Storage: {demo_dir / '.state'}\n")

    # ========================================================================
    # Part 1: Track a Conversation
    # ========================================================================
    print_section("Part 1: Tracking Conversations")

    session_id = "demo_session_001"

    # User asks a question
    print("👤 User asks about authentication...")
    uacs.add_user_message(
        content="Help me implement JWT authentication for my API",
        turn=1,
        session_id=session_id,
        topics=["security", "authentication", "jwt"]
    )
    print("   ✅ User message tracked\n")

    # Assistant responds
    print("🤖 Assistant provides guidance...")
    uacs.add_assistant_message(
        content="I'll help you implement JWT authentication. Let's use PyJWT library with RS256 signing. First, we'll need to generate key pairs.",
        turn=1,
        session_id=session_id,
        tokens_in=42,
        tokens_out=156,
        model="claude-sonnet-4"
    )
    print("   ✅ Assistant message tracked\n")

    # Tool use
    print("🔧 Assistant uses Edit tool...")
    uacs.add_tool_use(
        tool_name="Edit",
        tool_input={"file": "auth.py", "operation": "create"},
        tool_response="Created auth.py with JWT implementation",
        turn=2,
        session_id=session_id,
        latency_ms=450,
        success=True
    )
    print("   ✅ Tool execution tracked\n")

    # ========================================================================
    # Part 2: Capture Knowledge
    # ========================================================================
    print_section("Part 2: Capturing Knowledge")

    # Architectural decision
    print("🧠 Recording architectural decision...")
    uacs.add_decision(
        question="Which authentication method should we use?",
        decision="JWT with RS256 asymmetric signing",
        rationale="Stateless, scalable, works well with microservices. RS256 is more secure than HS256 for production.",
        session_id=session_id,
        alternatives=[
            "Session-based auth (doesn't scale horizontally)",
            "OAuth2 (overkill for internal API)",
            "HS256 JWT (symmetric keys harder to manage)"
        ],
        decided_by="user",
        topics=["security", "authentication", "architecture"]
    )
    print("   ✅ Decision captured\n")

    # Project convention
    print("💡 Recording project convention...")
    uacs.add_convention(
        content="Always use RS256 for JWT signing in production. Store private keys in environment variables, never commit to git.",
        topics=["security", "jwt", "best-practices"],
        source_session=session_id,
        confidence=1.0
    )
    print("   ✅ Convention captured\n")

    # Cross-session learning
    print("📖 Recording learning...")
    uacs.add_learning(
        pattern="JWT tokens should have short expiration (15min) with refresh token rotation",
        learned_from=[session_id],
        category="security_best_practice",
        confidence=0.95
    )
    print("   ✅ Learning captured\n")

    # Code artifact
    print("📄 Recording code artifact...")
    uacs.add_artifact(
        type="file",
        path="auth.py",
        description="JWT authentication implementation with RS256 signing and token refresh",
        created_in_session=session_id,
        topics=["authentication", "jwt"]
    )
    print("   ✅ Artifact tracked\n")

    # ========================================================================
    # Part 3: Semantic Search
    # ========================================================================
    print_section("Part 3: Semantic Search")

    # Search for authentication-related content
    print("🔍 Searching for: 'how did we implement authentication?'\n")
    results = uacs.search(
        query="how did we implement authentication?",
        limit=5
    )

    print(f"   Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        # Handle both SearchResult types (embeddings.SearchResult and knowledge.SearchResult)
        result_type = result.metadata.get('type', 'unknown') if hasattr(result, 'metadata') and result.metadata else getattr(result, 'type', 'unknown')
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        preview = text[:80] + "..." if len(text) > 80 else text

        print(f"   {i}. [{result_type}] {similarity:.0f}% match")
        print(f"      {preview}\n")

    # Search with filters
    print("\n🔍 Searching decisions only: 'authentication method'\n")
    decision_results = uacs.search(
        query="authentication method",
        types=["decision"],
        limit=3
    )

    print(f"   Found {len(decision_results)} decisions:\n")
    for result in decision_results:
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        print(f"   - {similarity:.0f}% match: {text[:100]}...\n")

    # ========================================================================
    # Part 4: Statistics
    # ========================================================================
    print_section("Part 4: System Statistics")

    stats = uacs.get_stats()

    print(f"📊 Conversation Data:")
    print(f"   User messages: {stats['semantic']['conversations']['total_user_messages']}")
    print(f"   Assistant messages: {stats['semantic']['conversations']['total_assistant_messages']}")
    print(f"   Tool uses: {stats['semantic']['conversations']['total_tool_uses']}")

    print(f"\n📚 Knowledge Base:")
    print(f"   Decisions: {stats['semantic']['knowledge']['decisions']}")
    print(f"   Conventions: {stats['semantic']['knowledge']['conventions']}")
    print(f"   Learnings: {stats['semantic']['knowledge']['learnings']}")
    print(f"   Artifacts: {stats['semantic']['knowledge']['artifacts']}")

    print(f"\n🔍 Semantic Search:")
    print(f"   Total vectors: {stats['semantic']['embeddings']['total_vectors']}")
    print(f"   Embedding dimension: {stats['semantic']['embeddings']['dimension']}")

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("✅ Complete!")

    print("You've learned:")
    print("  1. ✅ Track conversations (add_user_message, add_assistant_message, add_tool_use)")
    print("  2. ✅ Capture knowledge (add_decision, add_convention, add_learning, add_artifact)")
    print("  3. ✅ Search semantically (search with natural language)")
    print("  4. ✅ Get statistics (get_stats)")

    print("\n📖 Next steps:")
    print("  - Run 02_claude_code_integration.py to see real Claude Code usage")
    print("  - Run 03_web_ui.py to explore data in the Web UI")
    print("  - Run 04_search_and_knowledge.py for advanced patterns")

    print("\n📚 Documentation:")
    print("  - API Reference: docs/API_REFERENCE.md")
    print("  - Migration Guide: docs/MIGRATION.md")
    print("  - Hooks Guide: .claude-plugin/HOOKS_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
