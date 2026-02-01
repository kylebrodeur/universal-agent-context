# UACS v0.1.0 - Initial Release 🎉

**Release Date**: January 6, 2026

We're excited to announce the first release of **UACS (Universal Agent Context System)** - a comprehensive solution for AI agent context management!

## 🌟 What is UACS?

UACS is a universal system for discovering, translating, and managing AI agent capabilities across multiple formats. It provides:

- **Format Translation**: Convert between `.cursorrules`, `.clinerules`, `.agents.md`, and other agent skill formats
- **Context Compression**: Reduce token usage by 70%+ while preserving semantic meaning
- **Marketplace Integration**: Search and install agent skills from multiple registries
- **MCP Server**: Full Model Context Protocol implementation for integration with Claude Desktop, Cursor, and other MCP clients

## 📦 Installation Options

### Option 1: Python Package (from GitHub)
```bash
uv pip install git+https://github.com/kylebrodeur/universal-agent-context.git
```

### Option 2: Standalone Binary (macOS ARM64)
Download from the [Releases page](https://github.com/kylebrodeur/universal-agent-context/releases/tag/v0.1.0) or use the install script:
```bash
curl -fsSL https://raw.githubusercontent.com/kylebrodeur/universal-agent-context/main/scripts/install_mcp_server.sh | bash
```

### Option 3: Docker
```bash
docker run -d -p 3000:3000 --name uacs ghcr.io/kylebrodeur/uacs:0.1.0
```

Or use the quick start script:
```bash
./bin/docker-quickstart
```

Or create your own docker-compose.yml:
```yaml
services:
  uacs:
    image: ghcr.io/kylebrodeur/uacs:0.1.0
    ports:
      - "3000:3000"
    environment:
      - UACS_TRANSPORT=sse
```

## ✨ Key Features

### 🔌 MCP Server Integration
- **stdio transport** for Claude Desktop
- **SSE transport** for web-based clients
- Health check endpoint for monitoring
- <2 second startup time

### 📊 Context Management
- Discover agent skills across multiple formats
- Translate between formats automatically
- Compress context for efficient token usage
- Built-in validation and error checking

### 🛍️ Marketplace
- Search across multiple skill registries
- Install skills directly from CLI
- Package validation and security scanning
- Local caching for fast searches

### 🧠 Memory System
- Simple in-memory storage
- Query and retrieve agent history
- Cross-session persistence (optional)

## 📈 Performance Metrics

- **Binary Size**: 23MB (macOS ARM64)
- **Docker Image**: 228MB
- **Startup Time**: <2 seconds
- **Compression Ratio**: 70%+ typical
- **Test Coverage**: 90%+ (145 unit + 18 integration tests)

## 🚀 Quick Start

### CLI Usage
```bash
# Discover available context formats
uacs skills discover

# Start MCP server
uacs serve --port 8080

# Search marketplace for agent skills
uacs marketplace search "python testing"
```

### Python API
```python
from uacs import UnifiedContext

# Create context manager
context = UnifiedContext()

# Discover adapters
adapters = context.discover_adapters()

# Translate a skill
translated = context.translate_skill(
    source="path/to/.cursorrules",
    target_format="agent_skill"
)
```

### MCP Server
```bash
# Start in stdio mode (for Claude Desktop)
uacs-mcp --transport stdio

# Start in SSE mode (for web clients)
uacs-mcp --transport sse --port 3000
```

## 📚 Documentation

- **[README](https://github.com/kylebrodeur/universal-agent-context/blob/main/README.md)** - Project overview
- **[Quick Start Guide](https://github.com/kylebrodeur/universal-agent-context/blob/main/QUICKSTART.md)** - Tutorials
- **[Library Guide](https://github.com/kylebrodeur/universal-agent-context/blob/main/docs/LIBRARY_GUIDE.md)** - Python API
- **[CLI Reference](https://github.com/kylebrodeur/universal-agent-context/blob/main/docs/CLI_REFERENCE.md)** - Command-line usage
- **[MCP Server Setup](https://github.com/kylebrodeur/universal-agent-context/blob/main/docs/MCP_SERVER_SETUP.md)** - Integration guide

## 🔧 Technical Details

- **Python**: 3.11+ required
- **Key Dependencies**: typer, rich, httpx, pydantic, tiktoken, mcp
- **Build Tools**: PyInstaller 6.17.0, uv package manager
- **Container**: Alpine Linux base
- **License**: MIT

## 🙏 Acknowledgments

UACS builds on:
- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- The AI agent skills ecosystem
- Multi-agent orchestration patterns

## 🔮 What's Next

Upcoming features (Phase 3-6):
- Windows and Linux binaries
- Integration guides for Claude Desktop, Cursor, and Windsurf
- Additional marketplace registries (Smithery.ai, GitHub Topics)
- Enhanced memory system with semantic search
- Performance optimizations and caching
- Security hardening and audit

## 📝 Full Changelog

See [CHANGELOG.md](https://github.com/kylebrodeur/universal-agent-context/blob/main/CHANGELOG.md) for complete details.

## 🐛 Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/kylebrodeur/universal-agent-context/issues/new/choose).

## 💬 Community

- **Discussions**: [GitHub Discussions](https://github.com/kylebrodeur/universal-agent-context/discussions)
- **Issues**: [GitHub Issues](https://github.com/kylebrodeur/universal-agent-context/issues)

---

**Download the release assets below to get started!** 🚀
