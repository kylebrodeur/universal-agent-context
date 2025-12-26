# Universal Agent Context System (UACS)

**A universal system for discovering, translating, and managing AI agent capabilities**

UACS provides a unified approach to working with AI agent context across different formats, tools, and environments. It combines format translation, skills discovery, context compression, and persistent memory into a single, cohesive system.

## What is UACS?

UACS is three things:

1. **Python Library** - Programmatic access to context management, format translation, and marketplace discovery
2. **CLI Tool** - Command-line interface for managing skills, context, and memory
3. **MCP Server** - Model Context Protocol server for seamless IDE integration

### Key Features

- **Format Translation** - Convert between SKILLS.md, AGENTS.md, .cursorrules, .clinerules, and system prompts
- **Context Compression** - Achieve 70%+ compression with intelligent deduplication and summarization
- **Unified Marketplace** - Discover and install both skills and MCP servers from a single source
- **Memory System** - Persistent storage with project and global scopes
- **MCP Integration** - Expose context and skills to AI assistants via Model Context Protocol

## Installation

```bash
pip install universal-agent-context
```

## Quick Start

### Using the Library

```python
from uacs import UACS

# Initialize UACS for current project
uacs = UACS()

# Get skills from current context
skills = uacs.get_skills()
print(f"Found {len(skills)} skills")

# Search marketplace
results = uacs.marketplace.search("testing")
for result in results:
    print(f"{result.name}: {result.description}")

# Compress context
compressed = uacs.context.get_compressed_context(max_tokens=4000)
```

### Using the CLI

```bash
# View available skills
uacs skills list

# Search marketplace
uacs marketplace search "testing"

# Install a skill
uacs marketplace install agentskills/python-testing

# Check context statistics
uacs context stats

# View memory
uacs memory stats

# Start MCP server
uacs serve
```

### Using as MCP Server

Add to your MCP client configuration (e.g., Claude Desktop):

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
