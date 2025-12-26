"""Visualization for shared context and agent interactions.

Provides real-time terminal visualizations of:
1. Context flow between agents
2. Token usage and compression
3. Agent dependency graphs
4. Memory efficiency
"""

import time
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree


class ContextVisualizer:
    """Real-time visualization of shared context."""

    def __init__(self, console: Console | None = None):
        """Initialize visualizer.

        Args:
            console: Rich console instance
        """
        self.console = console or Console()

    def render_context_graph(self, graph: dict[str, Any]) -> Panel:
        """Render context graph as tree structure.

        Args:
            graph: Graph structure from SharedContextManager

        Returns:
            Rich Panel with graph visualization
        """
        tree = Tree("🧠 Shared Context Graph")

        # Group nodes by type
        entries = [n for n in graph["nodes"] if n["type"] == "entry"]
        summaries = [n for n in graph["nodes"] if n["type"] == "summary"]

        # Add entry branch
        if entries:
            entries_branch = tree.add("📝 Context Entries")
            for entry in entries:
                agent_icon = self._get_agent_icon(entry.get("agent", "unknown"))
                entries_branch.add(
                    f"{agent_icon} {entry['id']} "
                    f"({entry['tokens']} tokens) "
                    f"[dim]{entry['timestamp'][:19]}[/dim]"
                )

        # Add summary branch
        if summaries:
            summaries_branch = tree.add("🗜️  Summaries")
            for summary in summaries:
                summaries_branch.add(
                    f"📦 {summary['id']} "
                    f"({summary['entry_count']} entries, "
                    f"{summary['tokens_saved']} tokens saved)"
                )

        # Add edges info
        if graph["edges"]:
            edges_branch = tree.add(f"🔗 References ({len(graph['edges'])})")
            for edge in graph["edges"][:5]:  # Show first 5
                edges_branch.add(
                    f"{edge['source']} → {edge['target']} [dim]({edge['type']})[/dim]"
                )

        return Panel(
            tree, title="Context Relationships", border_style="cyan", box=box.ROUNDED
        )

    def render_stats_table(self, stats: dict[str, Any]) -> Table:
        """Render context statistics as table.

        Args:
            stats: Statistics from SharedContextManager

        Returns:
            Rich Table with statistics
        """
        table = Table(
            title="💾 Context Statistics",
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 2),
        )

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Entries", str(stats["entry_count"]))
        table.add_row("Summaries", str(stats["summary_count"]))
        table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
        table.add_row("Tokens Saved", f"{stats['tokens_saved']:,}")
        table.add_row("Compression", stats["compression_ratio"])
        table.add_row("Storage", f"{stats['storage_size_mb']:.2f} MB")

        return table

    def render_agent_flow(self, entries: list) -> Panel:
        """Render agent interaction flow.

        Args:
            entries: List of context entries

        Returns:
            Rich Panel with flow visualization
        """
        flow_lines = []

        for i, entry in enumerate(entries[-10:]):  # Last 10 entries
            agent = entry.get("agent", "unknown")
            agent_icon = self._get_agent_icon(agent)
            tokens = entry.get("token_estimate", 0)

            # Create flow arrow
            arrow = "  └─>" if i > 0 else "  ┌─>"
            flow_lines.append(
                f"{arrow} {agent_icon} [bold]{agent}[/bold] "
                f"[dim]({tokens} tokens)[/dim]"
            )

        flow_text = "\n".join(flow_lines) if flow_lines else "[dim]No entries yet[/dim]"

        return Panel(
            flow_text,
            title="🔄 Agent Interaction Flow",
            border_style="blue",
            box=box.ROUNDED,
        )

    def render_token_meter(self, used_tokens: int, max_tokens: int = 8000) -> Panel:
        """Render token usage meter.

        Args:
            used_tokens: Current token count
            max_tokens: Maximum tokens

        Returns:
            Rich Panel with token meter
        """
        percentage = (used_tokens / max_tokens) * 100
        bar_width = 40
        filled = int((percentage / 100) * bar_width)

        # Choose color based on usage
        if percentage < 50:
            color = "green"
        elif percentage < 80:
            color = "yellow"
        else:
            color = "red"

        bar = f"[{color}]{'█' * filled}[/]{color}{'░' * (bar_width - filled)}"

        meter_text = f"""
{bar}

Used: {used_tokens:,} / {max_tokens:,} tokens ({percentage:.1f}%)
Remaining: {max_tokens - used_tokens:,} tokens
"""

        return Panel(
            meter_text.strip(),
            title="🎯 Token Budget",
            border_style=color,
            box=box.ROUNDED,
        )

    def render_dashboard(
        self,
        graph: dict[str, Any],
        stats: dict[str, Any],
        token_usage: dict[str, int] | None = None,
    ) -> Layout:
        """Render complete dashboard layout.

        Args:
            graph: Context graph
            stats: Context statistics
            token_usage: Token usage info

        Returns:
            Rich Layout with full dashboard
        """
        layout = Layout()

        # Split into sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

        # Header
        layout["header"].update(
            Panel(Align.center("🤖 Multi-Agent Context Dashboard"), style="bold cyan")
        )

        # Body - split into left and right
        layout["body"].split_row(Layout(name="left"), Layout(name="right"))

        # Left side - graph and flow
        layout["left"].split_column(Layout(name="graph"), Layout(name="flow"))

        layout["graph"].update(self.render_context_graph(graph))

        if graph["nodes"]:
            layout["flow"].update(self.render_agent_flow(graph["nodes"]))

        # Right side - stats and tokens
        layout["right"].split_column(Layout(name="stats"), Layout(name="tokens"))

        layout["stats"].update(Panel(self.render_stats_table(stats)))

        if token_usage:
            layout["tokens"].update(
                self.render_token_meter(
                    token_usage.get("used", 0), token_usage.get("max", 8000)
                )
            )

        # Footer
        layout["footer"].update(
            Panel(
                "[dim]Press Ctrl+C to exit | Data updates every 2 seconds[/dim]",
                style="dim",
            )
        )

        return layout

    def live_dashboard(self, context_manager, update_interval: float = 2.0):
        """Run live updating dashboard.

        Args:
            context_manager: SharedContextManager instance
            update_interval: Seconds between updates
        """
        with Live(
            self.render_dashboard(
                context_manager.get_context_graph(),
                context_manager.get_stats(),
                {
                    "used": sum(
                        e.token_estimate for e in context_manager.entries.values()
                    )
                },
            ),
            refresh_per_second=1,
            screen=True,
        ) as live:
            try:
                while True:
                    time.sleep(update_interval)

                    # Update dashboard
                    graph = context_manager.get_context_graph()
                    stats = context_manager.get_stats()
                    token_usage = {
                        "used": sum(
                            e.token_estimate for e in context_manager.entries.values()
                        ),
                        "max": 8000,
                    }

                    live.update(self.render_dashboard(graph, stats, token_usage))
            except KeyboardInterrupt:
                pass

    def _get_agent_icon(self, agent: str) -> str:
        """Get icon for agent type.

        Args:
            agent: Agent name

        Returns:
            Icon emoji
        """
        icons = {
            "claude": "🔵",
            "gemini": "🟣",
            "copilot": "🟢",
            "openai": "🟡",
            "orchestrator": "🎭",
        }
        return icons.get(agent.lower(), "⚪")

    def render_compression_viz(
        self, before_tokens: int, after_tokens: int, method: str = "summary"
    ) -> Panel:
        """Visualize compression effect.

        Args:
            before_tokens: Tokens before compression
            after_tokens: Tokens after compression
            method: Compression method used

        Returns:
            Rich Panel showing compression
        """
        savings = before_tokens - after_tokens
        percentage = (savings / before_tokens * 100) if before_tokens > 0 else 0

        viz = f"""
Before:  {"█" * int(before_tokens / 100)} ({before_tokens:,} tokens)
After:   {"█" * int(after_tokens / 100)} ({after_tokens:,} tokens)

[green]Saved: {savings:,} tokens ({percentage:.1f}%)[/green]
Method: {method}
"""

        return Panel(
            viz.strip(),
            title="🗜️  Compression Effect",
            border_style="green",
            box=box.ROUNDED,
        )
