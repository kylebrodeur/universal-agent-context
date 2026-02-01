# UACS Integration with Cursor

**Universal Agent Context System (UACS)** integrates with Cursor as an MCP (Model Context Protocol) server, bringing intelligent context management, skills marketplace, and format translation capabilities to your AI-powered code editor.

## Quick Start

| Method | Best For | Setup Time |
|--------|----------|------------|
| **Binary** (Recommended) | Fastest startup, zero dependencies | 2 minutes |
| **Python Package** | Development, customization | 5 minutes |
| **Docker** | Isolated environment, server deployment | 3 minutes |

---

## Why UACS + Cursor?

Cursor is already powerful, but UACS makes it even better:

✅ **Persistent Context**: Keep project knowledge across sessions  
✅ **Skills Library**: Access pre-built agent skills for common tasks  
✅ **Token Optimization**: 70% reduction in context tokens  
✅ **Marketplace**: Discover and install community skills  
✅ **Multi-Format Support**: Translate between .cursorrules, AGENTS.md, and more  

---

## Installation

### Option 1: Binary Installation (Recommended)

#### Step 1: Install UACS Binary

```bash
# Clone repository
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context

# Build and install
uv run python tools/build_mcp_server.py
./bin/install
```

Or download from releases:
```bash
curl -L -o uacs-mcp https://github.com/kylebrodeur/universal-agent-context/releases/latest/download/uacs-macos-arm64
chmod +x uacs-mcp
sudo mv uacs-mcp /usr/local/bin/uacs-mcp
```

Verify installation:
```bash
uacs-mcp --help
```

#### Step 2: Configure Cursor

1. Open Cursor Settings (⌘ + , on macOS)
2. Navigate to **Features** → **Beta** → **Model Context Protocol**
3. Enable MCP support
4. Click **Edit Config** or manually edit the config file:
   - **macOS/Linux**: `~/.cursor/mcp.json`
   - **Windows**: `%APPDATA%\Cursor\mcp.json`

5. Add UACS configuration:

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

#### Step 3: Restart Cursor

Close and reopen Cursor completely. UACS will start automatically when Cursor launches.

---

### Option 2: Python Package Installation

For developers who want to customize UACS or use development versions.

#### Step 1: Install UACS

```bash
# From source
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync  # Or: pip install -e .

# From PyPI (when available)
# pip install universal-agent-context
```

#### Step 2: Configure Cursor

Edit Cursor's MCP config (`~/.cursor/mcp.json`):

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

Replace `/path/to/universal-agent-context` with your actual path.

#### Step 3: Restart Cursor

---

### Option 3: Docker Installation

Use Docker for isolated environments or team deployments.

#### Step 1: Start UACS Container

```bash
# Clone repository
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context

# Build and run
docker build -f Dockerfile.mcp-server -t uacs:latest .
docker run -d \
  --name uacs-mcp \
  -p 3000:3000 \
  -v ~/.state/uacs:/root/.state/uacs \
  uacs:latest --transport sse --port 3000
```

Verify it's running:
```bash
curl http://localhost:3000/health
# Should return: {"status":"ok"}
```

#### Step 2: Configure Cursor

Edit Cursor's MCP config (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "uacs": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

#### Step 3: Restart Cursor

---

## Configuration

### MCP Config File Location

Cursor's MCP configuration file is located at:

- **macOS**: `~/.cursor/mcp.json`
- **Linux**: `~/.cursor/mcp.json`
- **Windows**: `%APPDATA%\Cursor\mcp.json`

If the file doesn't exist, create it:

```json
{
  "mcpServers": {}
}
```

### Complete Configuration Example

Here's a full configuration with multiple MCP servers:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/projects"]
    },
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_DEBUG": "false",
        "UACS_STATE_DIR": "/Users/username/.state/uacs",
        "UACS_MAX_TOKENS": "4000"
      }
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    }
  }
}
```

### Environment Variables

Customize UACS behavior with environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `UACS_DEBUG` | Enable debug logging | `false` |
| `UACS_STATE_DIR` | State directory location | `~/.state/uacs` |
| `UACS_MAX_TOKENS` | Default max tokens for context | `4000` |
| `UACS_TRANSPORT` | Override transport mode | `stdio` |

---

## Testing the Integration

### Step 1: Verify UACS Is Loaded

Open Cursor and start a new chat. Ask the AI:

```
What MCP tools are available?
```

You should see UACS tools listed, including:
- `skills_list`
- `marketplace_search`
- `context_stats`
- `unified_build_prompt`
- And 20+ more...

### Step 2: Test Basic Features

#### List Available Skills
In Cursor's chat:
```
List all available agent skills using the skills_list tool.
```

#### Search for Skills
```
Search the marketplace for "code review" skills.
```

#### Get Context Statistics
```
Show me the current context statistics.
```

### Step 3: Test in Real Workflow

Here's a practical example using UACS in Cursor:

**Scenario**: You're working on a Python project and want to find testing skills.

1. Open Cursor chat (⌘ + L)
2. Ask: "Search the skills marketplace for Python testing tools"
3. Cursor uses `marketplace_search` to find relevant skills
4. Install a skill: "Install the pytest-skill from the marketplace"
5. Use it: "Use the pytest skill to generate tests for my current file"

---

## Available Tools

UACS provides 20+ MCP tools organized by category:

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

### Unified Context
- `unified_build_prompt` - Build complete agent prompt
- `unified_capabilities` - Get all unified capabilities
- `unified_token_stats` - Get token usage across all sources

### Marketplace
- `marketplace_search` - Search skills marketplace
- `marketplace_install` - Install skill from marketplace
- `marketplace_list_installed` - List installed skills

### Project Management
- `project_validate` - Validate AGENTS.md and skills configuration
- `agents_md_load` - Load and parse AGENTS.md file
- `agents_md_to_prompt` - Convert AGENTS.md to system prompt

---

## Use Cases

### 1. Code Review Assistant

```typescript
// Cursor chat
"Use the marketplace to find code review skills, then review this file for security issues."
```

UACS will:
1. Search marketplace for "code review" skills
2. Install the best match
3. Apply the skill to your current file
4. Provide detailed feedback

### 2. Test Generation

```typescript
// In any project file
"Find a testing skill and generate comprehensive tests for this module."
```

### 3. Documentation

```typescript
"Search for documentation skills and generate API docs for this codebase."
```

### 4. Context Compression

```typescript
// When working with large codebases
"Use context compression to summarize the entire project structure."
```

This reduces token usage by ~70% while preserving essential information.

---

## Performance Notes

### Startup Time
- **Binary**: ~100ms
- **Python Package**: ~300ms
- **Docker**: ~500ms

### Impact on Cursor
- **Initial Load**: Adds ~200ms to Cursor startup
- **Tool Invocation**: 10-100ms per call (varies by tool)
- **Memory**: ~150MB additional RAM usage (typical)
- **CPU**: Minimal (<5% during active use)

### Token Savings
UACS context compression can reduce token usage by up to 70%:

**Without UACS**:
- Full file content: 5,000 tokens
- Multiple files: 20,000+ tokens

**With UACS**:
- Compressed context: 1,500 tokens
- Multi-file summary: 6,000 tokens

This means faster responses and lower API costs.

---

## Troubleshooting

### Issue: MCP Tools Not Appearing

**Symptoms**: Cursor doesn't show UACS tools or reports "MCP server failed to start"

**Solutions**:

1. **Verify binary exists**:
   ```bash
   ls -l /usr/local/bin/uacs-mcp
   ```

2. **Test binary manually**:
   ```bash
   /usr/local/bin/uacs-mcp --help
   ```

3. **Check config syntax**:
   ```bash
   cat ~/.cursor/mcp.json | python -m json.tool
   ```

4. **Enable MCP in Cursor settings**:
   - Settings → Features → Beta → Model Context Protocol (enable)

5. **Completely restart Cursor**:
   - Quit Cursor (⌘ + Q)
   - Kill any background processes: `pkill -f cursor`
   - Reopen Cursor

6. **Check Cursor logs**:
   - **macOS**: `~/Library/Logs/Cursor/`
   - **Linux**: `~/.cursor/logs/`
   - Look for MCP-related errors

### Issue: Permission Denied

**Symptoms**: "Permission denied" error when starting UACS

**Solutions**:

1. **Make binary executable**:
   ```bash
   sudo chmod +x /usr/local/bin/uacs-mcp
   ```

2. **Remove macOS quarantine**:
   ```bash
   sudo xattr -d com.apple.quarantine /usr/local/bin/uacs-mcp
   ```

3. **Check file ownership**:
   ```bash
   ls -l /usr/local/bin/uacs-mcp
   # Should show: -rwxr-xr-x
   ```

### Issue: Tools Timing Out

**Symptoms**: Tool calls hang or take too long

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

2. **Reduce context size**:
   ```json
   {
     "env": {
       "UACS_MAX_TOKENS": "2000"
     }
   }
   ```

3. **Monitor resources**:
   ```bash
   top -pid $(pgrep -f uacs-mcp)
   ```

### Issue: Docker Connection Failed

**Symptoms**: "Failed to connect" when using Docker setup

**Solutions**:

1. **Verify container is running**:
   ```bash
   docker ps | grep uacs-mcp
   ```

2. **Check health endpoint**:
   ```bash
   curl http://localhost:3000/health
   ```

3. **View container logs**:
   ```bash
   docker logs -f uacs-mcp
   ```

4. **Restart container**:
   ```bash
   docker restart uacs-mcp
   ```

### Issue: Skills Not Found

**Symptoms**: "Skill 'xyz' not found" error

**Solutions**:

1. **Initialize UACS in project**:
   ```bash
   cd /path/to/your/project
   uacs context init
   ```

2. **Check state directory**:
   ```bash
   ls -la ~/.state/uacs/
   ```

3. **Validate skills**:
   ```bash
   uacs skills validate
   ```

---

## Debug Mode

Enable verbose logging to diagnose issues:

### For Binary

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

### View Logs

**macOS**:
```bash
# Cursor logs
tail -f ~/Library/Logs/Cursor/main.log

# UACS output (if redirected)
tail -f ~/.cursor/uacs.log
```

**Linux**:
```bash
tail -f ~/.cursor/logs/main.log
```

---

## Advanced Usage

### Project-Specific Configuration

Use different UACS configurations for different projects:

**Project A** (`.cursor/mcp.json` in project root):
```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_STATE_DIR": "/path/to/project-a/.uacs"
      }
    }
  }
}
```

**Project B**:
```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "UACS_STATE_DIR": "/path/to/project-b/.uacs"
      }
    }
  }
}
```

### Team Shared Context

Use Docker with shared volumes for team collaboration:

```bash
# Team server
docker run -d \
  --name uacs-team \
  -p 3000:3000 \
  -v /shared/network/uacs:/root/.state/uacs \
  uacs:latest --transport sse --port 3000
```

Team members configure Cursor to use the shared server:
```json
{
  "mcpServers": {
    "uacs": {
      "url": "http://team-server:3000/sse"
    }
  }
}
```

### Integration with .cursorrules

UACS can translate between formats:

```bash
# Convert .cursorrules to AGENTS.md
uacs translate .cursorrules AGENTS.md

# Or use within Cursor
"Translate my .cursorrules file to AGENTS.md format"
```

---

## Cursor-Specific Features

### Inline Context

UACS integrates with Cursor's inline chat (⌘ + K):

1. Select code
2. Open inline chat (⌘ + K)
3. Ask: "Use context_stats to check token usage for this selection"

### Composer Mode

In Cursor's Composer (⌘ + I), UACS tools are automatically available:

```
"Search marketplace for refactoring skills, install the best one, 
and refactor this entire file for better performance."
```

### Multi-File Context

When working across multiple files, UACS optimizes context:

```
"Use context compression to summarize all modified files 
in the current git diff."
```

---

## Best Practices

### 1. Initialize Per Project

Always initialize UACS in your project root:

```bash
cd /path/to/project
uacs context init
uacs memory init
```

This creates project-specific state in `.state/`.

### 2. Use Skills for Repetitive Tasks

Instead of re-explaining tasks:

```
# Bad: Explaining each time
"Review this code for security issues, check for SQL injection, 
XSS, buffer overflows..."

# Good: Use a skill
"Use the security-review skill on this file"
```

### 3. Leverage Marketplace

Before writing custom prompts, check the marketplace:

```
"Search marketplace for [your task]"
```

Chances are someone already built it.

### 4. Monitor Token Usage

Regularly check context stats:

```
"Show context_stats"
```

This helps optimize your workflow and reduce costs.

---

## Comparison with Other Tools

| Feature | UACS + Cursor | Cursor Alone |
|---------|---------------|--------------|
| Context Management | ✅ Advanced | Basic |
| Skills Library | ✅ 100+ skills | None |
| Token Compression | ✅ 70% savings | None |
| Marketplace | ✅ Yes | None |
| Multi-Format | ✅ 5+ formats | 1 format |
| Persistent Memory | ✅ Yes | No |
| Team Sharing | ✅ Yes | Limited |

---

## Getting Help

### Documentation
- [Main README](../../README.md)
- [MCP Server Binary Guide](../MCP_SERVER_BINARY.md)
- [Skills Documentation](../ADAPTERS.md)
- [Library Guide](../LIBRARY_GUIDE.md)

### Support Channels
- **GitHub Issues**: [Report bugs](https://github.com/kylebrodeur/universal-agent-context/issues)
- **Discussions**: [Ask questions](https://github.com/kylebrodeur/universal-agent-context/discussions)

### Common Questions

**Q: Does UACS work with Cursor's remote SSH mode?**  
A: Yes! Install UACS on the remote server and configure as normal.

**Q: Can I use UACS offline?**  
A: Yes, all core features work offline. Only marketplace features require internet.

**Q: Does UACS slow down Cursor?**  
A: Minimal impact (~100-200ms startup, <5% CPU during use).

**Q: Can I disable specific UACS tools?**  
A: Not yet, but this feature is planned. Track [issue #XX](https://github.com/kylebrodeur/universal-agent-context/issues).

---

## What's Next?

Now that UACS is integrated with Cursor, explore:

1. **[Skills Marketplace](../MARKETPLACE.md)** - Browse 100+ pre-built skills
2. **[Context Management](../CONTEXT.md)** - Advanced context optimization
3. **[AGENTS.md Format](../ADAPTERS.md)** - Multi-agent coordination
4. **[Library Guide](../LIBRARY_GUIDE.md)** - Python API

---

**Integration Status**: ✅ Full Support  
**Last Updated**: 2026-01-06  
**Tested With**: Cursor v0.42+ on macOS, Windows, Linux
