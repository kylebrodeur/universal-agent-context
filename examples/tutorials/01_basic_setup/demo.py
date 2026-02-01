#!/usr/bin/env python3
"""
Demo 1: Basic Setup - Introduction to UACS

This demo shows the fundamental UACS workflow:
1. Initialize UACS for a project
2. Add context entries (simulating agent conversation)
3. Build compressed context for an agent
4. Check token statistics

This is the "Hello World" of UACS - start here to understand the basics.

Expected output:
- Context entries are added successfully
- Context is built and compressed
- Token statistics show compression savings
- All operations complete in < 1 second
"""

import sys
from pathlib import Path

# Ensure we can import uacs from src
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from uacs import UACS


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def main():
    print_section("Demo 1: Basic Setup")

    print("This demo introduces the core UACS workflow.")
    print("Follow along to learn the fundamentals!\n")

    # Step 1: Initialize UACS
    print("Step 1: Initializing UACS...")
    print("-" * 70)

    # Use a temporary directory for this demo
    demo_dir = Path(__file__).parent / ".demo_state"
    demo_dir.mkdir(exist_ok=True)

    uacs = UACS(project_path=demo_dir)

    print(f"Project path: {demo_dir}")
    print(f"State directory: {demo_dir / '.state' / 'context'}")
    print("Status: Initialized successfully")

    # Step 2: Add context entries
    print_section("Step 2: Adding Context Entries")

    print("Simulating an agent conversation about security review...\n")

    # Entry 1: User request
    print("1. User asks for security review:")
    user_request = "Please review the authentication module for security issues."
    print(f"   Content: {user_request}")

    uacs.add_to_context(
        key="user",
        content=user_request,
        topics=["security", "code-review"]
    )
    print("   Status: Added (topics: security, code-review)")

    # Entry 2: Agent planning
    print("\n2. Claude plans the review:")
    planning = "I'll analyze the authentication module for common vulnerabilities: SQL injection, XSS, timing attacks, and weak password policies."
    print(f"   Content: {planning[:60]}...")

    uacs.add_to_context(
        key="claude",
        content=planning,
        topics=["security", "planning"]
    )
    print("   Status: Added (topics: security, planning)")

    # Entry 3: Finding
    print("\n3. Claude reports a finding:")
    finding = "Found potential timing attack in password comparison at line 42. Using '==' instead of secrets.compare_digest()."
    print(f"   Content: {finding[:60]}...")

    uacs.add_to_context(
        key="claude",
        content=finding,
        topics=["security", "finding"]
    )
    print("   Status: Added (topics: security, finding)")

    # Entry 4: Another finding
    print("\n4. Claude reports another issue:")
    finding2 = "Password requirements are weak: minimum 6 characters, no complexity. Recommend 12+ chars with mixed case, numbers, and symbols."
    print(f"   Content: {finding2[:60]}...")

    uacs.add_to_context(
        key="claude",
        content=finding2,
        topics=["security", "finding"]
    )
    print("   Status: Added (topics: security, finding)")

    # Step 3: Build context
    print_section("Step 3: Building Context")

    print("Building compressed context for Claude...")
    print("Query: 'Continue the security review'")
    print("Topic filter: security")
    print("Token budget: 4000 tokens\n")

    context = uacs.build_context(
        query="Continue the security review",
        agent="claude",
        max_tokens=4000,
        topics=["security"]
    )

    # Count tokens in the built context
    token_count = uacs.shared_context.count_tokens(context)

    print(f"Context built successfully:")
    print(f"  Length: {token_count} tokens")
    print(f"  Preview (first 200 chars):")
    print(f"  {context[:200]}...")

    # Step 4: Check statistics
    print_section("Step 4: Token Statistics")

    stats = uacs.get_token_stats()

    print("Token Usage:")
    print(f"  Total entries: {stats.get('total_entries', 4)}")
    print(f"  Total tokens: {stats.get('total_tokens', 0):,}")
    print(f"  Compressed tokens: {stats.get('compressed_tokens', token_count):,}")

    if stats.get('total_tokens', 0) > 0:
        compression_ratio = ((stats['total_tokens'] - token_count) / stats['total_tokens'] * 100)
        print(f"  Compression ratio: {compression_ratio:.1f}%")
        print(f"  Tokens saved: {stats['total_tokens'] - token_count:,}")

    print("\nCompression Strategies Applied:")
    print("  - Deduplication: Identical content stored once")
    print("  - Quality filtering: Low-value entries summarized")
    print("  - Recency bias: Recent entries prioritized")
    print("  - Topic relevance: Only 'security' entries included")

    # Step 5: What you learned
    print_section("What You Learned")

    print("1. Initialization:")
    print("   UACS uses project-local storage (.state/context/)")
    print("   State is persistent between sessions")

    print("\n2. Context Entries:")
    print("   Simple key-value pairs with automatic metadata")
    print("   Topics enable semantic filtering")

    print("\n3. Context Building:")
    print("   Compression happens automatically")
    print("   Topic filtering reduces irrelevant content")
    print("   Token budgets are enforced")

    print("\n4. Statistics:")
    print("   Real-time visibility into token usage")
    print("   Understand compression effectiveness")

    # Cleanup
    print_section("Demo Complete")

    print("Next Steps:")
    print("  1. Demo 2: Context Compression - Deep dive into 70%+ savings")
    print("  2. Demo 3: Multi-Agent Context - Share context between agents")
    print("  3. Demo 4: Topic-Based Retrieval - Advanced filtering")
    print("  4. Demo 5: Claude Code Integration - The killer use case")

    print("\nTo run next demo:")
    print("  uv run python examples/02_context_compression/demo.py")

    # Note: We keep .demo_state for inspection but don't auto-delete
    print(f"\nDemo state saved to: {demo_dir}")
    print("(You can delete this directory when done: rm -rf examples/01_basic_setup/.demo_state)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure UACS is installed: uv sync")
        print("  2. Run from project root: uv run python examples/01_basic_setup/demo.py")
        print("  3. Check write permissions in examples/ directory")
        sys.exit(1)
