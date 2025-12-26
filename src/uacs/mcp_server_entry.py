"""Entry point for UACS MCP Server (PyInstaller target)."""
import asyncio
import sys
from uacs.protocols.mcp.skills_server import main

if __name__ == "__main__":
    # Ensure we're running in an async loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
