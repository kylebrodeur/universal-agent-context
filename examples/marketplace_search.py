"""
Example: Marketplace Search

This script demonstrates how to search for skills and MCP servers
using the UACS marketplace API.
"""

import sys
import asyncio
from pathlib import Path

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs import UACS

async def main():
    print("🏪 Initializing UACS Marketplace...")

    # Initialize UACS facade
    uacs = UACS(Path.cwd())

    query = "python"
    print(f"\n🔍 Searching for '{query}' skills...")

    # Search for skills
    # Note: This requires internet access to query remote repositories
    # If no remote repos are configured or accessible, it might return empty
    try:
        results = await uacs.search(query, package_type="skills")

        if not results:
            print("No results found (check network or configured repositories).")
        else:
            print(f"Found {len(results)} packages:")
            for pkg in results:
                print(f"  - {pkg.name}: {pkg.description[:60]}...")

    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
