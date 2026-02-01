#!/usr/bin/env python3
"""Demo script for UACS Context Graph Visualizer.

This script demonstrates how to use the visualization server
with sample context data.

Usage:
    python examples/visualization_demo.py

Then open your browser to: http://localhost:8081
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs.context.shared_context import SharedContextManager
from uacs.visualization.web_server import VisualizationServer
import uvicorn


async def populate_sample_data(manager: SharedContextManager):
    """Populate context manager with sample data.

    Args:
        manager: SharedContextManager instance
    """
    print("Adding sample context entries...")

    # Add entries with various topics and quality levels
    manager.add_entry(
        "Implemented user authentication with JWT tokens and bcrypt password hashing",
        agent="claude",
        topics=["auth", "security", "backend"],
    )

    manager.add_entry(
        "Created unit tests for authentication service\n```python\ndef test_login():\n    assert login('user', 'pass') == True\n```",
        agent="copilot",
        topics=["testing", "auth"],
    )

    manager.add_entry(
        "Reviewed database schema for user tables",
        agent="gemini",
        topics=["database", "review"],
    )

    manager.add_entry(
        "Fixed SQL injection vulnerability in search endpoint",
        agent="claude",
        topics=["security", "bugfix"],
        references=[],
    )

    manager.add_entry(
        "Updated API documentation for new endpoints",
        agent="copilot",
        topics=["documentation", "api"],
    )

    manager.add_entry(
        "Implemented caching layer with Redis for session management",
        agent="claude",
        topics=["performance", "caching", "backend"],
    )

    manager.add_entry(
        "Error in deployment",  # Low quality entry
        agent="system",
        topics=["deployment"],
    )

    manager.add_entry(
        "Analyzed performance bottlenecks in API response times",
        agent="gemini",
        topics=["performance", "optimization"],
    )

    manager.add_entry(
        "Designed new user dashboard with React components",
        agent="claude",
        topics=["frontend", "ui", "design"],
    )

    manager.add_entry(
        "Configured CI/CD pipeline with GitHub Actions for automated testing and deployment",
        agent="copilot",
        topics=["devops", "ci-cd", "automation"],
    )

    # Add a duplicate to test deduplication
    manager.add_entry(
        "Implemented user authentication with JWT tokens and bcrypt password hashing",
        agent="claude",
        topics=["auth", "security"],
    )

    print(f"✓ Added entries (duplicates were automatically prevented)")

    # Get statistics
    stats = manager.get_stats()
    print(f"\nContext Statistics:")
    print(f"  Entries: {stats['entry_count']}")
    print(f"  Total Tokens: {stats['total_tokens']}")
    print(f"  Avg Quality: {stats['avg_quality']}")
    print(f"  Storage: {stats['storage_size_mb']:.2f} MB")


async def main():
    """Main demo function."""
    print("=" * 60)
    print("UACS Context Graph Visualizer - Demo")
    print("=" * 60)
    print()

    # Setup storage path
    storage_path = Path.cwd() / ".state" / "context_demo"
    storage_path.mkdir(parents=True, exist_ok=True)

    print(f"Storage path: {storage_path}")
    print()

    # Initialize context manager
    context_manager = SharedContextManager(storage_path=storage_path)

    # Populate with sample data
    await populate_sample_data(context_manager)

    print()
    print("=" * 60)
    print("Starting Visualization Server")
    print("=" * 60)
    print()
    print("✓ Web UI available at: http://localhost:8081")
    print("✓ WebSocket endpoint: ws://localhost:8081/ws")
    print()
    print("Available views:")
    print("  1. Conversation Flow - Interactive context graph")
    print("  2. Token Dashboard - Real-time token statistics")
    print("  3. Deduplication - Duplicate content analysis")
    print("  4. Quality Distribution - Content quality metrics")
    print("  5. Topic Clusters - Topic-based visualization")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Create and start visualization server
    viz_server = VisualizationServer(
        context_manager,
        host="localhost",
        port=8081
    )

    config = uvicorn.Config(
        viz_server.app,
        host="localhost",
        port=8081,
        log_level="info",
    )

    server = uvicorn.Server(config)

    try:
        await server.serve()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print("✓ Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user")
        sys.exit(0)
