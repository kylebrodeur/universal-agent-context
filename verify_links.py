#!/usr/bin/env python3
"""Verify all cross-reference links in documentation."""

import re
from pathlib import Path

def extract_markdown_links(content):
    """Extract all markdown links from content."""
    # Match [text](link) format
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.findall(pattern, content)

def verify_links(base_path):
    """Verify all links in documentation files."""
    docs_to_check = [
        "README.md",
        "docs/MIGRATION.md",
        "docs/API_REFERENCE.md",
        "QUICKSTART.md",
        "CHANGELOG.md"
    ]

    all_links = {}
    errors = []

    print("Checking documentation files for links...\n")

    for doc_file in docs_to_check:
        doc_path = base_path / doc_file
        if not doc_path.exists():
            errors.append(f"❌ {doc_file} does not exist")
            continue

        content = doc_path.read_text()
        links = extract_markdown_links(content)
        all_links[doc_file] = links

        print(f"📄 {doc_file}: {len(links)} links found")

        # Verify each link
        for text, link in links:
            # Skip external links (http/https)
            if link.startswith('http://') or link.startswith('https://'):
                continue

            # Skip anchors within the same file
            if link.startswith('#'):
                continue

            # Handle relative paths
            if '/' in link or link.endswith('.md'):
                # Remove anchor if present
                link_path = link.split('#')[0]

                # Resolve relative to document location
                if doc_file.startswith('docs/'):
                    # Link from docs/ directory
                    if link_path.startswith('../'):
                        # Link to parent directory
                        target_path = base_path / link_path.replace('../', '')
                    elif link_path.startswith('./'):
                        # Link within docs/
                        target_path = base_path / 'docs' / link_path.replace('./', '')
                    else:
                        # Link within docs/
                        target_path = base_path / 'docs' / link_path
                else:
                    # Link from root directory
                    if link_path.startswith('./'):
                        target_path = base_path / link_path.replace('./', '')
                    else:
                        target_path = base_path / link_path

                # Check if target exists
                if not target_path.exists():
                    errors.append(f"❌ {doc_file}: Broken link [{text}]({link}) -> {target_path}")

    print(f"\n{'='*60}")
    if errors:
        print(f"\n❌ Found {len(errors)} broken links:\n")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ All cross-reference links are valid!")

        # Print summary
        print(f"\nSummary:")
        total_links = sum(len(links) for links in all_links.values())
        print(f"  Total links checked: {total_links}")
        print(f"  Files checked: {len(docs_to_check)}")

        # Print key cross-references
        print(f"\nKey v0.3.0 cross-references:")
        key_links = [
            ("README.md → MIGRATION.md", "docs/MIGRATION.md"),
            ("README.md → API_REFERENCE.md", "docs/API_REFERENCE.md"),
            ("README.md → HOOKS_GUIDE.md", ".claude-plugin/HOOKS_GUIDE.md"),
            ("MIGRATION.md → API_REFERENCE.md", "API_REFERENCE.md"),
            ("MIGRATION.md → HOOKS_GUIDE.md", "../.claude-plugin/HOOKS_GUIDE.md"),
            ("API_REFERENCE.md → MIGRATION.md", "MIGRATION.md"),
            ("QUICKSTART.md → MIGRATION.md", "docs/MIGRATION.md"),
        ]

        for desc, link_target in key_links:
            found = False
            for doc, links in all_links.items():
                for text, link in links:
                    if link_target in link:
                        found = True
                        print(f"  ✓ {desc}")
                        break
                if found:
                    break
            if not found:
                print(f"  ⚠️  {desc} - NOT FOUND (may need to add)")

        return True

if __name__ == "__main__":
    base_path = Path(__file__).parent
    success = verify_links(base_path)
    exit(0 if success else 1)
