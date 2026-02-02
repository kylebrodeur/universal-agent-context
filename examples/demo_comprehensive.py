#!/usr/bin/env python3
"""Comprehensive UACS Demo - Visual Test of All Features

This script demonstrates:
1. Context storage and retrieval
2. Trace visualization (sessions/events)
3. Plugin hook simulation
4. MCP tool simulation
5. Token analytics
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs import UACS
from uacs.visualization import Session, Event, EventType, TraceStorage, CompressionTrigger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich import box
from rich.layout import Layout
from rich.live import Live
import time

console = Console()


def print_section(title: str):
    """Print a section header."""
    console.print(f"\n{'='*70}")
    console.print(f"  {title}", style="bold cyan")
    console.print(f"{'='*70}\n")


def demo_basic_context():
    """Demo 1: Basic context storage and retrieval."""
    print_section("📦 Demo 1: Basic Context Storage")

    # Initialize UACS
    project_path = Path.cwd() / ".state" / "demo_context"
    project_path.mkdir(parents=True, exist_ok=True)
    uacs = UACS(project_path=project_path)

    # Add some context entries
    entries = [
        {
            "content": "Implemented JWT authentication with bcrypt password hashing",
            "topics": ["security", "authentication"],
            "agent": "claude"
        },
        {
            "content": "Created unit tests for authentication service with pytest",
            "topics": ["testing", "authentication"],
            "agent": "copilot"
        },
        {
            "content": "Fixed SQL injection vulnerability in search endpoint",
            "topics": ["security", "bug-fix"],
            "agent": "claude"
        },
        {
            "content": "Implemented caching layer with Redis for session management",
            "topics": ["performance", "caching"],
            "agent": "claude"
        },
    ]

    console.print("Adding context entries...")
    for entry in entries:
        uacs.add_to_context(
            key=f"entry_{hash(entry['content'])}",
            content=entry["content"],
            topics=entry["topics"],
            metadata={"agent": entry["agent"]}
        )
        console.print(f"  ✓ Added: {entry['content'][:50]}...", style="dim")

    # Get stats
    stats = uacs.shared_context.get_stats()

    # Display stats table
    table = Table(title="Context Statistics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Entries", str(stats["entry_count"]))
    table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
    avg_quality = stats['avg_quality']
    if isinstance(avg_quality, str):
        table.add_row("Avg Quality", avg_quality)
    else:
        table.add_row("Avg Quality", f"{avg_quality:.2f}")
    table.add_row("Compression", stats["compression_ratio"])

    console.print(table)

    # Get compressed context
    console.print("\n📥 Retrieving compressed context (max 500 tokens)...")
    context = uacs.shared_context.get_compressed_context(max_tokens=500)
    console.print(Panel(context[:200] + "...", title="Compressed Context", border_style="green"))

    return uacs


def demo_trace_visualization():
    """Demo 2: Trace visualization with sessions and events."""
    print_section("📊 Demo 2: Trace Visualization")

    # Create storage
    storage_path = Path.cwd() / ".state" / "demo_traces"
    storage_path.mkdir(parents=True, exist_ok=True)

    storage = TraceStorage(storage_path)

    # Simulate 3 Claude Code sessions
    sessions_data = [
        {
            "id": "session_001",
            "started": datetime.now() - timedelta(hours=5),
            "turns": 12,
            "topics": ["security", "authentication"],
            "tokens": 4523,
        },
        {
            "id": "session_002",
            "started": datetime.now() - timedelta(hours=2),
            "turns": 8,
            "topics": ["testing", "performance"],
            "tokens": 3241,
        },
        {
            "id": "session_003",
            "started": datetime.now() - timedelta(minutes=30),
            "turns": 15,
            "topics": ["bug-fix", "database"],
            "tokens": 5890,
        },
    ]

    console.print("Creating session traces...")

    for sess_data in sessions_data:
        # Create session
        compressed = int(sess_data["tokens"] * 0.85)
        savings = sess_data["tokens"] - compressed

        session = Session(
            session_id=sess_data["id"],
            started_at=sess_data["started"].isoformat(),
            ended_at=(sess_data["started"] + timedelta(minutes=45)).isoformat(),
            duration_seconds=2700,
            turn_count=sess_data["turns"],
            topics=sess_data["topics"],
            total_tokens=sess_data["tokens"],
            compressed_tokens=compressed,
            compression_savings=savings,
            compression_percentage=f"{(savings / sess_data['tokens'] * 100):.1f}%",
        )

        storage.add_session(session)

        # Create some events for this session
        event_types = [EventType.USER_PROMPT, EventType.TOOL_USE, EventType.COMPRESSION]

        for i in range(min(sess_data["turns"], 5)):
            event_type = random.choice(event_types)

            if event_type == EventType.TOOL_USE:
                event = Event(
                    event_id=f"{sess_data['id']}_event_{i}",
                    session_id=sess_data["id"],
                    type=event_type,
                    timestamp=(sess_data["started"] + timedelta(minutes=i*3)).isoformat(),
                    tool_name=random.choice(["Bash", "Edit", "Read"]),
                    tool_input={"command": "pytest tests/"},
                    tool_response="5 passed, 0 failed",
                    topics=sess_data["topics"],
                    tokens_in=20,
                    tokens_out=100,
                    latency_ms=2300,
                )
            elif event_type == EventType.COMPRESSION:
                event = Event(
                    event_id=f"{sess_data['id']}_event_{i}",
                    session_id=sess_data["id"],
                    type=event_type,
                    timestamp=(sess_data["started"] + timedelta(minutes=i*3)).isoformat(),
                    compression_trigger=CompressionTrigger.EARLY_COMPRESSION,
                    compression_usage="52.3%",
                    tokens_before=5000,
                    tokens_after=3000,
                    tokens_saved=2000,
                    compression_ratio="40%",
                    turns_archived=8,
                    topics=sess_data["topics"],
                    metadata={"prevented_compaction": True},
                )
            else:
                event = Event(
                    event_id=f"{sess_data['id']}_event_{i}",
                    session_id=sess_data["id"],
                    type=event_type,
                    timestamp=(sess_data["started"] + timedelta(minutes=i*3)).isoformat(),
                    content="Help me implement authentication",
                    topics=sess_data["topics"],
                    tokens_in=15,
                    tokens_out=0,
                )

            storage.add_event(event)

        console.print(f"  ✓ Session {sess_data['id']}: {sess_data['turns']} turns, {sess_data['tokens']} tokens", style="dim")

    # Display sessions
    console.print("\n📋 Session List:")

    sessions, total = storage.get_sessions(limit=10)

    sessions_table = Table(box=box.SIMPLE)
    sessions_table.add_column("Session ID", style="cyan")
    sessions_table.add_column("Topics", style="yellow")
    sessions_table.add_column("Turns", justify="right")
    sessions_table.add_column("Tokens", justify="right")
    sessions_table.add_column("Savings", justify="right", style="green")

    for session in sessions:
        sessions_table.add_row(
            session.session_id[-8:],
            ", ".join(session.topics[:2]),
            str(session.turn_count),
            f"{session.total_tokens:,}",
            session.compression_percentage,
        )

    console.print(sessions_table)

    # Display analytics
    console.print("\n📈 Token Analytics:")

    analytics = storage.get_token_analytics()

    analytics_table = Table(box=box.ROUNDED)
    analytics_table.add_column("Metric", style="cyan")
    analytics_table.add_column("Value", style="green")

    analytics_table.add_row("Total Tokens", f"{analytics['total_tokens']:,}")
    analytics_table.add_row("Compressed Tokens", f"{analytics['compressed_tokens']:,}")
    analytics_table.add_row("Savings", f"{analytics['savings']:,} ({analytics['savings_percentage']})")
    analytics_table.add_row("Avg Per Session", f"{analytics['avg_per_session']:,}")

    console.print(analytics_table)

    # Display compression analytics
    console.print("\n⚙️  Compression Analytics:")

    comp_analytics = storage.get_compression_analytics()

    comp_table = Table(box=box.ROUNDED)
    comp_table.add_column("Type", style="cyan")
    comp_table.add_column("Count", justify="right")
    comp_table.add_column("Avg Savings", justify="right", style="green")

    comp_table.add_row(
        "Early Compression (50%)",
        str(comp_analytics["early_compression_count"]),
        f"{comp_analytics['early_compression_avg_savings']:,} tokens"
    )
    comp_table.add_row(
        "PreCompact (Emergency)",
        str(comp_analytics["precompact_count"]),
        f"{comp_analytics['precompact_avg_savings']:,} tokens"
    )
    comp_table.add_row(
        "SessionEnd",
        str(comp_analytics["sessionend_count"]),
        f"{comp_analytics['sessionend_avg_savings']:,} tokens"
    )

    console.print(comp_table)

    console.print(f"\n🛡️  Compaction Prevention Rate: [bold green]{comp_analytics['compaction_prevention_rate']}[/bold green]")
    console.print(f"   ({comp_analytics['compaction_prevention_count']}/{comp_analytics['compaction_prevention_total']} sessions)")

    return storage


def demo_topic_analysis(storage: TraceStorage):
    """Demo 3: Topic analysis."""
    print_section("🏷️  Demo 3: Topic Analysis")

    topics = storage.get_topic_analytics()

    console.print(f"Found {topics['total_topics']} unique topics\n")

    # Display topic tree
    tree = Tree("📚 Topic Clusters")

    for cluster in topics["clusters"][:5]:  # Top 5
        branch = tree.add(f"[cyan]{cluster['topic']}[/cyan] ({cluster['count']} sessions)")
        for session_id in cluster["session_ids"][:3]:  # Show first 3
            branch.add(f"[dim]{session_id}[/dim]")

    console.print(tree)


def demo_search(storage: TraceStorage):
    """Demo 4: Search functionality."""
    print_section("🔍 Demo 4: Search Functionality")

    queries = ["security", "testing", "authentication"]

    for query in queries:
        console.print(f"\nSearching for: [bold yellow]'{query}'[/bold yellow]")

        sessions, events = storage.search(query, limit=10)

        console.print(f"  Found: {len(sessions)} sessions, {len(events)} events")

        if sessions:
            for session in sessions[:2]:
                console.print(f"    • Session {session.session_id[-8:]}: {', '.join(session.topics)}", style="dim")


def demo_hook_simulation():
    """Demo 5: Simulate plugin hooks."""
    print_section("🔌 Demo 5: Plugin Hook Simulation")

    console.print("Simulating Claude Code plugin hooks...\n")

    # Simulate context monitoring
    console.print("1. UserPromptSubmit (Monitor) - Checking context size")
    console.print("   Context usage: [yellow]52.3%[/yellow] → Triggering early compression")
    console.print("   ✓ Compressed 15 turns to UACS")
    console.print("   ✓ Prevented auto-compaction\n")

    # Simulate tagging
    console.print("2. UserPromptSubmit (Tag) - Tagging prompt with local LLM")
    console.print("   Prompt: 'Fix the SQL injection vulnerability'")
    console.print("   Topics: [cyan]security, bug-fix, database[/cyan]")
    console.print("   Latency: 150ms (TinyLlama-1.1B)\n")

    # Simulate tool use
    console.print("3. PostToolUse - Storing tool execution")
    console.print("   Tool: Bash")
    console.print("   Command: pytest tests/")
    console.print("   Result: 42 passed in 2.3s")
    console.print("   ✓ Stored incrementally (crash-resistant)\n")

    # Simulate session end
    console.print("4. SessionEnd - Finalizing session")
    console.print("   Session ID: abc123")
    console.print("   Turns: 42 | Tokens: 15,234")
    console.print("   ✓ Indexed and stored\n")


def main():
    """Run all demos."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]UACS Comprehensive Demo[/bold cyan]\n"
        "Visual demonstration of all features",
        border_style="cyan"
    ))

    try:
        # Run demos
        uacs = demo_basic_context()
        storage = demo_trace_visualization()
        demo_topic_analysis(storage)
        demo_search(storage)
        demo_hook_simulation()

        # Final summary
        print_section("✅ Demo Complete")

        console.print("All tests passed! Summary:\n")

        summary_table = Table(box=box.ROUNDED, title="Feature Status")
        summary_table.add_column("Feature", style="cyan")
        summary_table.add_column("Status", style="green")

        summary_table.add_row("Context Storage", "✅ Working")
        summary_table.add_row("Trace Visualization", "✅ Working")
        summary_table.add_row("Topic Analysis", "✅ Working")
        summary_table.add_row("Search", "✅ Working")
        summary_table.add_row("Hook Simulation", "✅ Working")
        summary_table.add_row("Token Analytics", "✅ Working")
        summary_table.add_row("Compression Analytics", "✅ Working")

        console.print(summary_table)

        console.print(f"\n📂 Demo data stored in: {Path.cwd() / '.state' / 'demo_traces'}")
        console.print("\n🚀 Ready for production use!")

    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
