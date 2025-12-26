"""
Example: Memory Usage

This script demonstrates how to use the persistent memory system
to store and retrieve long-term information.
"""

import sys
import shutil
from pathlib import Path

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs.memory.simple_memory import SimpleMemoryStore

def main():
    print("🧠 Initializing Memory Store...")
    
    # Use a temporary directory for this example
    temp_dir = Path(".temp_memory_example")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # Initialize store with project path
        store = SimpleMemoryStore(project_path=temp_dir)
        store.init_storage("project")
        
        print("\n💾 Storing memories...")
        
        # Add some memories
        store.add_memory(
            content="The user prefers Python for backend development.",
            tags=["preference", "tech-stack"],
            scope="project"
        )
        
        store.add_memory(
            content="The project uses Poetry for dependency management.",
            tags=["tech-stack", "tooling"],
            scope="project"
        )
        
        store.add_memory(
            content="Deployments are done via GitHub Actions.",
            tags=["devops", "deployment"],
            scope="project"
        )
        
        print("\n🔍 Searching memories...")
        
        # Search by text
        query = "tech stack"
        print(f"Query: '{query}'")
        results = store.search(query)
        
        for mem in results:
            print(f"  - [{mem.scope}] {mem.content} (tags: {mem.tags})")
            
        # Search by tag
        tag = "devops"
        print(f"\nQuery Tag: '{tag}'")
        results = store.search(tag) # Simple search matches tags too
        
        for mem in results:
            print(f"  - [{mem.scope}] {mem.content}")
            
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
