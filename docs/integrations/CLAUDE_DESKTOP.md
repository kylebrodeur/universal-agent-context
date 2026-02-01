# UACS Integration with Claude Desktop

**Universal Agent Context System (UACS)** can be integrated with Claude Desktop as an MCP (Model Context Protocol) server, providing powerful context management, skills marketplace, and multi-format translation capabilities directly in your Claude conversations.

## Quick Start

Choose your installation method based on your needs:

| Method | Best For | Setup Time |
|--------|----------|------------|
| **Binary** (Recommended) | Quick setup, no dependencies | 2 minutes |
| **Docker** | Isolated environment, team sharing | 3 minutes |
| **Python Package** | Development, customization | 5 minutes |

---

## Installation Methods

### Option 1: Binary Installation (Recommended)

The standalone binary requires no Python installation and provides the fastest startup time.

#### Step 1: Install the Binary

```bash
# Clone the repository
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context

# Build and install (requires Python for build step only)
uv run python tools/build_mcp_server.py
./bin/install
```

Or download directly from releases:
```bash
# Download latest release (macOS ARM64)
curl -L -o uacs-mcp https://github.com/kylebrodeur/universal-agent-context/releases/latest/download/uacs-macos-arm64

# Make executable and move to system path
chmod +x uacs-mcp
sudo mv uacs-mcp /usr/local/bin/uacs-mcp
```

#### Step 2: Verify Installation

```bash
uacs-mcp --help
```

You should see:
```
usage: uacs-mcp [-h] [--transport {stdio,sse}] [--port PORT]

UACS MCP Server

options:
  -h, --help            show this help message and exit
  --transport {stdio,sse}
                        Transport mode
  --port PORT           Port for SSE server
```

#### Step 3: Configure Claude Desktop

1. Open Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add UACS to the `mcpServers` section:

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

**Note**: If you already have other MCP servers configured, add UACS as an additional entry:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "/path/to/existing-server"
    },
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"]
    }
  }
}
```

#### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop completely. The UACS MCP server will automatically start when Claude Desktop launches.

---

### Option 2: Docker Installation

Docker provides isolation and is ideal for team environments or when you want to avoid any local installations.

#### Step 1: Build or Pull the Docker Image

```bash
# Clone repository
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context

# Build locally
docker build -f Dockerfile -t uacs:latest .

# Or pull from registry (when available)
# docker pull ghcr.io/kylebrodeur/uacs:latest
```

#### Step 2: Start the Docker Container

```bash
# Quick start script
./bin/docker-quickstart

# Or manual start
docker run -d \
  --name uacs-mcp \
  -p 3000:3000 \
  -v ~/.state/uacs:/root/.state/uacs \
  uacs:latest --transport sse --port 3000
```

#### Step 3: Configure Claude Desktop for SSE

Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "uacs": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

#### Step 4: Verify Connection

```bash
# Check container is running
docker ps | grep uacs-mcp

# Check health endpoint
curl http://localhost:3000/health
# Should return: {"status":"ok"}
```

#### Step 5: Restart Claude Desktop

Close and reopen Claude Desktop. It will connect to the UACS server via HTTP SSE transport.

---

### Option 3: Python Package Installation

For developers who want to customize UACS or integrate it into existing Python workflows.

#### Step 1: Install UACS

```bash
# From source
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync  # Or: pip install -e .

# From PyPI (when available)
# pip install universal-agent-context
```

#### Step 2: Configure Claude Desktop

Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "uacs": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/universal-agent-context",
        "python",
        "-m",
        "uacs.mcp_server_entry",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

Replace `/path/to/universal-agent-context` with your actual clone path.

#### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop.

---

## Configuration

### Finding the Config File

The Claude Desktop configuration file location varies by platform:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

If the file doesn't exist, create it with this minimal structure:

```json
{
  "mcpServers": {}
}
```

### Complete Configuration Example

Here's a full configuration with multiple MCP servers and UACS:

```json
{
  "globalShortcut": "",
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/Documents"]
    },
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_DEBUG": "false",
        "UACS_STATE_DIR": "/Users/username/.state/uacs"
      }
    }
  },
  "preferences": {
    "quickEntryDictationShortcut": ""
  }
}
```

### Environment Variables

You can pass environment variables to customize UACS behavior:

| Variable | Description | Default |
|----------|-------------|---------|
| `UACS_DEBUG` | Enable debug logging | `false` |
| `UACS_STATE_DIR` | State directory location | `~/.state/uacs` |
| `UACS_TRANSPORT` | Override transport mode | `stdio` |
| `UACS_MAX_TOKENS` | Default max tokens for context | `4000` |

Example with environment variables:

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_DEBUG": "true",
        "UACS_STATE_DIR": "/custom/path/.state/uacs"
      }
    }
  }
}
```

---

## Testing the Integration

### Step 1: Verify Tools Are Loaded

After restarting Claude Desktop, start a new conversation and ask:

```
What MCP tools do you have available?
```

Claude should list UACS tools including:
- `skills_list` - List all available agent skills
- `marketplace_search` - Search skills marketplace
- `context_stats` - Get context statistics
- `unified_build_prompt` - Build complete agent prompt
- And 20+ more tools...

### Step 2: Test Basic Functionality

Try these example prompts in Claude:

#### List Available Skills
```
Use the skills_list tool to show me what skills are available.
```

#### Search the Marketplace
```
Search the skills marketplace for "testing" related skills.
```

#### Get Context Statistics
```
Show me the current context statistics using context_stats.
```

#### Test Skill Triggering
```
Use skills_test_trigger to see which skill would handle the query "review my code for security issues".
```

### Example Interaction

Here's a complete example of using UACS with Claude Desktop:

**You**: "Search the marketplace for Python testing tools"

**Claude**: Uses `marketplace_search` tool with query="python testing"

**Result**:
```json
{
  "results": [
    {
      "name": "pytest-skill",
      "description": "Comprehensive Python testing with pytest",
      "source": "github.com/anthropic/skills",
      "category": "testing"
    },
    {
      "name": "unittest-helper",
      "description": "Python unittest framework helper",
      "source": "agentskills.io",
      "category": "testing"
    }
  ],
  "total": 12,
  "query": "python testing"
}
```

---

## Available Tools Reference

UACS exposes 20+ MCP tools organized by category:

### Skills Management
- `skills_list` - List all available agent skills
- `skills_show` - Show detailed skill information
- `skills_test_trigger` - Test which skill matches a query
- `skills_validate` - Validate skills file format

### Context Management
- `context_stats` - Get context and token usage statistics
- `context_get_compressed` - Get compressed context within token budget
- `context_add_entry` - Add new context entry
- `context_compress` - Manually trigger compression
- `context_graph` - Get context relationship graph

### AGENTS.md Management
- `agents_md_load` - Load and parse AGENTS.md file
- `agents_md_to_prompt` - Convert AGENTS.md to system prompt

### Unified Context
- `unified_build_prompt` - Build complete agent prompt with all sources
- `unified_capabilities` - Get all unified capabilities
- `unified_token_stats` - Get token usage across all sources

### Marketplace Integration
- `marketplace_search` - Search skills marketplace
- `marketplace_install` - Install skill from marketplace
- `marketplace_list_installed` - List installed marketplace skills

### Project Validation
- `project_validate` - Validate AGENTS.md and skills configuration

---

## Troubleshooting

### Issue: UACS Tools Not Appearing

**Symptoms**: Claude Desktop doesn't show UACS tools or can't use them.

**Solutions**:

1. **Verify binary path**:
   ```bash
   which uacs-mcp
   # Should output: /usr/local/bin/uacs-mcp
   ```

2. **Test binary manually**:
   ```bash
   /usr/local/bin/uacs-mcp --help
   ```
   If this fails, reinstall the binary.

3. **Check config file syntax**:
   ```bash
   # Validate JSON syntax
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
   ```

4. **Completely restart Claude Desktop**:
   - Quit Claude Desktop (Cmd+Q on macOS)
   - Wait 5 seconds
   - Reopen Claude Desktop

5. **Check Claude Desktop logs** (macOS):
   ```bash
   # View recent logs
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### Issue: Connection Errors (Docker)

**Symptoms**: "Failed to connect to MCP server" when using Docker setup.

**Solutions**:

1. **Verify container is running**:
   ```bash
   docker ps | grep uacs-mcp
   ```

2. **Check port is accessible**:
   ```bash
   curl http://localhost:3000/health
   ```

3. **Review container logs**:
   ```bash
   docker logs uacs-mcp
   ```

4. **Restart container**:
   ```bash
   docker restart uacs-mcp
   ```

### Issue: Permission Denied

**Symptoms**: "Permission denied" when executing binary.

**Solutions**:

1. **Make binary executable**:
   ```bash
   sudo chmod +x /usr/local/bin/uacs-mcp
   ```

2. **Remove quarantine (macOS)**:
   ```bash
   sudo xattr -d com.apple.quarantine /usr/local/bin/uacs-mcp
   ```

### Issue: Tools Timing Out

**Symptoms**: Tool calls hang or timeout.

**Solutions**:

1. **Enable debug mode**:
   ```json
   {
     "mcpServers": {
       "uacs": {
         "command": "/usr/local/bin/uacs-mcp",
         "args": ["--transport", "stdio"],
         "env": {
           "UACS_DEBUG": "true"
         }
       }
     }
   }
   ```

2. **Check system resources**:
   ```bash
   # Monitor CPU/memory usage
   top -pid $(pgrep -f uacs-mcp)
   ```

3. **Reduce context size**:
   ```json
   {
     "env": {
       "UACS_MAX_TOKENS": "2000"
     }
   }
   ```

### Issue: Skill Not Found

**Symptoms**: "Skill 'xyz' not found" error.

**Solutions**:

1. **Initialize UACS in project**:
   ```bash
   cd /path/to/your/project
   uv run uacs context init
   ```

2. **Verify skills directory exists**:
   ```bash
   ls -la .state/context/
   ```

3. **Check skill file format**:
   ```bash
   uv run uacs skills validate
   ```

---

## Debug Mode

Enable verbose logging to diagnose issues:

### For Binary

Update Claude Desktop config:

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_DEBUG": "true",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### For Docker

```bash
# Run with debug logging
docker run -d \
  --name uacs-mcp \
  -p 3000:3000 \
  -e UACS_DEBUG=true \
  uacs:latest --transport sse --port 3000

# View logs
docker logs -f uacs-mcp
```

### Viewing Logs

**macOS**:
```bash
# Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp*.log

# System logs
log stream --predicate 'eventMessage contains "uacs"'
```

**Linux**:
```bash
# User logs
journalctl --user -u claude-desktop -f
```

---

## Performance Notes

### Startup Time
- **Binary**: ~100ms (fastest)
- **Docker**: ~500ms (includes container networking)
- **Python Package**: ~300ms (depends on environment)

### Memory Usage
- **Idle**: ~50MB
- **Active (typical)**: ~150MB
- **Active (heavy context)**: ~300MB

### Token Processing
- **Context compression**: 10,000 tokens/second
- **Marketplace search**: <100ms typical
- **Skill validation**: <50ms per skill

---

## Advanced Usage

### Custom State Directory

Store UACS state in a project-specific location:

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_STATE_DIR": "/Users/username/myproject/.uacs"
      }
    }
  }
}
```

### Team Shared Context

Use Docker with volume mounts to share context across team members:

```bash
# Start with shared volume
docker run -d \
  --name uacs-mcp \
  -p 3000:3000 \
  -v /shared/team/uacs:/root/.state/uacs \
  uacs:latest --transport sse --port 3000
```

### Multiple UACS Instances

Run different UACS instances for different projects:

```json
{
  "mcpServers": {
    "uacs-project-a": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_STATE_DIR": "/path/to/project-a/.uacs"
      }
    },
    "uacs-project-b": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_STATE_DIR": "/path/to/project-b/.uacs"
      }
    }
  }
}
```

---

## Getting Help

### Documentation
- [Main README](../../README.md)
- [MCP Server Binary Guide](../MCP_SERVER_BINARY.md)
- [MCP Server Docker Guide](../MCP_SERVER_DOCKER.md)
- [Library Guide](../LIBRARY_GUIDE.md)

### Support Channels
- **GitHub Issues**: [Report bugs or request features](https://github.com/kylebrodeur/universal-agent-context/issues)
- **Discussions**: [Ask questions](https://github.com/kylebrodeur/universal-agent-context/discussions)
- **Documentation**: [Full docs](https://github.com/kylebrodeur/universal-agent-context/tree/main/docs)

### Common Questions

**Q: Can I use UACS with other MCP clients?**  
A: Yes! UACS implements the standard MCP protocol and works with any MCP-compatible client (Claude Desktop, Cursor, Windsurf, etc.).

**Q: Does UACS require internet access?**  
A: No, UACS runs locally. Internet is only needed for marketplace features (optional).

**Q: Can I customize which tools are exposed?**  
A: Not yet, but this feature is planned. Track [issue #XX](https://github.com/kylebrodeur/universal-agent-context/issues).

**Q: How do I update UACS?**  
A: Reinstall using your chosen method (binary/Docker/Python). Your state directory is preserved.

---

## What's Next?

Now that you have UACS integrated with Claude Desktop, explore:

1. **[Skills Marketplace](../MARKETPLACE.md)** - Discover and install pre-built skills
2. **[Context Management](../CONTEXT.md)** - Learn about advanced context features
3. **[AGENTS.md](../../docs/ADAPTERS.md)** - Multi-agent coordination
4. **[Library Guide](../LIBRARY_GUIDE.md)** - Use UACS in Python code

---

**Integration Status**: ✅ Full Support  
**Last Updated**: 2026-01-06  
**Tested With**: Claude Desktop v0.7.2+ on macOS, Windows, Linux
