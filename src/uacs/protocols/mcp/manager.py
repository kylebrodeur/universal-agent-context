"""MCP Server Manager."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class McpServerConfig:
    """Configuration for an MCP server."""

    name: str
    command: str
    args: list[str]
    env: dict[str, str]
    enabled: bool = True


class McpManager:
    """Manages MCP server configurations."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize MCP manager.

        Args:
            config_dir: Directory to store configuration
        """
        self.config_dir = config_dir or Path.home() / ".uacs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "mcp_servers.json"
        self.servers: dict[str, McpServerConfig] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text())
                for name, config in data.items():
                    self.servers[name] = McpServerConfig(**config)
            except Exception as e:
                print(f"Error loading MCP config: {e}")

    def _save_config(self):
        """Save configuration to file."""
        data = {name: asdict(config) for name, config in self.servers.items()}
        self.config_file.write_text(json.dumps(data, indent=2))

    def add_server(
        self,
        name: str,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
    ):
        """Add or update an MCP server configuration."""
        self.servers[name] = McpServerConfig(
            name=name, command=command, args=args, env=env or {}
        )
        self._save_config()

    def remove_server(self, name: str):
        """Remove an MCP server configuration."""
        if name in self.servers:
            del self.servers[name]
            self._save_config()

    def list_servers(self) -> list[McpServerConfig]:
        """List all configured servers."""
        return list(self.servers.values())

    def get_server(self, name: str) -> McpServerConfig | None:
        """Get a specific server configuration."""
        return self.servers.get(name)


__all__ = ["McpManager", "McpServerConfig"]
