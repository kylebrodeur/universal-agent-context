"""UACS Claude Code plugin management."""

from pathlib import Path
import shutil
import json
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="plugin",
    help="Manage Claude Code plugin installation",
    no_args_is_help=True,
)

console = Console()


@app.command()
def install():
    """Install UACS Claude Code plugin.
    
    Installs hooks and configuration for automatic context tracking
    in Claude Code sessions.
    """
    try:
        import uacs
        
        # Find plugin files in package
        package_root = Path(uacs.__file__).parent
        plugin_source = package_root / ".claude-plugin"
        
        if not plugin_source.exists():
            console.print("[red]Error:[/red] Plugin files not found in package")
            console.print(f"Expected at: {plugin_source}")
            raise typer.Exit(1)
        
        # Claude Code plugin directory
        claude_dir = Path.home() / ".claude"
        hooks_dir = claude_dir / "hooks"
        
        # Create directories
        claude_dir.mkdir(exist_ok=True)
        hooks_dir.mkdir(exist_ok=True)
        
        # Copy hooks
        hooks_source = plugin_source / "hooks"
        if hooks_source.exists():
            for hook_file in hooks_source.glob("*.py"):
                dest = hooks_dir / hook_file.name
                shutil.copy2(hook_file, dest)
                dest.chmod(0o755)  # Make executable
                console.print(f"[green]✓[/green] Installed hook: {hook_file.name}")
        
        # Handle plugin.json
        plugin_json = plugin_source / "plugin-semantic.json"
        claude_plugin = claude_dir / "plugin.json"

        # Load and update paths in config
        new_config = json.loads(plugin_json.read_text())

        # Update hook paths to absolute paths
        for hook_type, hook_configs in new_config.get("hooks", {}).items():
            for config in hook_configs:
                for hook in config.get("hooks", []):
                    if "command" in hook:
                        # Replace relative path with absolute path to ~/.claude/hooks/
                        cmd = hook["command"]
                        if ".claude-plugin/hooks/" in cmd:
                            hook_file = cmd.split("/")[-1]
                            hook["command"] = f"python3 {hooks_dir}/{hook_file}"

        if claude_plugin.exists():
            # Merge with existing
            existing = json.loads(claude_plugin.read_text())

            # Merge hooks
            if "hooks" not in existing:
                existing["hooks"] = {}
            for hook_type, hooks in new_config.get("hooks", {}).items():
                if hook_type not in existing["hooks"]:
                    existing["hooks"][hook_type] = []
                existing["hooks"][hook_type].extend(hooks)

            claude_plugin.write_text(json.dumps(existing, indent=2))
            console.print("[green]✓[/green] Merged with existing plugin.json")
        else:
            # Create new
            claude_plugin.write_text(json.dumps(new_config, indent=2))
            console.print("[green]✓[/green] Created plugin.json")
        
        # Success message
        console.print()
        console.print(Panel.fit(
            "[bold green]UACS Claude Code Plugin Installed![/bold green]\n\n"
            "The following hooks are now active:\n"
            "• [cyan]UserPromptSubmit[/cyan] - Captures user messages\n"
            "• [cyan]PostToolUse[/cyan] - Tracks tool executions\n"
            "• [cyan]SessionEnd[/cyan] - Extracts knowledge\n\n"
            "Your Claude Code sessions will now automatically:\n"
            "✓ Track conversations with semantic structure\n"
            "✓ Extract decisions and conventions\n"
            "✓ Enable natural language search\n\n"
            "[dim]Restart Claude Code for changes to take effect[/dim]",
            title="✨ Installation Complete",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def uninstall():
    """Uninstall UACS Claude Code plugin."""
    try:
        claude_dir = Path.home() / ".claude"
        hooks_dir = claude_dir / "hooks"
        
        # Remove hooks
        removed = []
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("uacs_*.py"):
                hook_file.unlink()
                removed.append(hook_file.name)
        
        if removed:
            console.print(f"[green]✓[/green] Removed {len(removed)} hooks")
            for name in removed:
                console.print(f"  • {name}")
        else:
            console.print("[yellow]No UACS hooks found[/yellow]")
        
        # Note about plugin.json
        console.print()
        console.print("[dim]Note: plugin.json was not modified[/dim]")
        console.print("[dim]Remove UACS hooks manually if needed[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def status():
    """Check UACS plugin installation status."""
    claude_dir = Path.home() / ".claude"
    hooks_dir = claude_dir / "hooks"
    plugin_json = claude_dir / "plugin.json"
    
    console.print("[bold]UACS Plugin Status[/bold]\n")
    
    # Check hooks
    if hooks_dir.exists():
        uacs_hooks = list(hooks_dir.glob("uacs_*.py"))
        if uacs_hooks:
            console.print(f"[green]✓[/green] Hooks installed: {len(uacs_hooks)}")
            for hook in uacs_hooks:
                console.print(f"  • {hook.name}")
        else:
            console.print("[yellow]○[/yellow] No hooks installed")
    else:
        console.print("[yellow]○[/yellow] Hooks directory not found")
    
    console.print()
    
    # Check plugin.json
    if plugin_json.exists():
        console.print("[green]✓[/green] plugin.json exists")
        try:
            config = json.loads(plugin_json.read_text())
            has_uacs = any("uacs" in str(h).lower() for h in config.get("hooks", {}).values())
            if has_uacs:
                console.print("  [green]✓[/green] UACS hooks configured")
            else:
                console.print("  [yellow]○[/yellow] UACS hooks not configured")
        except Exception as e:
            console.print(f"  [red]✗[/red] Error reading: {e}")
    else:
        console.print("[yellow]○[/yellow] plugin.json not found")


__all__ = ["app"]
