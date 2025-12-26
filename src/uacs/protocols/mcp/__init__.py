"""MCP protocol components."""

__all__ = ["McpManager", "McpServerConfig"]

from uacs.protocols.mcp.manager import McpManager, McpServerConfig

# Note: McpToolAdapter (client utils) remains in multi-agent-cli
# as it depends on google-adk which is a MAOS dependency
