"""Test the README Quick Start example"""
from uacs import UACS
from pathlib import Path

# Initialize
uacs = UACS(project_path=Path.cwd())

# Add context entries (simulating agent conversation)
uacs.shared_context.add_entry(
    content="Review authentication for security issues",
    agent="user"
)

uacs.shared_context.add_entry(
    content="Found timing attack in password comparison",
    agent="claude",
    topics=["security"]
)

# Get compressed context
context = uacs.shared_context.get_compressed_context(
    max_tokens=1000        # Token budget
)

# Check compression stats
stats = uacs.get_token_stats()
print(f"✅ Compression: {stats['compression_ratio']}")
print(f"✅ Tokens saved: {stats['tokens_saved_by_compression']}")
print(f"✅ Total tokens: {stats['total_potential_tokens']}")
print("\n✅ README Quick Start example works!")
