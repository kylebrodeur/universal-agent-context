# UACS Quick Start Guide

**Get productive with UACS in 5 minutes.**

This guide walks you through installation and your first useful commands. For comprehensive tutorials, see [README.md](README.md).

---

## Prerequisites

- Python 3.11+
- `uv` package manager (recommended) or `pip`

---

## Installation (Choose One)

### Option 1: From Source (Current - v0.1.0)

```bash
# Clone and install
git clone https://github.com/yourusername/universal-agent-context.git
cd universal-agent-context
uv sync --all-extras
```

### Option 2: From PyPI (Coming Soon)

```bash
pip install universal-agent-context
```

### Option 3: With uvx (Coming Soon)

```bash
uvx universal-agent-context --help
```

---

## First Command (30 seconds)

Verify installation and explore capabilities:

```bash
uacs --help
```

**Expected output:**
```
Usage: uacs [OPTIONS] COMMAND [ARGS]...

  Universal Agent Context System (UACS)

Commands:
  context      Context management commands
  marketplace  Search and install skills/MCP servers
  memory       Persistent memory management
  skills       Skill management commands
  mcp          MCP server operations
```

Try getting version info:

```bash
uacs --version
# Output: uacs, version 0.1.0
```

---

## Quick Wins

### 1. Search the Marketplace (1 minute)

Find skills and MCP servers instantly:

```bash
# Search for testing-related tools
uacs marketplace search "testing"

# Search for Python skills
uacs marketplace search "python"

# List all available packages
uacs marketplace list
```

**Expected output:**
```
🔍 Searching for "testing"...

Found 3 packages:
  📦 pytest-skills (skill)
     Testing utilities and patterns for Python
     Source: github.com/examples/pytest-skills

  📦 test-automation (skill)
     Automated testing frameworks
     Source: github.com/examples/test-automation
```

### 2. Format Conversion (2 minutes)

Convert agent configs between formats:

```bash
# Create a sample SKILLS.md
cat > SKILLS.md << 'EOF'
# Skills

## Code Review
Expert at reviewing code for bugs, security, and best practices.

**Triggers:** "review this", "check for bugs"

## Testing
Create comprehensive test suites using pytest.

**Triggers:** "write tests", "test coverage"
EOF

# Convert to Cursor format
uacs skills convert --to cursorrules --output .cursorrules

# Convert to Cline format
uacs skills convert --to clinerules --output .clinerules

# View converted content
cat .cursorrules
```

**Result:** One source of truth → multiple agent formats. Zero manual sync.

### 3. Python API - Context Compression (1 minute)

Save 70% on token costs with intelligent compression:

```python
from uacs import UACS
from pathlib import Path

# Initialize
uacs = UACS(Path.cwd())

# Get compressed context (70% savings)
context = uacs.get_compressed_context(max_tokens=3000)

print(f"Token count: {context['token_count']}")
print(f"Content preview: {context['content'][:200]}...")
```

**Save to file:**

```bash
cat > quick_test.py << 'EOF'
from uacs import UACS
from pathlib import Path

uacs = UACS(Path.cwd())
context = uacs.get_compressed_context(max_tokens=3000)
print(f"✅ Compressed to {context['token_count']} tokens")
print(f"📝 Content length: {len(context['content'])} chars")
EOF

uv run python quick_test.py
```

**Expected output:**
```
✅ Compressed to 2847 tokens
📝 Content length: 12438 chars
```

### 4. Memory System - Persistent Context (1 minute)

Store information across agent sessions:

```python
from uacs.memory import SimpleMemoryStore
from pathlib import Path

# Initialize memory
store = SimpleMemoryStore(project_path=Path.cwd())
store.init_storage("project")

# Store a memory
store.add_memory(
    content="User prefers pytest over unittest",
    tags=["preference", "testing"],
    scope="project"
)

# Retrieve memories
memories = store.search_memories(query="testing", scope="project")
for mem in memories:
    print(f"- {mem.content}")
```

**Save to file:**

```bash
cat > memory_test.py << 'EOF'
from uacs.memory import SimpleMemoryStore
from pathlib import Path

store = SimpleMemoryStore(project_path=Path.cwd())
store.init_storage("project")

# Add memories
store.add_memory(
    content="User prefers Python for backend",
    tags=["preference", "tech"],
    scope="project"
)

store.add_memory(
    content="Project uses GitHub Actions for CI/CD",
    tags=["devops", "deployment"],
    scope="project"
)

# Search
print("🧠 Stored memories about 'tech':")
results = store.search_memories(query="tech", scope="project")
for mem in results:
    print(f"  - {mem.content}")
EOF

uv run python memory_test.py
```

**Expected output:**
```
🧠 Stored memories about 'tech':
  - User prefers Python for backend
```

---

## What You Just Learned

✅ **Installation** - Set up UACS from source  
✅ **CLI basics** - Navigate commands with `uacs --help`  
✅ **Marketplace** - Search skills and MCP servers instantly  
✅ **Format conversion** - One config → multiple formats  
✅ **Context compression** - Save 70% on token costs  
✅ **Memory system** - Persist context across sessions

---

## Next Steps

### Explore More Features

1. **Full Tutorial** - [README.md](README.md) - Complete walkthrough with real examples
2. **MCP Server** - [docs/MCP_SERVER_SETUP.md](docs/MCP_SERVER_SETUP.md) - Use with Claude Desktop
3. **Custom Adapters** - [docs/ADAPTERS.md](docs/ADAPTERS.md) - Add new format support
4. **API Reference** - [docs/LIBRARY_GUIDE.md](docs/LIBRARY_GUIDE.md) - Python API documentation
5. **Marketplace** - [docs/MARKETPLACE.md](docs/MARKETPLACE.md) - Publishing and discovery

### Common Tasks

**Initialize a new project:**
```bash
uacs context init
# Creates .uacs/ directory with default config
```

**Check context stats:**
```bash
uacs context stats
# Shows token counts, compression ratios
```

**Install a skill from marketplace:**
```bash
uacs marketplace install pytest-skills
```

**Run MCP server:**
```bash
uacs mcp serve --port 8080
# Exposes UACS via MCP protocol
```

### Join the Community

- **Issues:** [GitHub Issues](https://github.com/yourusername/universal-agent-context/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/universal-agent-context/discussions)
- **License:** MIT

---

## Troubleshooting

**Command not found?**
```bash
# If using uv sync, activate with:
source .venv/bin/activate
uacs --help

# Or always prefix with uv run:
uv run uacs --help
```

**Import errors?**
```bash
# Ensure dependencies installed:
uv sync --all-extras

# Or with pip:
pip install -e ".[dev,mcp,all]"
```

**MCP server won't start?**
```bash
# Check port availability:
lsof -i :8080

# Try different port:
uacs mcp serve --port 8081
```

---

**Time to productivity: 5 minutes ⚡**

Ready for more? Head to [README.md](README.md) for the complete guide.
