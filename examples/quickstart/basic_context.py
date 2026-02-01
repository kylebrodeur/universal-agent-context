"""
Example: Basic Context Usage

This script demonstrates how to initialize the UnifiedContextAdapter,
add context entries, and retrieve a compressed context.
"""

import sys
from pathlib import Path

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs.context.unified_context import UnifiedContextAdapter
from uacs.context.shared_context import SharedContextManager

def main():
    print("🚀 Initializing Unified Context...")

    # Initialize the adapter
    # This will look for AGENTS.md and SKILLS.md in the current directory
    adapter = UnifiedContextAdapter()

    print("\n📝 Adding context entries...")

    # Simulate a conversation
    adapter.shared_context.add_entry(
        content="Please review the authentication module for security flaws.",
        agent="user",
        metadata={"role": "user"}
    )

    adapter.shared_context.add_entry(
        content="I'll check for common vulnerabilities like SQL injection and XSS.",
        agent="claude",
        metadata={"role": "assistant"},
        topics=["security", "planning"]
    )

    adapter.shared_context.add_entry(
        content="Found a potential timing attack in the password comparison function.",
        agent="claude",
        metadata={"role": "assistant"},
        topics=["security", "finding"]
    )

    print("\n📊 Context Statistics:")
    stats = adapter.get_token_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")

    print("\n🔍 Retrieving Compressed Context (max 500 tokens)...")
    # This simulates what would be sent to an LLM
    context = adapter.shared_context.get_compressed_context(max_tokens=500)

    print("\n--- Context Dump ---")
    print(context)
    print("--------------------")

if __name__ == "__main__":
    main()
