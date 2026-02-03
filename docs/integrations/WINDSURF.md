# UACS Integration with Windsurf

**Universal Agent Context System (UACS)** integrates with Windsurf as an MCP (Model Context Protocol) server, bringing intelligent context management, package management, and multi-format translation to the Windsurf AI-powered IDE.

## Quick Start

| Method | Best For | Setup Time |
|--------|----------|------------|
| **Binary** (Recommended) | Fast, standalone execution | 2 minutes |
| **Python Package** | Development, customization | 5 minutes |
| **Docker** | Server deployments, teams | 3 minutes |

---

## Why UACS + Windsurf?

Windsurf's Cascade AI is powerful, but UACS takes it further:

✅ **Extended Memory**: Persistent context across sessions  
✅ **Skills Library**: Pre-built capabilities for common dev tasks  
✅ **Token Efficiency**: Up to 70% reduction in context tokens  
✅ **Package Management**: Community-driven skills and tools  
✅ **Format Translation**: Bridge between .windsurfrules, AGENTS.md, and more  

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

Or download directly:
```bash
# macOS ARM64
curl -L -o uacs-mcp https://github.com/kylebrodeur/universal-agent-context/releases/latest/download/uacs-macos-arm64

# Make executable and install
chmod +x uacs-mcp
sudo mv uacs-mcp /usr/local/bin/uacs-mcp
```

Verify:
```bash
uacs-mcp --help
```

#### Step 2: Configure Windsurf

1. Open Windsurf Settings:
   - **macOS**: Windsurf → Settings (⌘ + ,)
   - **Windows**: File → Preferences → Settings
   - **Linux**: File → Preferences → Settings

2. Navigate to **Cascade** → **MCP Servers** or edit config directly:
   - **macOS**: `~/Library/Application Support/Windsurf/mcp_config.json`
   - **Windows**: `%APPDATA%\Windsurf\mcp_config.json`
   - **Linux**: `~/.config/Windsurf/mcp_config.json`

3. Add UACS configuration:

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "enabled": true
    }
  }
}
```

#### Step 3: Restart Windsurf

Completely close and reopen Windsurf. UACS will automatically start with Cascade.

---

### Option 2: Python Package Installation

For developers working with UACS source or customizations.

#### Step 1: Install UACS

```bash
# From source
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync  # Or: pip install -e .

# From PyPI (when available)
# pip install universal-agent-context
```

#### Step 2: Configure Windsurf

Edit Windsurf's MCP config:

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
      ],
      "enabled": true
    }
  }
}
```

Replace `/path/to/universal-agent-context` with your actual installation path.

#### Step 3: Restart Windsurf

---

### Option 3: Docker Installation

Ideal for team environments or isolated deployments.

#### Step 1: Start UACS Container

```bash
# Build image
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
docker build -f Dockerfile -t uacs:latest .

# Run container
docker run -d \
  --name uacs-mcp \
  -p 3000:3000 \
  -v ~/.state/uacs:/root/.state/uacs \
  uacs:latest --transport sse --port 3000
```

Verify:
```bash
curl http://localhost:3000/health
# Expected: {"status":"ok"}
```

#### Step 2: Configure Windsurf

Edit MCP config for SSE transport:

```json
{
  "mcpServers": {
    "uacs": {
      "url": "http://localhost:3000/sse",
      "enabled": true
    }
  }
}
```

#### Step 3: Restart Windsurf

---

## Configuration

### Config File Location

Windsurf's MCP configuration is stored at:

- **macOS**: `~/Library/Application Support/Windsurf/mcp_config.json`
- **Windows**: `%APPDATA%\Windsurf\mcp_config.json`
- **Linux**: `~/.config/Windsurf/mcp_config.json`

Create the file if it doesn't exist:

```json
{
  "mcpServers": {}
}
```

### Complete Configuration Example

Multi-server setup with UACS:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
      "enabled": true
    },
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "enabled": true,
      "env": {
        "UACS_DEBUG": "false",
        "UACS_STATE_DIR": "/home/user/.state/uacs",
        "UACS_MAX_TOKENS": "4000"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "enabled": true
    }
  }
}
```

### Environment Variables

Customize UACS behavior:

| Variable | Description | Default |
|----------|-------------|---------|
| `UACS_DEBUG` | Enable verbose logging | `false` |
| `UACS_STATE_DIR` | State/cache directory | `~/.state/uacs` |
| `UACS_MAX_TOKENS` | Max tokens for context | `4000` |
| `UACS_TRANSPORT` | Transport protocol override | `stdio` |

---

## Testing the Integration

### Step 1: Verify UACS is Loaded

Open Cascade chat in Windsurf and ask:

```
What MCP tools are available from UACS?
```

Expected response should include tools like:
- `skills_list`
- `packages_search`
- `context_stats`
- `unified_build_prompt`
- Plus 20+ additional tools

### Step 2: Test Core Features

#### List Agent Skills
```
Use the skills_list tool to show available agent skills.
```

#### Search Packages
```
Search the package registry for "debugging" related capabilities.
```

#### Context Statistics
```
Show me context statistics using the context_stats tool.
```

### Step 3: Real-World Workflow Test

**Scenario**: Finding and using a code review skill in Windsurf

1. Open a Python file in Windsurf
2. Open Cascade (F1 or ⌘ + ⇧ + P → "Cascade Chat")
3. Prompt: "Search packages for code review skills, install the best one, and review my current file"
4. UACS will:
   - Search the package registry
   - Present options
   - Install selected skill
   - Apply it to your code
   - Return detailed review

---

## Available Tools

UACS exposes 20+ MCP tools via Windsurf Cascade:

### Skills Management
- `skills_list` - List all available agent skills
- `skills_show` - Display detailed skill information
- `skills_test_trigger` - Test skill matching for queries
- `skills_validate` - Validate skill file formats

### Context Management
- `context_stats` - Token and context usage statistics
- `context_get_compressed` - Compressed context within budget
- `context_add_entry` - Add new context entries
- `context_compress` - Manual compression trigger
- `context_graph` - Visualize context relationships

### Unified Context
- `unified_build_prompt` - Build complete agent prompts
- `unified_capabilities` - List all capabilities
- `unified_token_stats` - Cross-source token statistics

### Package Management
- `packages_search` - Search for skills and tools
- `packages_install` - Install packages
- `packages_list_installed` - List installed items

### Project Management
- `project_validate` - Validate AGENTS.md and skills
- `agents_md_load` - Load and parse AGENTS.md
- `agents_md_to_prompt` - Convert AGENTS.md to prompts

---

## Windsurf-Specific Features

### Cascade Integration

UACS tools are automatically available in Windsurf's Cascade AI:

**Agent Flow Commands**:
```
@cascade search packages for testing tools
@cascade use context compression on this project
@cascade validate my agent skills configuration
```

### Rules File Translation

Convert between Windsurf rules and other formats:

```bash
# CLI
uacs translate .windsurfrules AGENTS.md

# In Cascade
"Translate my .windsurfrules to AGENTS.md format"
```

### Workspace Context

UACS enhances Windsurf's workspace understanding:

```
"Use unified_build_prompt to create a complete context summary 
for this workspace, including all skills and project structure."
```

### Multi-Agent Coordination

When using multiple Cascade agents:

```
"Use unified_capabilities to show which skills each agent has access to."
```

---

## Use Cases

### 1. Intelligent Code Review

```typescript
// Windsurf Cascade
"Search packages for security-focused code review skills, 
install one, and thoroughly review this module for vulnerabilities."
```

UACS will:
- Find relevant skills
- Install automatically
- Apply to your code
- Provide actionable feedback

### 2. Automated Test Generation

```python
# In any Python file
"Find a pytest skill and generate comprehensive tests 
with edge cases for all functions in this file."
```

### 3. Documentation Generation

```javascript
"Use package documentation skills to generate 
API docs for this entire project."
```

### 4. Context-Aware Debugging

```
"Use context_graph to show the relationship between 
recent changes and this bug."
```

This helps trace issues through context history.

### 5. Token Optimization

```
"Compress the context for the last 10 commits to save tokens."
```

Reduces API costs while maintaining key information.

---

## Performance Notes

### Startup Times
- **Binary**: ~100ms (fastest)
- **Python Package**: ~300ms
- **Docker**: ~500ms (includes networking)

### Windsurf Impact
- **Initial Load**: +150ms to Cascade startup
- **Tool Calls**: 10-150ms per invocation
- **Memory**: ~150MB additional RAM (typical usage)
- **CPU**: <5% during active operations

### Token Savings

UACS context compression provides significant savings:

| Context Type | Without UACS | With UACS | Savings |
|--------------|--------------|-----------|---------|
| Single file | 3,000 tokens | 1,000 tokens | 67% |
| Project summary | 15,000 tokens | 4,500 tokens | 70% |
| Full history | 50,000 tokens | 12,000 tokens | 76% |

**Real-world impact**: Lower API costs, faster responses, more context fits in Cascade's window.

---

## Troubleshooting

### Issue: MCP Server Not Loading

**Symptoms**: UACS tools don't appear in Cascade

**Solutions**:

1. **Verify binary installation**:
   ```bash
   which uacs-mcp
   # Expected: /usr/local/bin/uacs-mcp
   ```

2. **Test binary manually**:
   ```bash
   /usr/local/bin/uacs-mcp --help
   ```

3. **Check config syntax**:
   ```bash
   cat ~/Library/Application\ Support/Windsurf/mcp_config.json | python -m json.tool
   ```

4. **Enable MCP in Windsurf**:
   - Settings → Cascade → Enable MCP Servers

5. **Restart Windsurf completely**:
   - Quit Windsurf (not just close window)
   - Wait 5 seconds
   - Reopen

6. **Check Windsurf logs**:
   - **macOS**: `~/Library/Logs/Windsurf/`
   - **Linux**: `~/.config/Windsurf/logs/`
   - **Windows**: `%APPDATA%\Windsurf\logs\`

### Issue: Permission Errors

**Symptoms**: "Permission denied" when starting UACS

**Solutions**:

1. **Make binary executable**:
   ```bash
   sudo chmod +x /usr/local/bin/uacs-mcp
   ```

2. **Remove macOS quarantine**:
   ```bash
   sudo xattr -d com.apple.quarantine /usr/local/bin/uacs-mcp
   ```

3. **Verify ownership**:
   ```bash
   ls -l /usr/local/bin/uacs-mcp
   # Should show: -rwxr-xr-x
   ```

### Issue: Tools Timeout

**Symptoms**: Tool calls hang or take too long

**Solutions**:

1. **Enable debug mode**:
   ```json
   {
     "mcpServers": {
       "uacs": {
         "command": "/usr/local/bin/uacs-mcp",
         "args": ["--transport", "stdio"],
         "enabled": true,
         "env": {
           "UACS_DEBUG": "true"
         }
       }
     }
   }
   ```

2. **Reduce token budget**:
   ```json
   {
     "env": {
       "UACS_MAX_TOKENS": "2000"
     }
   }
   ```

3. **Check system resources**:
   ```bash
   top -pid $(pgrep -f uacs-mcp)
   ```

### Issue: Docker Connection Failed

**Symptoms**: Cannot connect to Docker-based UACS

**Solutions**:

1. **Verify container**:
   ```bash
   docker ps | grep uacs-mcp
   ```

2. **Test endpoint**:
   ```bash
   curl http://localhost:3000/health
   ```

3. **Check logs**:
   ```bash
   docker logs -f uacs-mcp
   ```

4. **Restart**:
   ```bash
   docker restart uacs-mcp
   ```

### Issue: Skills Not Found

**Symptoms**: "Skill not found" errors

**Solutions**:

1. **Initialize project**:
   ```bash
   cd /path/to/project
   uacs context init
   uacs memory init
   ```

2. **Verify state directory**:
   ```bash
   ls -la ~/.state/uacs/
   ```

3. **Validate skills**:
   ```bash
   uacs skills validate
   ```

---

## Debug Mode

Enable detailed logging for troubleshooting:

### Binary Configuration

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "enabled": true,
      "env": {
        "UACS_DEBUG": "true",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Docker Configuration

```bash
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
tail -f ~/Library/Logs/Windsurf/main.log
```

**Linux**:
```bash
tail -f ~/.config/Windsurf/logs/main.log
```

**Windows**:
```powershell
Get-Content "$env:APPDATA\Windsurf\logs\main.log" -Wait
```

---

## Advanced Usage

### Project-Specific Context

Different UACS state per project:

```json
{
  "mcpServers": {
    "uacs-frontend": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "enabled": true,
      "env": {
        "UACS_STATE_DIR": "/projects/frontend/.uacs"
      }
    },
    "uacs-backend": {
      "command": "/usr/local/bin/uacs-mcp",
      "args": ["--transport", "stdio"],
      "enabled": true,
      "env": {
        "UACS_STATE_DIR": "/projects/backend/.uacs"
      }
    }
  }
}
```

### Team Shared Server

Central UACS server for team collaboration:

```bash
# Server setup
docker run -d \
  --name uacs-team \
  -p 3000:3000 \
  -v /team/shared/uacs:/root/.state/uacs \
  uacs:latest --transport sse --port 3000
```

Team members configure Windsurf:
```json
{
  "mcpServers": {
    "uacs": {
      "url": "http://team-server.local:3000/sse",
      "enabled": true
    }
  }
}
```

### Custom Skills Repository

Point UACS to your organization's private skills:

```json
{
  "env": {
    "UACS_SKILLS_REPO": "https://github.com/yourorg/private-skills.git"
  }
}
```

---

## Feature Compatibility Matrix

| Feature | Support Level | Notes |
|---------|---------------|-------|
| Skills Management | ✅ Full | All 20+ tools work |
| Context Compression | ✅ Full | 70% token savings |
| Package Search | ✅ Full | Real-time search |
| Package Install | ✅ Full | Automatic installation |
| AGENTS.md | ✅ Full | Load and convert |
| .windsurfrules | ⚠️ Partial | Translation supported |
| Multi-Agent | ✅ Full | Cascade multi-agent flows |
| Persistent Memory | ✅ Full | Cross-session context |
| Team Sharing | ✅ Full | Via Docker/SSE |
| Offline Mode | ✅ Full | Except packages |

**Legend**:
- ✅ Full: Complete support, tested
- ⚠️ Partial: Works with limitations
- ❌ None: Not yet supported

---

## Best Practices

### 1. Initialize Per Workspace

Always initialize UACS when opening a new workspace:

```bash
cd /path/to/workspace
uacs context init
uacs memory init
```

### 2. Use Skills for Repetitive Tasks

Instead of re-prompting:

```
# Inefficient
"Check this code for security issues, SQL injection, XSS, CSRF..."

# Efficient
"Use the security-review skill"
```

### 3. Leverage Context Compression

For large projects:

```
"Compress context for the last sprint's changes"
```

### 4. Search Before Creating

Check packages before writing custom skills:

```
"Search packages for [task description]"
```

### 5. Monitor Token Usage

Regularly check stats:

```
"Show unified_token_stats"
```

---

## Comparison with Alternatives

| Capability | UACS + Windsurf | Windsurf Alone |
|------------|-----------------|----------------|
| Context Management | ✅ Advanced | Basic |
| Persistent Memory | ✅ Yes | Limited |
| Skills Library | ✅ 100+ skills | None |
| Token Optimization | ✅ 70% savings | Minimal |
| Package Management | ✅ Yes | No |
| Multi-Format | ✅ 5+ formats | 1 format |
| Team Sharing | ✅ Full | Limited |
| Offline Work | ✅ Most features | All features |

---

## Getting Help

### Documentation
- [Main README](../../README.md)
- [MCP Server Binary](../MCP_SERVER_BINARY.md)
- [Skills Guide](../ADAPTERS.md)
- [Library API](../LIBRARY_GUIDE.md)

### Support
- **Issues**: [GitHub Issues](https://github.com/kylebrodeur/universal-agent-context/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kylebrodeur/universal-agent-context/discussions)
- **Docs**: [Full Documentation](https://github.com/kylebrodeur/universal-agent-context/tree/main/docs)

### FAQ

**Q: Does UACS work with Windsurf Flows?**  
A: Yes! UACS tools integrate seamlessly with Windsurf's Flow feature.

**Q: Can I use UACS offline in Windsurf?**  
A: Yes, all core features work offline. Only packages require internet.

**Q: Does UACS slow down Cascade?**  
A: Minimal impact: ~150ms startup, <5% CPU during use.

**Q: Can I customize which tools appear in Cascade?**  
A: Not yet, but planned. Track the GitHub issue for updates.

**Q: Is UACS compatible with Windsurf's remote development?**  
A: Yes! Install UACS on the remote server and configure normally.

---

## Known Limitations

1. **Rules Translation**: .windsurfrules → AGENTS.md is experimental
2. **Real-time Sync**: Team context syncs on tool use, not live
3. **Tool Filtering**: Can't disable individual tools yet
4. **Cascade UI**: MCP tools appear as text, no custom UI yet

These are actively being addressed. See [roadmap](../IMPLEMENTATION_ROADMAP.md).

---

## What's Next?

With UACS integrated into Windsurf, explore:

1. **[Package Management](../features/PACKAGES.md)** - Browse 100+ pre-built skills
2. **[Context Optimization](../CONTEXT.md)** - Advanced compression techniques
3. **[AGENTS.md Format](../ADAPTERS.md)** - Multi-agent coordination
4. **[Python Library](../LIBRARY_GUIDE.md)** - Build custom integrations

---

**Integration Status**: ✅ Full Support  
**Last Updated**: 2026-01-06  
**Tested With**: Windsurf v1.0+ on macOS, Windows, Linux  
**MCP Protocol**: v1.0 compliant
