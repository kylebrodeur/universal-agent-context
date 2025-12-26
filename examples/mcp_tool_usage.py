"""
Example: MCP Tool Usage

This script demonstrates how to use the UACS MCP tools programmatically.
These are the same tools exposed by the 'uacs serve' command.
"""

import sys
import asyncio
from pathlib import Path

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the tool implementation directly
from uacs.protocols.mcp.skills_server import list_skills, read_skill

async def main():
    print("🛠️  Testing MCP Tools...")
    
    # 1. List Skills
    print("\n📋 Calling 'list_skills' tool...")
    try:
        # In a real MCP server, this is called via JSON-RPC
        # Here we call the implementation directly
        skills = await list_skills()
        
        print(f"Found {len(skills)} skills.")
        for skill in skills:
            print(f"  - {skill['name']}: {skill['description']}")
            
    except Exception as e:
        print(f"Error listing skills: {e}")
        
    # 2. Read a Skill (if any exist)
    # We'll try to read a hypothetical 'test-skill' or just skip
    skill_name = "test-skill"
    print(f"\n📖 Calling 'read_skill' for '{skill_name}'...")
    try:
        skill_content = await read_skill(skill_name)
        print("Result:", skill_content[:100] + "...")
    except Exception as e:
        print(f"Expected error (skill not found): {e}")

if __name__ == "__main__":
    asyncio.run(main())
