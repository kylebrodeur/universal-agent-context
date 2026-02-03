#!/usr/bin/env python3
"""
Example 4: Advanced Search & Knowledge Patterns

Demonstrates advanced v0.3.0 semantic API features:
- Type-filtered search (decisions only, conventions only)
- Confidence-filtered search (high-quality items)
- Multi-type search (search across categories)
- Knowledge organization best practices
- Cross-session insight extraction

Run: uv run python examples/04_search_and_knowledge.py
"""

from pathlib import Path
from uacs import UACS


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def populate_rich_knowledge():
    """Populate UACS with knowledge from multiple sessions for search demo."""

    demo_dir = Path(__file__).parent / ".demo_state"
    demo_dir.mkdir(exist_ok=True)
    uacs = UACS(project_path=demo_dir)

    print("📝 Populating knowledge from 3 different sessions...\n")

    # ========================================================================
    # Session 1: Security Implementation
    # ========================================================================
    session1 = "security_session_001"

    uacs.add_decision(
        question="How should we prevent common web attacks?",
        decision="Implement input validation with allowlists, not denylists",
        rationale="Allowlists are more secure - explicitly permit safe patterns rather than trying to block all dangerous ones",
        session_id=session1,
        alternatives=["Regex filtering", "Escape special characters only"],
        topics=["security", "input-validation"]
    )

    uacs.add_convention(
        content="Always validate user input at API boundaries using Pydantic models",
        topics=["security", "validation", "api"],
        source_session=session1,
        confidence=1.0  # High confidence
    )

    uacs.add_learning(
        pattern="Rate limiting should be per-user, not per-IP, to prevent proxy bypass",
        learned_from=[session1],
        category="security_best_practice",
        confidence=0.95  # Very confident
    )

    # ========================================================================
    # Session 2: Performance Optimization
    # ========================================================================
    session2 = "performance_session_002"

    uacs.add_decision(
        question="How should we cache expensive database queries?",
        decision="Use Redis with TTL-based invalidation",
        rationale="Redis provides fast lookups, distributed caching, and automatic expiration",
        session_id=session2,
        alternatives=["In-memory cache", "Memcached"],
        topics=["performance", "caching", "database"]
    )

    uacs.add_convention(
        content="Cache keys should follow pattern: {service}:{entity}:{id}",
        topics=["caching", "naming"],
        source_session=session2,
        confidence=0.8  # Good confidence
    )

    uacs.add_learning(
        pattern="Database indexes should match your query patterns, not just foreign keys",
        learned_from=[session2],
        category="database_optimization",
        confidence=0.9
    )

    # ========================================================================
    # Session 3: API Design
    # ========================================================================
    session3 = "api_design_session_003"

    uacs.add_decision(
        question="Should we use REST or GraphQL for our API?",
        decision="REST for public API, GraphQL for internal frontend",
        rationale="REST is simpler for external consumers, GraphQL reduces over-fetching for our SPA",
        session_id=session3,
        alternatives=["Only REST", "Only GraphQL", "gRPC"],
        topics=["api-design", "architecture"]
    )

    uacs.add_convention(
        content="API endpoints should use plural nouns: /users, /posts, not /user, /post",
        topics=["api-design", "naming"],
        source_session=session3,
        confidence=0.9
    )

    uacs.add_learning(
        pattern="Versioning APIs in the URL (/v1/, /v2/) is easier than header-based versioning",
        learned_from=[session3],
        category="api_best_practice",
        confidence=0.75  # Medium-high confidence
    )

    print("✅ Populated 3 sessions with 9 knowledge items\n")
    return uacs


def main():
    print_section("UACS v0.3.0: Advanced Search & Knowledge")

    # Populate knowledge
    uacs = populate_rich_knowledge()

    # ========================================================================
    # Part 1: Type-Filtered Search
    # ========================================================================
    print_section("Part 1: Type-Filtered Search")

    print("🔍 Searching for DECISIONS only: 'how to handle caching'\n")
    decisions = uacs.search(
        query="how to handle caching",
        types=["decision"],  # Only search decisions
        limit=5
    )

    print(f"   Found {len(decisions)} decision(s):\n")
    for result in decisions:
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        print(f"   - {similarity:.0f}% match: {text[:100]}...\n")

    print("\n🔍 Searching for CONVENTIONS only: 'naming patterns'\n")
    conventions = uacs.search(
        query="naming patterns",
        types=["convention"],  # Only search conventions
        limit=5
    )

    print(f"   Found {len(conventions)} convention(s):\n")
    for result in conventions:
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        print(f"   - {similarity:.0f}% match: {text[:100]}...\n")

    # ========================================================================
    # Part 2: Multi-Type Search
    # ========================================================================
    print_section("Part 2: Multi-Type Search")

    print("🔍 Searching across DECISIONS + LEARNINGS: 'security best practices'\n")
    security_knowledge = uacs.search(
        query="security best practices",
        types=["decision", "learning"],  # Search both types
        limit=5
    )

    print(f"   Found {len(security_knowledge)} item(s):\n")
    for result in security_knowledge:
        result_type = result.metadata.get('type', 'unknown') if hasattr(result, 'metadata') and result.metadata else getattr(result, 'type', 'unknown')
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        print(f"   [{result_type}] {similarity:.0f}% match:")
        print(f"   {text[:120]}...\n")

    # ========================================================================
    # Part 3: Confidence-Based Filtering
    # ========================================================================
    print_section("Part 3: High-Confidence Knowledge")

    print("🔍 Searching for HIGH-CONFIDENCE items (>= 0.9): 'best practices'\n")
    high_conf = uacs.search(
        query="best practices",
        types=["convention", "learning"],
        min_confidence=0.9,  # Only high-confidence items
        limit=10
    )

    print(f"   Found {len(high_conf)} high-confidence item(s):\n")
    for result in high_conf:
        result_type = result.metadata.get('type', 'unknown') if hasattr(result, 'metadata') and result.metadata else getattr(result, 'type', 'unknown')
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')

        # Try to get confidence from metadata
        confidence = None
        if hasattr(result, 'metadata') and result.metadata:
            confidence = result.metadata.get('confidence')

        conf_str = f" [conf: {confidence:.2f}]" if confidence else ""
        print(f"   [{result_type}]{conf_str} {similarity:.0f}% match:")
        print(f"   {text[:120]}...\n")

    # ========================================================================
    # Part 4: Session-Specific Search
    # ========================================================================
    print_section("Part 4: Session-Specific Search")

    print("🔍 Searching within SPECIFIC SESSION: security_session_001\n")
    session_results = uacs.search(
        query="security patterns",
        session_id="security_session_001",  # Filter by session
        limit=10
    )

    print(f"   Found {len(session_results)} item(s) from security_session_001:\n")
    for result in session_results:
        result_type = result.metadata.get('type', 'unknown') if hasattr(result, 'metadata') and result.metadata else getattr(result, 'type', 'unknown')
        similarity = (getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)) * 100
        text = getattr(result, 'text', None) or getattr(result, 'content', '')
        print(f"   [{result_type}] {similarity:.0f}% match:")
        print(f"   {text[:120]}...\n")

    # ========================================================================
    # Part 5: Knowledge Organization Best Practices
    # ========================================================================
    print_section("Part 5: Knowledge Organization Tips")

    print("💡 Best Practices:\n")

    print("1. Type Selection:")
    print("   - Use DECISIONS for 'why we chose X over Y' questions")
    print("   - Use CONVENTIONS for 'how we always do X' patterns")
    print("   - Use LEARNINGS for cross-session insights")
    print("   - Use ARTIFACTS to track what files/functions exist\n")

    print("2. Topics:")
    print("   - Use consistent topic names across sessions")
    print("   - Keep topics lowercase and hyphenated: 'api-design', not 'API Design'")
    print("   - Use 2-4 topics per item for good searchability\n")

    print("3. Confidence Scores:")
    print("   - 1.0: Established patterns you always follow")
    print("   - 0.9: Strong patterns with rare exceptions")
    print("   - 0.8: Good patterns but context-dependent")
    print("   - 0.7: Emerging patterns, still evaluating\n")

    print("4. Search Strategies:")
    print("   - Start broad, then filter by type/confidence")
    print("   - Use session_id to understand decision context")
    print("   - Combine types (decision + learning) for full picture")
    print("   - Set min_confidence high for trusted guidance\n")

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("✅ Complete!")

    print("You've learned:")
    print("  1. ✅ Type-filtered search (decisions, conventions, learnings)")
    print("  2. ✅ Multi-type search across categories")
    print("  3. ✅ Confidence-based filtering for quality")
    print("  4. ✅ Session-specific search for context")
    print("  5. ✅ Knowledge organization best practices")

    print("\n📖 Next steps:")
    print("  - Integrate UACS into your projects")
    print("  - Install Claude Code hooks for automatic capture")
    print("  - Explore the Web UI for visual knowledge browsing")

    print("\n📚 Documentation:")
    print("  - API Reference: docs/API_REFERENCE.md")
    print("  - Hooks Guide: .claude-plugin/HOOKS_GUIDE.md")
    print("  - Migration Guide: docs/MIGRATION.md")
    print()


if __name__ == "__main__":
    main()
