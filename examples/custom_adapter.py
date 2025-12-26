"""
Example: Custom Format Adapter

This script demonstrates how to create and register a custom format adapter
to support a hypothetical 'MY_CONFIG.txt' file format.
"""

import sys
from pathlib import Path
from typing import List

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs.adapters.base import BaseFormatAdapter, ParsedContent
from uacs.adapters.registry import FormatAdapterRegistry
from uacs.context.unified_context import UnifiedContextAdapter

# 1. Define the Custom Adapter
@FormatAdapterRegistry.register
class MyConfigAdapter(BaseFormatAdapter):
    """Adapter for MY_CONFIG.txt files."""
    
    FORMAT_NAME = "my_config"
    SUPPORTED_FILES = ["MY_CONFIG.txt"]
    
    def parse(self, content: str) -> ParsedContent:
        """Parse the custom config file."""
        print(f"  [MyConfigAdapter] Parsing content ({len(content)} chars)...")
        
        # Simple parsing logic: treat lines starting with 'RULE:' as instructions
        instructions = []
        for line in content.splitlines():
            if line.startswith("RULE:"):
                instructions.append(line.replace("RULE:", "").strip())
                
        return ParsedContent(
            instructions="\n".join(instructions),
            metadata={"source": "custom_adapter"}
        )
        
    def to_system_prompt(self) -> str:
        """Convert to system prompt format."""
        if not self.parsed:
            return ""
        return f"### MY CUSTOM RULES\n{self.parsed.instructions}"

def main():
    print("🔧 Testing Custom Adapter...")
    
    # 2. Create a dummy config file
    config_file = Path("MY_CONFIG.txt")
    config_file.write_text(
        "This is a custom config file.\n"
        "RULE: Always be polite.\n"
        "RULE: Use metric units.\n"
        "Ignore this line."
    )
    
    try:
        # 3. Initialize UnifiedContextAdapter
        # It automatically discovers registered adapters and files
        print("\n📥 Loading context...")
        adapter = UnifiedContextAdapter()
        
        # 4. Verify our content was loaded
        prompt_data = adapter.build_agent_prompt("Hello", "test_agent")
        
        print("\n📄 Generated System Prompt:")
        print("-" * 40)
        print(prompt_data.system_prompt)
        print("-" * 40)
        
        if "### MY CUSTOM RULES" in prompt_data.system_prompt:
            print("\n✅ Success! Custom adapter content found in prompt.")
        else:
            print("\n❌ Failure. Custom content not found.")
            
    finally:
        # Cleanup
        if config_file.exists():
            config_file.unlink()

if __name__ == "__main__":
    main()
