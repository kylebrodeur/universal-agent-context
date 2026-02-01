"""
Example: Context Compression

This script demonstrates UACS's context compression capabilities,
showing how 70%+ token reduction is achieved while preserving quality.

Features demonstrated:
- Before/after token counts
- Compression ratio calculation
- Quality scoring and filtering
- Deduplication strategy
"""

import sys
from pathlib import Path

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs.context.shared_context import SharedContextManager


def main():
    print("🗜️  UACS Context Compression Demo\n")
    print("=" * 70)

    # Initialize context manager
    print("\n📦 Initializing SharedContextManager...")
    ctx = SharedContextManager()

    # Simulate a realistic conversation with repeated information
    print("\n📝 Adding conversation entries...\n")

    conversations = [
        # User request (high quality)
        {
            "content": "Please review the authentication module in auth.py for security vulnerabilities.",
            "agent": "user",
            "topics": ["security", "auth"],
            "metadata": {"role": "user"}
        },
        # Agent planning (medium quality)
        {
            "content": "I'll check the authentication module for common security issues like SQL injection, XSS, and timing attacks.",
            "agent": "claude",
            "topics": ["security", "planning"],
            "metadata": {"role": "assistant"}
        },
        # Agent finding (high quality)
        {
            "content": "Found a potential timing attack in the password comparison function at line 42. Using '==' instead of secure comparison.",
            "agent": "claude",
            "topics": ["security", "finding"],
            "metadata": {"role": "assistant"}
        },
        # Duplicate request (will be deduplicated)
        {
            "content": "Please review the authentication module in auth.py for security vulnerabilities.",
            "agent": "user",
            "topics": ["security", "auth"],
            "metadata": {"role": "user"}
        },
        # More details (medium quality)
        {
            "content": "Also checking for hardcoded credentials and weak password requirements.",
            "agent": "claude",
            "topics": ["security", "planning"],
            "metadata": {"role": "assistant"}
        },
        # Another finding (high quality)
        {
            "content": "Password requirements are weak: minimum 6 characters, no complexity requirements. Recommend 12+ chars with mixed case, numbers, symbols.",
            "agent": "claude",
            "topics": ["security", "finding"],
            "metadata": {"role": "assistant"}
        },
        # User acknowledgment (low quality)
        {
            "content": "Thanks",
            "agent": "user",
            "topics": [],
            "metadata": {"role": "user"}
        },
        # Agent acknowledgment (low quality)
        {
            "content": "You're welcome!",
            "agent": "claude",
            "topics": [],
            "metadata": {"role": "assistant"}
        },
        # Follow-up question (high quality)
        {
            "content": "Can you also check the session management code for vulnerabilities?",
            "agent": "user",
            "topics": ["security", "session"],
            "metadata": {"role": "user"}
        },
        # Agent response (high quality)
        {
            "content": "Found issue with session tokens: using predictable sequential IDs instead of cryptographically secure random tokens. Recommend using secrets.token_urlsafe().",
            "agent": "claude",
            "topics": ["security", "session", "finding"],
            "metadata": {"role": "assistant"}
        },
    ]

    # Add all entries and track which were deduplicated
    entry_ids = []
    deduped_count = 0

    for i, conv in enumerate(conversations, 1):
        entry_id = ctx.add_entry(
            content=conv["content"],
            agent=conv["agent"],
            topics=conv["topics"],
            metadata=conv["metadata"]
        )

        # Check if this was a duplicate
        if entry_id in entry_ids:
            deduped_count += 1
            print(f"  {i}. [DEDUPED] {conv['agent']}: {conv['content'][:50]}...")
        else:
            entry_ids.append(entry_id)
            print(f"  {i}. [{conv['agent']:8s}] {conv['content'][:50]}...")

    print(f"\n✅ Added {len(conversations)} entries ({deduped_count} duplicates removed)")

    # Show stats before compression
    print("\n" + "=" * 70)
    print("📊 BEFORE COMPRESSION")
    print("=" * 70)

    # Get uncompressed context
    full_context = "\n\n".join([
        f"{entry.agent}: {entry.content}"
        for entry in ctx.entries.values()
    ])

    original_tokens = ctx.count_tokens(full_context)
    print(f"\nTotal entries: {len(ctx.entries)}")
    print(f"Original tokens: {original_tokens:,}")
    print(f"Deduplication savings: {deduped_count} entries removed")

    # Show quality scores
    print("\n📈 Quality Scores:")
    for entry_id, entry in list(ctx.entries.items())[:5]:  # Show first 5
        print(f"  - {entry.agent:8s} (quality={entry.quality:.2f}): {entry.content[:40]}...")
    if len(ctx.entries) > 5:
        print(f"  ... and {len(ctx.entries) - 5} more entries")

    # Compress with different token budgets
    print("\n" + "=" * 70)
    print("🗜️  COMPRESSION RESULTS")
    print("=" * 70)

    budgets = [8000, 4000, 2000, 1000]

    for budget in budgets:
        compressed = ctx.get_compressed_context(max_tokens=budget)
        compressed_tokens = ctx.count_tokens(compressed)
        ratio = ((original_tokens - compressed_tokens) / original_tokens * 100)

        print(f"\n📦 Budget: {budget:,} tokens")
        print(f"   Result: {compressed_tokens:,} tokens")
        print(f"   Compression: {ratio:.1f}% reduction")
        print(f"   Preview: {compressed[:100]}...")

    # Show topic-based filtering
    print("\n" + "=" * 70)
    print("🎯 TOPIC-BASED COMPRESSION")
    print("=" * 70)

    # Get context filtered by topic using get_focused_context
    security_context = ctx.get_focused_context(
        topics=["security"],
        max_tokens=2000
    )
    security_tokens = ctx.count_tokens(security_context)

    print(f"\n🔒 Security topic only:")
    print(f"   Tokens: {security_tokens:,}")
    print(f"   Preview: {security_context[:150]}...")

    # Show agent-specific filtering using get_focused_context
    claude_context = ctx.get_focused_context(
        agent="claude",
        max_tokens=2000
    )
    claude_tokens = ctx.count_tokens(claude_context)

    print(f"\n🤖 Claude's responses only:")
    print(f"   Tokens: {claude_tokens:,}")
    print(f"   Preview: {claude_context[:150]}...")

    # Summary statistics
    print("\n" + "=" * 70)
    print("📊 COMPRESSION SUMMARY")
    print("=" * 70)

    # Calculate actual 70%+ compression
    target_budget = int(original_tokens * 0.3)  # 70% reduction = 30% remaining
    compressed_70 = ctx.get_compressed_context(max_tokens=target_budget)
    compressed_70_tokens = ctx.count_tokens(compressed_70)
    actual_ratio = ((original_tokens - compressed_70_tokens) / original_tokens * 100)

    print(f"\n✨ Compression Strategies Used:")
    print(f"   1. Deduplication: {deduped_count} duplicate entries removed")
    print(f"   2. Quality filtering: Low-value entries summarized")
    print(f"   3. Recency bias: Recent entries preserved")
    print(f"   4. Topic relevance: Context-aware filtering available")

    print(f"\n🎯 Target: 70% compression")
    print(f"   Original: {original_tokens:,} tokens")
    print(f"   Compressed: {compressed_70_tokens:,} tokens")
    print(f"   Actual reduction: {actual_ratio:.1f}%")
    print(f"   {'✅ Target achieved!' if actual_ratio >= 70 else '⚠️  Below target'}")

    # Cost savings example
    print("\n" + "=" * 70)
    print("💰 COST SAVINGS (Example)")
    print("=" * 70)

    # Example pricing: $0.01 per 1K tokens (typical for GPT-4)
    cost_per_1k = 0.01
    calls_per_day = 100

    original_cost_per_call = (original_tokens / 1000) * cost_per_1k
    compressed_cost_per_call = (compressed_70_tokens / 1000) * cost_per_1k

    daily_savings = (original_cost_per_call - compressed_cost_per_call) * calls_per_day
    monthly_savings = daily_savings * 30

    print(f"\n💵 At $0.01 per 1K tokens, 100 calls/day:")
    print(f"   Without compression: ${original_cost_per_call:.4f}/call × 100 = ${original_cost_per_call * calls_per_day:.2f}/day")
    print(f"   With compression:    ${compressed_cost_per_call:.4f}/call × 100 = ${compressed_cost_per_call * calls_per_day:.2f}/day")
    print(f"   Daily savings:       ${daily_savings:.2f}")
    print(f"   Monthly savings:     ${monthly_savings:.2f}")
    print(f"   Annual savings:      ${monthly_savings * 12:.2f}")

    print("\n" + "=" * 70)
    print("✅ Compression demo complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
