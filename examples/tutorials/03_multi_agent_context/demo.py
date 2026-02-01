#!/usr/bin/env python3
"""
Demo 3: Multi-Agent Context Sharing

This demo shows how multiple agents share context through UACS:
1. Agent 1 (Security Reviewer) analyzes code and adds findings
2. Agent 2 (Code Fixer) retrieves findings and adds fixes
3. Agent 3 (Verifier) retrieves everything and validates fixes
4. Statistics show cost savings from shared compression

This demonstrates UACS as context middleware for multi-agent systems.

Expected output:
- Three agents working sequentially
- Automatic context sharing (no manual coordination)
- Topic-based filtering per agent
- Cost savings from shared compression
"""

import sys
from pathlib import Path

# Ensure we can import uacs from src
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from uacs import UACS


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}\n")


def print_agent_header(agent_name: str, role: str):
    """Print agent header."""
    print(f"\n{'─' * 70}")
    print(f"🤖 Agent: {agent_name} ({role})")
    print(f"{'─' * 70}\n")


def main():
    print_section("Demo 3: Multi-Agent Context Sharing")

    print("This demo shows three agents working together through shared context:")
    print("  1. Security Reviewer (finds issues)")
    print("  2. Code Fixer (fixes issues)")
    print("  3. Verifier (validates fixes)")
    print("\nNo manual context passing required - UACS handles it automatically!\n")

    # Setup shared UACS instance
    demo_dir = Path(__file__).parent / ".demo_state"
    demo_dir.mkdir(exist_ok=True)

    print("Initializing shared UACS context...")
    uacs = UACS(project_path=demo_dir)
    print(f"Context storage: {demo_dir / '.state' / 'context'}\n")

    # ========================================================================
    # AGENT 1: Security Reviewer
    # ========================================================================
    print_agent_header("Agent 1", "Security Reviewer")

    print("Task: Analyze authentication.py for security vulnerabilities\n")

    print("Analysis in progress...")
    print("  Checking for SQL injection...")
    print("  Checking for timing attacks...")
    print("  Checking session security...\n")

    # Agent 1 findings
    findings = [
        {
            "content": "CRITICAL: SQL injection vulnerability at line 42 in user_login(). Using string concatenation instead of parameterized queries. Attacker can inject SQL: ' OR '1'='1",
            "topics": ["security", "sql-injection", "finding"],
            "severity": "CRITICAL"
        },
        {
            "content": "HIGH: Timing attack vulnerability at line 78 in password verification. Using '==' operator instead of secrets.compare_digest(). Allows character-by-character password guessing.",
            "topics": ["security", "timing-attack", "finding"],
            "severity": "HIGH"
        },
        {
            "content": "HIGH: Session tokens are predictable at line 156. Using sequential IDs instead of cryptographically secure random tokens. Recommend secrets.token_urlsafe(32).",
            "topics": ["security", "session", "finding"],
            "severity": "HIGH"
        },
    ]

    print("Findings discovered:")
    for i, finding in enumerate(findings, 1):
        # Add to shared context
        uacs.add_to_context(
            key="security-reviewer",
            content=finding["content"],
            topics=finding["topics"],
            metadata={"severity": finding["severity"]}
        )
        print(f"  {i}. [{finding['severity']}] {finding['content'][:60]}...")

    print(f"\n✅ Agent 1 complete: {len(findings)} findings added to shared context")

    # ========================================================================
    # AGENT 2: Code Fixer
    # ========================================================================
    print_agent_header("Agent 2", "Code Fixer")

    print("Task: Fix security issues found by Security Reviewer\n")

    # Agent 2 retrieves context
    print("Retrieving security findings from shared context...")
    context = uacs.build_context(
        query="Fix security vulnerabilities",
        agent="code-fixer",
        topics=["security", "finding"],
        max_tokens=3000
    )

    context_tokens = uacs.shared_context.count_tokens(context)
    print(f"Retrieved context: {context_tokens} tokens")
    print(f"Topics: security, finding\n")

    # Parse findings from context (simulated - in real use, LLM would do this)
    print("Context includes:")
    for i, finding in enumerate(findings, 1):
        severity = finding["severity"]
        content = finding["content"][:50]
        print(f"  {i}. [{severity}] {content}...")

    print("\nGenerating fixes...\n")

    # Agent 2 adds fixes
    fixes = [
        {
            "content": "FIX: Replaced string concatenation with parameterized query at line 42. Now using cursor.execute('SELECT * FROM users WHERE username = ?', (username,)). SQL injection no longer possible.",
            "topics": ["security", "sql-injection", "fix"],
            "finding_id": 1
        },
        {
            "content": "FIX: Replaced '==' with secrets.compare_digest() at line 78. Timing attack no longer possible as comparison time is constant regardless of input.",
            "topics": ["security", "timing-attack", "fix"],
            "finding_id": 2
        },
        {
            "content": "FIX: Replaced sequential session IDs with secrets.token_urlsafe(32) at line 156. Session tokens are now cryptographically secure and unpredictable.",
            "topics": ["security", "session", "fix"],
            "finding_id": 3
        },
    ]

    print("Fixes implemented:")
    for i, fix in enumerate(fixes, 1):
        # Add to shared context
        uacs.add_to_context(
            key="code-fixer",
            content=fix["content"],
            topics=fix["topics"],
            metadata={"finding_id": fix["finding_id"]}
        )
        print(f"  {i}. {fix['content'][:60]}...")

    print(f"\n✅ Agent 2 complete: {len(fixes)} fixes added to shared context")

    # ========================================================================
    # AGENT 3: Verifier
    # ========================================================================
    print_agent_header("Agent 3", "Verifier")

    print("Task: Verify that all security issues have been properly fixed\n")

    # Agent 3 retrieves full security context (findings + fixes)
    print("Retrieving full security context (findings + fixes)...")
    verification_context = uacs.build_context(
        query="Verify security fixes are complete and correct",
        agent="verifier",
        topics=["security"],  # All security-related context
        max_tokens=4000
    )

    verification_tokens = uacs.shared_context.count_tokens(verification_context)
    print(f"Retrieved context: {verification_tokens} tokens")
    print(f"Topics: security (all subtopics)\n")

    print("Context includes:")
    print(f"  - {len(findings)} findings from Security Reviewer")
    print(f"  - {len(fixes)} fixes from Code Fixer")
    print(f"  - Total: {len(findings) + len(fixes)} entries\n")

    print("Verification in progress...")

    # Simulate verification
    verifications = []
    for i in range(len(findings)):
        finding = findings[i]
        fix = fixes[i]

        # Check if fix addresses finding
        verification = {
            "finding": finding["content"][:40],
            "fix": fix["content"][:40],
            "status": "✅ VERIFIED",
            "notes": "Fix properly addresses the vulnerability"
        }
        verifications.append(verification)

        uacs.add_to_context(
            key="verifier",
            content=f"Verified fix for {finding['topics'][1]}: {fix['content'][:50]}... - Status: COMPLETE",
            topics=["security", "verification", finding["topics"][1]],
            metadata={"finding_id": i + 1, "status": "verified"}
        )

    print("\nVerification results:")
    for i, verification in enumerate(verifications, 1):
        print(f"  {i}. Finding: {verification['finding']}...")
        print(f"     Fix: {verification['fix']}...")
        print(f"     {verification['status']}: {verification['notes']}\n")

    print(f"✅ Agent 3 complete: All {len(verifications)} fixes verified")

    # ========================================================================
    # STATISTICS & ANALYSIS
    # ========================================================================
    print_section("Multi-Agent Context Statistics")

    # Get overall statistics
    stats = uacs.get_token_stats()

    total_entries = len(findings) + len(fixes) + len(verifications)
    print(f"Total Entries: {total_entries}")
    print(f"  - Security findings: {len(findings)}")
    print(f"  - Fixes: {len(fixes)}")
    print(f"  - Verifications: {len(verifications)}\n")

    # Calculate total tokens written
    all_content = []
    for finding in findings:
        all_content.append(finding["content"])
    for fix in fixes:
        all_content.append(fix["content"])
    for verification in verifications:
        all_content.append(f"Verified: {verification['finding']}")

    total_tokens_written = sum(
        uacs.shared_context.count_tokens(content) for content in all_content
    )

    # Calculate tokens read by each agent
    agent2_tokens = context_tokens
    agent3_tokens = verification_tokens
    total_tokens_read = agent2_tokens + agent3_tokens

    print(f"Token Usage:")
    print(f"  Total written: {total_tokens_written:,} tokens")
    print(f"  Agent 2 read: {agent2_tokens:,} tokens (findings only)")
    print(f"  Agent 3 read: {agent3_tokens:,} tokens (findings + fixes)")
    print(f"  Total read: {total_tokens_read:,} tokens\n")

    # Calculate compression
    # Without compression: Agent 2 would read all findings, Agent 3 would read all
    uncompressed_agent2 = sum(
        uacs.shared_context.count_tokens(f["content"]) for f in findings
    )
    uncompressed_agent3 = uncompressed_agent2 + sum(
        uacs.shared_context.count_tokens(f["content"]) for f in fixes
    )
    total_uncompressed = uncompressed_agent2 + uncompressed_agent3

    compression_ratio = (
        (total_uncompressed - total_tokens_read) / total_uncompressed * 100
        if total_uncompressed > 0 else 0
    )

    print(f"Compression Analysis:")
    print(f"  Without UACS: {total_uncompressed:,} tokens")
    print(f"  With UACS: {total_tokens_read:,} tokens")
    print(f"  Compression: {compression_ratio:.1f}%")
    print(f"  Tokens saved: {total_uncompressed - total_tokens_read:,}\n")

    # Cost calculation
    cost_per_1k = 0.01
    cost_without = (total_uncompressed / 1000) * cost_per_1k
    cost_with = (total_tokens_read / 1000) * cost_per_1k
    savings = cost_without - cost_with

    print(f"Cost Savings (${cost_per_1k}/1K tokens):")
    print(f"  Without compression: ${cost_without:.4f}")
    print(f"  With compression: ${cost_with:.4f}")
    print(f"  Savings per workflow: ${savings:.4f} ({compression_ratio:.1f}%)\n")

    # Scaling
    workflows_per_day = 100
    monthly_savings = savings * workflows_per_day * 30

    print(f"Scaling Impact ({workflows_per_day} workflows/day):")
    print(f"  Daily savings: ${savings * workflows_per_day:.2f}")
    print(f"  Monthly savings: ${monthly_savings:.2f}")
    print(f"  Annual savings: ${monthly_savings * 12:.2f}")

    # ========================================================================
    # WHAT YOU LEARNED
    # ========================================================================
    print_section("What You Learned")

    print("1. Shared Context is Automatic:")
    print("   - Agents write to shared context")
    print("   - Other agents read automatically")
    print("   - No manual coordination needed\n")

    print("2. Topic-Based Routing Works:")
    print("   - Agent 2 filtered by 'finding'")
    print("   - Agent 3 got all 'security' topics")
    print("   - Each agent sees only what's relevant\n")

    print("3. Compression Benefits All Agents:")
    print(f"   - {compression_ratio:.1f}% compression across {total_entries} entries")
    print("   - Applied once, benefits multiple agents")
    print("   - Cost scales linearly with agent count\n")

    print("4. Agent Independence:")
    print("   - Agents don't know about each other")
    print("   - Can use different LLM providers")
    print("   - UACS handles coordination\n")

    print("5. Sequential Workflows Scale:")
    print("   - More agents = more token reuse")
    print("   - Cost per agent decreases")
    print("   - Context continuity maintained")

    # ========================================================================
    # ARCHITECTURE PATTERNS
    # ========================================================================
    print_section("Architecture Patterns Demonstrated")

    print("This demo showed: Sequential Pipeline")
    print("  Agent 1 → Agent 2 → Agent 3")
    print("  (Find) → (Fix) → (Verify)\n")

    print("Other patterns possible:")
    print("  • Parallel Specialists: Multiple agents analyze different aspects")
    print("  • Hierarchical: Coordinator delegates to specialists")
    print("  • Collaborative: Agents iterate on shared artifacts\n")

    print("See architecture.md for detailed patterns and examples.")

    # ========================================================================
    # COMPLETION
    # ========================================================================
    print_section("Demo Complete")

    print("Key Takeaway:")
    print(f"  3 agents collaborated through shared context")
    print(f"  {compression_ratio:.1f}% compression saved {total_uncompressed - total_tokens_read:,} tokens")
    print(f"  ${monthly_savings:.2f}/month savings at 100 workflows/day")
    print("  Zero manual context synchronization")

    print("\nNext Steps:")
    print("  1. Demo 4: Topic-Based Retrieval - Advanced filtering")
    print("  2. Demo 5: Claude Code Integration - The killer use case")
    print("  3. See architecture.md for multi-agent patterns")

    print("\nTo run next demo:")
    print("  uv run python examples/04_topic_based_retrieval/demo.py")

    print(f"\nDemo state saved to: {demo_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("  1. Make sure UACS is installed: uv sync")
        print("  2. Run from project root: uv run python examples/03_multi_agent_context/demo.py")
        sys.exit(1)
