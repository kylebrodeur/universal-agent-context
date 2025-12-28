"""
Example: Multi-Format Translation

This script demonstrates UACS's format translation capabilities.
Shows how to load one format (AGENTS.md) and convert it to other formats
(.cursorrules, .clinerules) with validation.

Note: This is a simplified example showing the concept. The actual
AgentSkillAdapter works with individual SKILL.md files in .agent/skills/ directory.

Features demonstrated:
- Loading AGENTS.md format
- Converting to .cursorrules (Cursor IDE)
- Converting to .clinerules (Cline extension)
- Format validation
"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs.adapters.agents_md_adapter import AgentsMDAdapter
from uacs.adapters.cursorrules_adapter import CursorRulesAdapter
from uacs.adapters.clinerules_adapter import ClineRulesAdapter


def create_sample_agents_file(path: Path) -> None:
    """Create a sample AGENTS.md file for demonstration."""
    content = """# Project Context

## Overview

Multi-Agent CLI Orchestration Tool for coordinating multiple AI agents.

## Tech Stack

- Python 3.11+
- Google ADK (Agent Development Kit)
- MCP (Model Context Protocol)
- Rich (Terminal UI)

## Code Style

- Use type hints for all functions
- Follow PEP 8 conventions
- Docstrings for public APIs (Google style)
- Ruff for formatting and linting (line length: 88)

## Best Practices

When writing code:
- Always add type annotations
- Use dataclasses instead of dictionaries for structured data
- Implement async/await for I/O operations
- Write tests for new features
"""
    path.write_text(content)


def main():
    print("🔄 UACS Multi-Format Translation Demo\n")
    print("=" * 70)

    # Create temporary directory for demo files
    with TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Step 1: Create source AGENTS.md
        print("\n📝 Step 1: Creating sample AGENTS.md file...")
        agents_file = tmppath / "AGENTS.md"
        create_sample_agents_file(agents_file)
        print(f"   ✅ Created: {agents_file}")

        # Show original content
        print("\n📄 Original AGENTS.md content:")
        print("-" * 70)
        original_content = agents_file.read_text()
        print(original_content[:400] + "...")
        print("-" * 70)

        # Step 2: Parse AGENTS.md
        print("\n🔍 Step 2: Parsing AGENTS.md...")
        agents_adapter = AgentsMDAdapter(agents_file)

        # Read and parse content
        agents_content = agents_file.read_text()
        parsed = agents_adapter.parse(agents_content)

        print(f"   ✅ Parsed successfully")
        print(f"      Overview: {parsed.instructions[:80] if parsed.instructions else 'N/A'}...")

        # Step 3: Convert to .cursorrules
        print("\n🎯 Step 3: Converting to .cursorrules (Cursor IDE)...")
        cursorrules_file = tmppath / ".cursorrules"

        # Generate system prompt from AGENTS.md
        agents_adapter.parsed = parsed
        system_prompt = agents_adapter.to_system_prompt()

        # Create .cursorrules with the content
        cursor_adapter = CursorRulesAdapter(cursorrules_file)
        # Manually set the content since we're translating from AGENTS.md
        cursorrules_file.write_text(system_prompt)

        cursor_content = cursorrules_file.read_text()
        cursor_tokens = len(cursor_content.split())
        print(f"   ✅ Created: {cursorrules_file}")
        print(f"   📏 Size: {len(cursor_content)} chars, ~{cursor_tokens} tokens")
        print(f"\n   Preview:")
        print("   " + "-" * 66)
        for line in cursor_content.split("\n")[:10]:
            print(f"   {line}")
        print("   ...")
        print("   " + "-" * 66)

        # Step 4: Convert to .clinerules
        print("\n🎯 Step 4: Converting to .clinerules (Cline extension)...")
        clinerules_file = tmppath / ".clinerules"

        # Create .clinerules with the same content
        cline_adapter = ClineRulesAdapter(clinerules_file)
        clinerules_file.write_text(system_prompt)

        cline_content = clinerules_file.read_text()
        cline_tokens = len(cline_content.split())
        print(f"   ✅ Created: {clinerules_file}")
        print(f"   📏 Size: {len(cline_content)} chars, ~{cline_tokens} tokens")
        print(f"\n   Preview:")
        print("   " + "-" * 66)
        for line in cline_content.split("\n")[:10]:
            print(f"   {line}")
        print("   ...")
        print("   " + "-" * 66)

        # Step 5: Compare formats
        print("\n📊 Step 5: Format Comparison")
        print("=" * 70)

        original_tokens = len(original_content.split())

        formats = [
            ("AGENTS.md (original)", original_tokens),
            (".cursorrules", cursor_tokens),
            (".clinerules", cline_tokens),
        ]

        print(f"\n{'Format':<25} {'Tokens':>10} {'Overhead':>10}")
        print("-" * 70)
        for format_name, tokens in formats:
            overhead = ((tokens - original_tokens) / original_tokens * 100)
            overhead_str = f"{overhead:+.1f}%" if format_name != "AGENTS.md (original)" else "baseline"
            print(f"{format_name:<25} {tokens:>10,} {overhead_str:>10}")

        # Step 6: Format validation
        print("\n✅ Step 6: Format Validation")
        print("=" * 70)

        print("\n   Validating generated files:")

        # Validate .cursorrules
        if cursorrules_file.exists() and len(cursor_content) > 0:
            print(f"   ✅ .cursorrules: Valid (contains {cursor_tokens} tokens)")
        else:
            print(f"   ❌ .cursorrules: Invalid")

        # Validate .clinerules
        if clinerules_file.exists() and len(cline_content) > 0:
            print(f"   ✅ .clinerules: Valid (contains {cline_tokens} tokens)")
        else:
            print(f"   ❌ .clinerules: Invalid")

        # Step 7: Use Case - Deploy Everywhere
        print("\n" + "=" * 70)
        print("🚀 Use Case: One Source → Deploy Everywhere")
        print("=" * 70)

        print("""
The translation workflow enables:

1. 📝 Write once in your preferred format (e.g., AGENTS.md)
2. 🔄 Auto-convert to all formats:
   - .cursorrules for Cursor IDE
   - .clinerules for Cline extension
   - (easily extensible to other formats)
3. ✅ No manual synchronization
4. ✅ No copy-paste errors
5. ✅ Single source of truth

Example CLI workflow:
  $ uacs skills convert --to cursorrules
  $ uacs skills convert --to clinerules

Or use the Python API:
  from uacs import UACS
  from pathlib import Path

  uacs = UACS(Path.cwd())
  uacs.convert_format("AGENTS.md", ".cursorrules")
  uacs.convert_format("AGENTS.md", ".clinerules")
        """)

        # Step 8: Summary
        print("\n" + "=" * 70)
        print("📊 Translation Summary")
        print("=" * 70)

        print(f"""
✅ Successfully demonstrated:
   1. Parsed AGENTS.md → extracted project context
   2. Converted to .cursorrules → {cursor_tokens:,} tokens
   3. Converted to .clinerules → {cline_tokens:,} tokens
   4. Validated all output formats

🎯 Key Benefits:
   - Single source of truth (AGENTS.md)
   - Automatic format conversion
   - Consistent project context across tools
   - Extensible to new formats via adapter pattern

🔧 Implementation:
   - All adapters extend BaseFormatAdapter
   - Registry pattern for auto-discovery
   - System prompt generation from parsed content
   - File pattern matching for auto-detection
        """)

        print("\n" + "=" * 70)
        print("✅ Multi-format translation demo complete!")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

