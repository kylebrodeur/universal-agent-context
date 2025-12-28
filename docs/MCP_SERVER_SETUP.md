# UACS MCP Server Setup Guide

This guide explains how to install and configure the Universal Agent Context System (UACS) MCP server for use with Claude Desktop and other MCP clients.

## Installation Methods

### 1. Python Package (Recommended for Developers)

Install via pip:

```bash
pip install universal-agent-context
```

**Running the Server:**

To run the server cleanly (without log output interfering with the MCP protocol), use:

> **Note:** We use `python -m uacs.mcp_server_entry` instead of `uacs serve` because MCP communicates over `stdin`/`stdout`. Any extra output (like "Starting server..." logs) will break the JSON-RPC protocol connection.

```bash
python -m uacs.mcp_server_entry
```

### 2. UVX (One-liner)

You can run the server directly without installing it first using `uvx`:

```bash
uvx --from universal-agent-context python -m uacs.mcp_server_entry
```

### 3. Docker

Build the image:

```bash
docker build -f Dockerfile.mcp-server -t uacs-mcp-server .
```

Run the server:

```bash
docker run -i --rm uacs-mcp-server
```

### 4. Standalone Binary

If you have built the binary using `scripts/build_mcp_server.py`, you can run it directly:

```bash
./dist/uacs-mcp-server
```

## Configuration for Claude Desktop

To use UACS with Claude Desktop, add the server configuration to your `claude_desktop_config.json`.

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration Examples

**Using UVX (Easiest):**

```json
{
  "mcpServers": {
    "uacs": {
      "command": "uvx",
      "args": [
        "--from",
        "universal-agent-context",
        "python",
        "-m",
        "uacs.mcp_server_entry"
      ]
    }
  }
}
```

**Using Python (Virtual Environment):**

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "-m",
        "uacs.mcp_server_entry"
      ]
    }
  }
}
```

**Using Docker:**

```json
{
  "mcpServers": {
    "uacs": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/path/to/your/project:/project",
        "uacs-mcp-server"
      ]
    }
  }
}
```
*Note: For Docker, you may need to mount your project directory to allow the server to access your files.*

**Using Binary:**

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/path/to/uacs-mcp-server",
      "args": []
    }
  }
}
```

## Verification

To verify the server is working:

1. Restart Claude Desktop.
2. Look for the 🔌 icon in the top right.
3. You should see "uacs" listed as a connected server.
4. You can now use tools like `skills_list`, `context_stats`, etc.
