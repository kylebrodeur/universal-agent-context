# Phase 5: MCP Server Integration Testing - Agent Task

## Context

UACS (Universal Agent Context System) is a Python library and MCP server for AI agent context management. We've completed Phase 2 (standalone packaging) and have:
- macOS ARM64 binary (`uacs-mcp`)
- Docker image (`uacs:latest`)
- GitHub installation via `uv pip install git+https://github.com/kylebrodeur/universal-agent-context.git`

## Your Mission

Create comprehensive integration guides and test UACS MCP server with major MCP clients (Claude Desktop, Cursor, Windsurf).

## Time Estimate: 8-10 hours

---

## Task 1: Claude Desktop Integration (3-4 hours)

### 1.1 Test Binary with Claude Desktop (1.5 hours)

**Steps:**
1. Install the binary: `./bin/install`
2. Locate Claude Desktop config:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Add UACS to config:
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
4. Restart Claude Desktop
5. Test available tools in Claude:
   - List all UACS tools
   - Test `discover_adapters`
   - Test `translate_skill`
   - Test `search_marketplace`
6. Document any issues or quirks

### 1.2 Test Docker with Claude Desktop (1 hour)

**Steps:**
1. Start Docker container: `./bin/docker-quickstart`
2. Configure Claude Desktop for SSE transport:
   ```json
   {
     "mcpServers": {
       "uacs": {
         "url": "http://localhost:3000/sse"
       }
     }
   }
   ```
3. Test same tools as above
4. Document differences from binary approach

### 1.3 Create Integration Guide (1.5 hours)

**Create:** `docs/integrations/CLAUDE_DESKTOP.md`

**Contents:**
```markdown
# UACS Integration with Claude Desktop

## Installation Methods

### Option 1: Binary (Recommended)
[Step-by-step instructions]

### Option 2: Docker
[Step-by-step instructions]

### Option 3: Python Package
[Step-by-step instructions]

## Configuration

### Finding the Config File
[Platform-specific paths]

### Configuration Examples
[JSON examples for each method]

## Testing the Integration

### Verifying Tools Appear
[How to check tools are loaded]

### Example Interactions
[Sample prompts to test UACS]

## Troubleshooting

### Common Issues
- MCP server not appearing
- Tools not loading
- Connection errors
- Permission issues

### Debug Mode
[How to enable verbose logging]

### Getting Help
[Where to report issues]
```

**Deliverables:**
- [ ] Working Claude Desktop config (binary)
- [ ] Working Claude Desktop config (Docker)
- [ ] Complete `docs/integrations/CLAUDE_DESKTOP.md`
- [ ] Screenshots of UACS tools in Claude Desktop
- [ ] List of any issues discovered

---

## Task 2: Cursor Integration (2-3 hours)

### 2.1 Test with Cursor Editor (1.5 hours)

**Steps:**
1. Install Cursor (if not already installed)
2. Configure MCP server in Cursor settings
3. Test context access from editor
4. Measure performance impact
5. Test key workflows:
   - Discovering available skills
   - Translating between formats
   - Searching marketplace
   - Using context compression

### 2.2 Create Integration Guide (1.5 hours)

**Create:** `docs/integrations/CURSOR.md`

**Contents:**
- Installation steps
- Configuration for Cursor
- Example use cases
- Performance considerations
- Troubleshooting

**Deliverables:**
- [ ] Working Cursor configuration
- [ ] Complete `docs/integrations/CURSOR.md`
- [ ] Performance notes (latency, memory usage)
- [ ] List of Cursor-specific considerations

---

## Task 3: Windsurf Integration (2-3 hours)

### 3.1 Test with Windsurf (1.5 hours)

**Steps:**
1. Install Windsurf
2. Configure MCP server
3. Test feature compatibility
4. Document any limitations

### 3.2 Create Integration Guide (1.5 hours)

**Create:** `docs/integrations/WINDSURF.md`

**Contents:**
- Installation steps
- Configuration
- Feature compatibility matrix
- Known limitations
- Troubleshooting

**Deliverables:**
- [ ] Working Windsurf configuration
- [ ] Complete `docs/integrations/WINDSURF.md`
- [ ] Feature compatibility notes

---

## Task 4: Integration Summary (1 hour)

### 4.1 Create Master Integration Guide

**Create:** `docs/INTEGRATIONS.md`

**Contents:**
```markdown
# UACS Integrations

UACS MCP Server works with any MCP-compatible client.

## Tested Integrations

- ✅ [Claude Desktop](integrations/CLAUDE_DESKTOP.md) - Full support
- ✅ [Cursor](integrations/CURSOR.md) - Full support
- ✅ [Windsurf](integrations/WINDSURF.md) - Full support

## Configuration Quick Reference

[Table comparing configuration across clients]

## General Troubleshooting

[Common issues across all clients]
```

### 4.2 Update Main README

Add integration section to README.md:
```markdown
## Integrations

UACS works with popular MCP clients:

- **Claude Desktop**: [Setup Guide](docs/integrations/CLAUDE_DESKTOP.md)
- **Cursor**: [Setup Guide](docs/integrations/CURSOR.md)
- **Windsurf**: [Setup Guide](docs/integrations/WINDSURF.md)

See [full integration guide](docs/INTEGRATIONS.md) for details.
```

**Deliverables:**
- [ ] `docs/INTEGRATIONS.md` created
- [ ] README.md updated with integrations section
- [ ] All guides cross-linked

---

## Validation Criteria

Before marking this task complete, verify:

1. **All integrations tested**:
   - ✅ Claude Desktop (binary + Docker)
   - ✅ Cursor
   - ✅ Windsurf

2. **Documentation complete**:
   - ✅ 3 integration guides created
   - ✅ Master INTEGRATIONS.md created
   - ✅ README updated

3. **Quality checks**:
   - ✅ All steps tested and verified
   - ✅ Screenshots included where helpful
   - ✅ Troubleshooting sections are practical
   - ✅ Configuration examples are copy-pasteable

4. **Issues documented**:
   - ✅ Any bugs found are filed as GitHub issues
   - ✅ Limitations clearly stated
   - ✅ Workarounds provided

---

## Questions to Answer

As you work through this, document answers to:

1. **Performance**: What's the latency overhead of UACS MCP server?
2. **Limitations**: Are there any features that don't work with certain clients?
3. **User Experience**: What's the smoothest installation path for each client?
4. **Debugging**: What are the most common configuration mistakes?
5. **Compatibility**: Do different MCP protocol versions matter?

---

## Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **UACS Docs**: `docs/` directory
- **Binary Location**: `/usr/local/bin/uacs-mcp` (after install)
- **Docker Image**: `uacs:latest`
- **Test Scripts**: `scripts/install_mcp_server.sh`, `scripts/docker_quickstart.sh`

---

## Notes for the Agent

- Take screenshots as you go (especially successful tool listings)
- Document exact error messages if you hit issues
- Test on a clean machine/environment if possible
- Focus on the user experience - what would make setup easier?
- Create issues for any bugs you find, but keep working
- If you can't test a client (e.g., no Windsurf access), document the limitation

**When complete, report back with:**
1. All deliverables checked off
2. Summary of findings
3. List of issues created
4. Recommendations for improving the integration experience
