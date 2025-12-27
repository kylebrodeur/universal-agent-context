# Universal Agent Context System (UACS)

**Context Management Infrastructure for AI Agents**

UACS is agent middleware - infrastructure that makes existing AI tools better, not another CLI competing for attention.

[![Tests](https://img.shields.io/badge/tests-100%2B%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

---

## The Problem

Building with AI agents today means:

- 😫 **Context switching** - Maintaining separate configs for Claude, Gemini, Copilot (SKILLS.md, .cursorrules, .clinerules, AGENTS.md)
- 😫 **Copy-paste errors** - Manually syncing instructions across formats
- 😫 **Token waste** - Large contexts cost money, no intelligent compression
- 😫 **Tool isolation** - Each agent tool manages skills/context separately
- 😫 **Memory fragmentation** - Context lost between agent sessions

## The Solution

UACS provides three integration points:

1. **Python Library** - Direct use by developers building agent applications
2. **CLI Tool** - `uacs` commands for local development and scripting  
3. **MCP Server** - Expose UACS capabilities to Claude Desktop, Cursor, Windsurf, Cline

**The 10x Insight:**
> Other tools can use UACS via MCP to get marketplace search, format conversion, context compression, and memory - making them 10x better without competing with them.

---

## What Makes UACS Different

- 🔄 **Format Translation** - Converts between 5+ formats (SKILLS.md, AGENTS.md, .cursorrules, .clinerules, ADK Config)
- 🗜️ **70%+ Compression** - Intelligent context compression with LLM-based summarization
- 🏪 **Unified Marketplace** - Skills + MCP servers in one search with caching
- 🎯 **Topic-Based Retrieval** - Auto-tagging and focused context
- 🧠 **Memory System** - Long-term memory with project and global scopes
- ⚡ **Smart Caching** - 24hr TTL cache for marketplace, <200ms cached searches
- 🐍 **Standalone Library** - Python API, not just CLI

**vs Similar Tools:**

| Feature | UACS | openskills | ai-agent-skills |
|---------|------|------------|-----------------|
| Format Translation | ✅ 5+ formats | ❌ Skills only | ❌ Skills only |
| Context Compression | ✅ 70%+ savings | ❌ None | ❌ None |
| Marketplace | ✅ Skills + MCP | ✅ Skills only | ✅ Skills catalog |
| Memory System | ✅ Project + Global | ❌ None | ❌ None |
| MCP Server | ✅ Full integration | ❌ None | ❌ None |
| Python API | ✅ Complete | ⚠️ Limited | ⚠️ Limited |

See [LAUNCH_STRATEGY.md](docs/LAUNCH_STRATEGY.md) for full positioning and [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) for development status.

---

## Quick Start

### Installation

```bash
# Option 1: PyPI (Coming in Phase 3)
pip install universal-agent-context

# Option 2: From source (Current)
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync

# Initialize
uacs context init
uacs memory init
```

### Three Ways to Use UACS

#### 1. Python Library

```python
from uacs import UACS
from pathlib import Path

# Initialize
uacs = UACS(project_path=Path.cwd())

# Search marketplace
results = uacs.search("python testing")

# Install skill
uacs.install(results[0].name)

# Get compressed context
context = uacs.get_compressed_context(
    topic="testing",
    max_tokens=4000  # 70% compression applied
)

# Memory management
uacs.memory.add("Important: Always use pytest-asyncio for async tests")
relevant = uacs.memory.search("async testing")
```

#### 2. CLI Tool

```bash
# Marketplace
uacs marketplace search "python testing"
uacs marketplace install pytest-skill

# Format conversion
uacs skills convert --from cursorrules --to skills

# Context management
uacs context stats
uacs context compress --max-tokens 4000

# Memory
uacs memory add "Important insight"
uacs memory search "relevant topic"
```

#### 3. MCP Server (For Claude Desktop, Cursor, Windsurf)

```bash
# Start MCP server
uacs serve

# Or with uvx (one-liner)
uvx universal-agent-context serve
```

**Configure in Claude Desktop:**
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "uacs": {
      "command": "uacs",
      "args": ["serve"],
      "env": {
        "UACS_PROJECT_PATH": "/path/to/your/project"
      }
    }
  }
}
```

**Now Claude Desktop can:**
- Search your local skills and marketplace
- Convert between formats on-the-fly
- Compress large contexts automatically
- Access your project memory
- Install skills directly from conversation

---

## Core Features

### 🔄 Format Translation

Convert between 5+ agent instruction formats:

```bash
# Convert .cursorrules to SKILLS.md
uacs skills convert --from cursorrules --to skills
```

**Supported Formats:**
- ✅ Agent Skills (SKILLS.md) - Anthropic standard
- ✅ AGENTS.md - Project context standard
- ✅ .cursorrules - Cursor IDE format
- ✅ .clinerules - Cline VSCode extension
- ✅ ADK Agent Config - Google ADK format (Phase 7)

### 🗜️ Token Compression

**4-layer compression achieving 70%+ savings:**

| Technique | Savings | How |
|-----------|---------|-----|
| Deduplication | 40% | Hash-based duplicate detection |
| Summarization | 75% | LLM-based context condensing |
| Topic Filtering | 85% | Send only relevant context |
| Progressive Context | 90% | Incremental updates |

**Real-world example:**
- Before: 10,000 tokens → $0.10 per call
- After: 3,000 tokens → $0.03 per call
- **Savings:** 70% cost reduction

### 🏪 Unified Marketplace

Search across Skills + MCP servers:

```bash
# Search everything
uacs marketplace search "filesystem"

# Skills only
uacs marketplace search "python testing" --type skill

# Cache management
uacs marketplace cache --status
```

**Performance:**
- <500ms for marketplace search
- <200ms for cached results

### 🧠 Memory System

Persistent memory with project and global scopes:

```bash
# Initialize
uacs memory init

# Add project memory
uacs memory add "Use pytest-asyncio for async tests"

# Search
uacs memory search "testing patterns"
```

---

## Documentation

**Getting Started:**
- [Installation Guide](docs/INSTALLATION.md) (Coming in Phase 1)
- [Quick Start](docs/QUICKSTART.md) (Coming in Phase 1)

**User Guides:**
- [Library Guide](docs/LIBRARY_GUIDE.md) - Python API reference
- [CLI Reference](docs/CLI_REFERENCE.md) - Command documentation
- [MCP Server Setup](docs/MCP_SERVER_SETUP.md) - MCP integration guide

**Advanced:**
- [Adapters](docs/ADAPTERS.md) - Format translation
- [Context Management](docs/CONTEXT.md) - Compression and memory
- [Marketplace](docs/MARKETPLACE.md) - Skills and MCP discovery

**Development:**
- [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md) - Development status
- [Launch Strategy](docs/LAUNCH_STRATEGY.md) - Marketing and positioning
- [Contributing](docs/CONTRIBUTING.md) (Coming in Phase 1)

---

## Development Status

**Current Phase:** Phase 0 Complete (Spinout) ✅

### Completed
- ✅ Repository created and code migrated
- ✅ 100+ tests passing independently
- ✅ Core documentation in place
- ✅ Clean separation from MAOS

### Next Steps (8-Week Launch Plan)
- **Week 1:** Polish & Documentation
- **Week 2:** MCP Server Packaging
- **Week 3:** PyPI Publishing
- **Week 4:** Public Launch

See [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) for complete plan.

---

## Integration Examples

### Claude Desktop
```json
{
  "mcpServers": {
    "uacs": {
      "command": "uacs",
      "args": ["serve"]
    }
  }
}
```

### Python Application
```python
from uacs import UACS

class MyAgent:
    def __init__(self):
        self.uacs = UACS(project_path=Path.cwd())
    
    def get_context(self, task):
        return self.uacs.get_compressed_context(
            topic=task,
            max_tokens=4000
        )
```

---

## Requirements

- Python >= 3.11
- Optional: Node.js (for MCP filesystem server)
- Optional: Docker (for containerized deployment)

---

## Related Projects

### Multi-Agent CLI (MAOS)
- **Repository:** [github.com/kylebrodeur/multi-agent-cli](https://github.com/kylebrodeur/multi-agent-cli)
- **Relationship:** MAOS uses UACS for context management
- **Focus:** Multi-agent orchestration with ADK

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Acknowledgments

- **Anthropic** - Agent Skills specification and MCP protocol
- **Google** - Agent Development Kit (ADK)
- **OpenAI** - AGENTS.md standard
- **Community** - Skills marketplace contributors

---

**Status:** Phase 0 Complete ✅ | **Next:** Phase 1 (Polish & Documentation)  
**Version:** 0.1.0-dev | **Last Updated:** December 26, 2025
      "command": "uacs",
      "args": ["serve"]
    }
  }
}
```

## Documentation

- [Library Guide](docs/LIBRARY_GUIDE.md) - How to use UACS in your Python code
- [CLI Reference](docs/CLI_REFERENCE.md) - Command-line interface documentation
- [Context Management](docs/CONTEXT.md) - Understanding the unified context system
- [Marketplace Guide](docs/MARKETPLACE.md) - Discovering and installing skills
- [Format Adapters](docs/ADAPTERS.md) - Supported file formats and custom adapters

## Examples

Check out the `examples/` directory for working code samples:

- [Basic Context](examples/basic_context.py) - Initialize and use the context system
- [Marketplace Search](examples/marketplace_search.py) - Search for skills and MCP servers
- [Custom Adapter](examples/custom_adapter.py) - Create a custom format adapter
- [Memory Usage](examples/memory_usage.py) - Use persistent memory
- [MCP Tools](examples/mcp_tool_usage.py) - Programmatic access to MCP tools

## Development

```bash
# Clone the repository
git clone https://github.com/kylebrodeur/universal-agent-context.git
cd universal-agent-context

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .
ruff check --fix .
```

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Related Projects

- [Multi-Agent CLI](https://github.com/kylebrodeur/multi-agent-cli) - Multi-agent orchestration system that uses UACS
