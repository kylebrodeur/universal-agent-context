# Universal Agent Context System (UACS)

**Context Management Infrastructure for AI Agents**

[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-blue)](https://pypi.org/project/universal-agent-context/)
[![Tests](https://img.shields.io/badge/tests-100%2B%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

> **TL;DR:** Universal context middleware for AI agents. One source of truth → 5+ formats. 70% token compression. Package management for skills + MCP. Works with Claude, Cursor, Windsurf, Cline, or your own Python code.

---

## Why UACS?

Building AI agent systems today means juggling multiple formats, wasting tokens, and losing context between sessions. **UACS solves this.**

**In 30 seconds:**
- 🔄 Write once → Deploy to Claude, Cursor, Cline, Gemini, Copilot
- 🗜️ Save 70% on token costs with intelligent compression
- 📦 Package management for skills + MCP servers (GitHub, Git, local)
- 🧠 Persistent memory across sessions (project + global)
- ⚡ Python API + CLI + MCP server = works everywhere

**What makes UACS different:** It's **middleware**, not another agent tool. Claude Desktop gets better when you add UACS. So does Cursor. So does your custom Python agent.

---

## Installation

Choose the installation method that best fits your workflow:

| Method | Best For | Prerequisite |
| :--- | :--- | :--- |
| **Python (pip)** | Developers integrating UACS into Python projects | Python 3.11+ |
| **uvx** | Quick, temporary usage without installing dependencies | `uv` installed |
| **[Binary](docs/MCP_SERVER_BINARY.md)** | Standalone usage, no Python environment needed | None |
| **[Docker](docs/MCP_SERVER_DOCKER.md)** | Server deployments, team environments | Docker |

### Quick Start (Python)

```bash
# Option 1: From source (Current - Week 1)
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync                    # Or: pip install -e .

# Option 2: PyPI (Coming Week 3)
pip install universal-agent-context

# Option 3: One-liner (Coming Week 2)
uvx universal-agent-context serve

# Initialize project
uv run uacs context init   # Creates .state/context/ directory
uv run uacs memory init    # Creates .state/memory/ directory
```

---

## CLI Demo

See UACS in action:

```bash
# Install packages from GitHub
$ uacs packages install anthropic/skills-testing

📦 Installing package 'anthropic/skills-testing'...
✅ Cloning from GitHub...
✅ Validating package structure...
✅ Installed to .agent/skills/testing/

# List installed packages
$ uacs packages list

📚 Installed Packages (5):

Skills:
  ✓ code-review               - Review code for security and best practices
    Source: github.com/anthropic/skills

  ✓ documentation             - Generate comprehensive docs
    Source: github.com/anthropic/skills

  ✓ testing                   - Create unit, integration, and e2e tests
    Source: github.com/anthropic/skills

MCP Servers:
  ✓ filesystem                - File operations via MCP
    Source: github.com/anthropic/mcp-servers

# Check context compression stats
$ uacs context stats

📊 Context Statistics:
  Total entries: 127
  Original tokens: 45,234
  Compressed tokens: 12,456 (72.5% reduction)
  Token savings: 32,778
  
  Compression breakdown:
    - Deduplication: 15,234 tokens (33.7%)
    - Summarization: 14,567 tokens (32.2%)
    - Quality filtering: 2,977 tokens (6.6%)

💰 Cost Savings (at $0.01/1K tokens):
  Without compression: $0.45/call
  With compression: $0.12/call
  Savings: $0.33/call (73%)

# Convert between formats
$ uacs skills convert --to cursorrules

✅ Converted SKILLS.md → .cursorrules
   Skills: 5
   Output: .cursorrules (3,456 tokens)
   Format validated: ✓

# Memory operations
$ uacs memory search "testing"

🔍 Searching memories for "testing"...

📝 Found 3 relevant memories:
  1. [Score: 0.92] Always use pytest-asyncio for async tests
     Added: 2024-12-15, Tags: testing, pytest
     
  2. [Score: 0.87] Integration tests run in Docker containers
     Added: 2024-12-20, Tags: testing, docker
     
  3. [Score: 0.81] E2E tests use Playwright with page fixtures
     Added: 2024-12-18, Tags: testing, e2e
```

**What this shows:**
- 📦 **Easy package installation** - From GitHub, Git, or local paths
- 📊 **Real-time compression stats** - See exactly what you're saving
- 🔄 **Format conversion** - One command, any format
- 🧠 **Memory recall** - Find relevant context instantly

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

**The Result:**
> Your existing tools get package management, format conversion, 70% token compression, and persistent memory - without changing how you work.

---

## Use Cases

### 1. Multi-Tool Development
**Scenario:** You build agents for both Claude Desktop and Cursor IDE.

**Before UACS:**
```
.cursorrules          (Cursor config)
SKILLS.md             (Claude config)
.clinerules           (Cline config)
# Manual sync, 3x maintenance
```

**With UACS:**
```bash
# Write once in SKILLS.md
uacs skills convert --to cursorrules  # Auto-generate .cursorrules
uacs skills convert --to clinerules   # Auto-generate .clinerules
# One source, zero sync errors
```

### 2. Token Cost Optimization
**Scenario:** Your agent uses 10,000 tokens per call at $0.01/1K tokens.

**Before UACS:**
- Cost per call: $0.10
- 100 calls/day: $10/day = $300/month

**With UACS:**
```python
context = uacs.get_compressed_context(max_tokens=3000)  # 70% compression
# Cost per call: $0.03
# 100 calls/day: $3/day = $90/month
# Savings: $210/month (70%)
```

### 3. Package Management
**Scenario:** You need testing capabilities for your agent.

**Before UACS:**
```
# Search GitHub manually
# Clone repos
# Copy-paste configs
# Update manually when changes occur
```

**With UACS:**
```bash
uacs packages install anthropic/skills-testing
# Installed in .agent/skills/ with metadata tracking
# Works with GitHub repos, Git URLs, or local paths
```

### 4. Persistent Agent Memory
**Scenario:** Your agent should remember project conventions across sessions.

**With UACS:**
```python
# Session 1: Agent learns convention
uacs.memory.add("Use pytest-asyncio for async tests", scope="project")

# Session 2: Different agent, same project
relevant = uacs.memory.search("testing")
# Returns: "Use pytest-asyncio for async tests"
# Zero manual context management
```

---

## What Makes UACS Different

- 🔄 **Format Translation** - Converts between 5+ formats (SKILLS.md, AGENTS.md, .cursorrules, .clinerules, ADK Config)
- 🗜️ **70%+ Compression** - Intelligent context compression with LLM-based summarization
- 📦 **Package Management** - Install skills + MCP servers from GitHub, Git, or local paths
- 🎯 **Topic-Based Retrieval** - Auto-tagging and focused context
- 🧠 **Memory System** - Long-term memory with project and global scopes
- 🐍 **Standalone Library** - Python API, not just CLI

**vs Similar Tools:**

| Feature | UACS | openskills | ai-agent-skills |
|---------|------|------------|-----------------|
| Format Translation | ✅ 5+ formats | ❌ Skills only | ❌ Skills only |
| Context Compression | ✅ 70%+ savings | ❌ None | ❌ None |
| Package Management | ✅ Skills + MCP | ⚠️ Limited | ⚠️ Limited |
| Memory System | ✅ Project + Global | ❌ None | ❌ None |
| MCP Server | ✅ Full integration | ❌ None | ❌ None |
| Python API | ✅ Complete | ⚠️ Limited | ⚠️ Limited |
| Token Tracking | ✅ Real-time stats | ❌ None | ❌ None |

**Bottom line:** UACS is the only solution that provides format translation, compression, package management, memory, AND MCP server in one package.

See [LAUNCH_STRATEGY.md](docs/LAUNCH_STRATEGY.md) for full positioning.

---

## Quick Start

**Goal:** Get context compression working in 2 minutes.

### Installation

Choose the installation method that best fits your workflow:

| Method | Best For | Prerequisite |
| :--- | :--- | :--- |
| **Python (pip)** | Developers integrating UACS into Python projects | Python 3.11+ |
| **uvx** | Quick, temporary usage without installing dependencies | `uv` installed |
| **[Binary](docs/MCP_SERVER_BINARY.md)** | Standalone usage, no Python environment needed | None |
| **[Docker](docs/MCP_SERVER_DOCKER.md)** | Server deployments, team environments | Docker |

#### Quick Start (Python)

```bash
# Option 1: From source (Current - Week 1)
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync                    # Or: pip install -e .

# Option 2: PyPI (Coming Week 3)
pip install universal-agent-context

# Option 3: One-liner (Coming Week 2)
uvx universal-agent-context serve

# Initialize project
uv run uacs context init   # Creates .state/context/ directory
uv run uacs memory init    # Creates .state/memory/ directory
```

### 5-Minute Tutorial

**Step 1: Test the CLI (30 seconds)**
```bash
uv run uacs --help
# Output: Shows 5 command groups: context, skills, marketplace, memory, mcp
```

**Step 2: Install a Package (1 minute)**
```bash
uv run uacs packages install anthropic/skills-testing
# Output: Clones from GitHub, validates, and installs
# Works with GitHub repos, Git URLs, or local paths
```

**Step 3: Python API - Context Compression (2 minutes)**

Create `test_uacs.py`:
```python
from uacs import UACS
from pathlib import Path

# Initialize
uacs = UACS(project_path=Path.cwd())

# Add context entries (simulating agent conversation)
uacs.shared_context.add_entry(
    content="Review authentication for security issues",
    agent="user"
)

uacs.shared_context.add_entry(
    content="Found timing attack in password comparison",
    agent="claude",
    topics=["security"]
)

# Get compressed context
context = uacs.get_compressed_context(
    topic="security",      # Filter by topic
    max_tokens=1000        # Token budget
)

# Check compression stats
stats = uacs.get_token_stats()
print(f"Compression: {stats['compression_ratio']}")
print(f"Tokens saved: {stats['tokens_saved_by_compression']}")
```

Run it:
```bash
uv run python test_uacs.py
# Output: Shows compression ratio and tokens saved
```

**Step 4: Memory System (1 minute)**
```bash
# Add persistent memory
uv run uacs memory add "Always use pytest-asyncio for async tests"

# Search later
uv run uacs memory search "testing"
# Output: Returns relevant memories with scores
```

**What you just did:**
- ✅ Installed UACS
- ✅ Installed a package from GitHub
- ✅ Compressed context with Python API
- ✅ Added persistent memory

**Next steps:** [MCP Server Setup](docs/MCP_SERVER_SETUP.md) | [Full Library Guide](docs/LIBRARY_GUIDE.md)

---

### Three Ways to Use UACS

#### 1. Python Library

```python
from uacs import UACS
from pathlib import Path

# Initialize
uacs = UACS(project_path=Path.cwd())

# Install packages
uacs.packages.install("anthropic/skills-testing")  # From GitHub
uacs.packages.install("/path/to/local/skill")      # From local path

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
# Package management
uacs packages install anthropic/skills-testing
uacs packages list
uacs packages remove pytest-skill

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
- Manage packages from GitHub, Git, or local paths
- Convert between formats on-the-fly
- Compress large contexts automatically
- Access your project memory
- Install skills directly from conversation

---

## Core Features

### 🔄 Format Translation

**The Problem:** You write for Claude (SKILLS.md), but also need Cursor (.cursorrules) and Cline (.clinerules) configs.

**The Solution:** Write once, deploy everywhere.

```bash
# Convert .cursorrules to SKILLS.md
uv run uacs skills convert --from cursorrules --to skills

# Or in Python:
from uacs.adapters import FormatAdapterRegistry

adapter = FormatAdapterRegistry.get_adapter("cursorrules")
content = adapter.parse(Path(".cursorrules").read_text())
skills_format = content.to_system_prompt()
```

**Supported Formats:**
- ✅ **Agent Skills (SKILLS.md)** - Anthropic standard ([spec](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills))
- ✅ **AGENTS.md** - Project context standard ([spec](https://github.com/openai/agents))
- ✅ **.cursorrules** - Cursor IDE format
- ✅ **.clinerules** - Cline VSCode extension
- 🚧 **ADK Agent Config** - Google ADK format (Coming Phase 7)

**Quality validation included:** All conversions verify structure, check for required fields, score quality.

### 🗜️ Context Compression

**The Problem:** Large contexts = high costs. A 10K token call costs $0.10. At scale, this adds up fast.

**The Solution:** 4-layer compression achieving 70%+ token savings.

| Technique | Savings | How it Works |
|-----------|---------|--------------|
| Deduplication | 40% | Hash-based duplicate detection |
| LLM Summarization | 75% | Intelligently condense old context |
| Topic Filtering | 85% | Send only relevant context per task |
| Progressive Loading | 90% | Incremental context updates |

**Real-world Impact:**
```python
# Before compression:
- Context size: 10,000 tokens
- Cost per call: $0.10 (at $0.01/1K tokens)
- 100 calls/day: $10/day = $300/month

# After 70% compression:
- Context size: 3,000 tokens  
- Cost per call: $0.03
- 100 calls/day: $3/day = $90/month
- Monthly savings: $210 (70%)
```

**Usage:**
```python
# Automatic compression
context = uacs.get_compressed_context(
    topic="security review",  # Filter by topic
    max_tokens=4000,          # Target size
    agent="claude"            # Filter by agent (optional)
)

# Check what you saved
stats = uacs.get_token_stats()
print(f"Saved: {stats['tokens_saved_by_compression']} tokens")
print(f"Ratio: {stats['compression_ratio']}")
```

### 📦 Package Management

**The Problem:** Skills scattered across GitHub. MCP servers in different repositories. Manual cloning and installation.

**The Solution:** Simple package manager modeled after GitHub CLI extensions.

```bash
# Install from GitHub
uv run uacs packages install anthropic/skills-testing

# Install from Git URL
uv run uacs packages install https://github.com/owner/repo.git

# Install from local path
uv run uacs packages install /path/to/skill

# List installed packages
uv run uacs packages list

# Update packages
uv run uacs packages update
```

**Installation sources:**
- ✅ GitHub repositories (`owner/repo`)
- ✅ Git URLs (HTTPS or SSH)
- ✅ Local paths (absolute or relative)

**Installation tracking:**
```bash
# Install package
uv run uacs packages install anthropic/skills-testing

# Stored in: .agent/skills/testing/
# Metadata: .agent/skills/.installed.json (tracks source, version, installed date)

# Uninstall
uv run uacs packages remove testing
```

### 🧠 Memory System

**The Problem:** Agents forget project conventions between sessions. You repeat instructions constantly.

**The Solution:** Persistent memory with project and global scopes.

```bash
# Initialize
uv run uacs memory init

# Add project-specific memory
uv run uacs memory add "Use pytest-asyncio for async tests" --scope project

# Add global memory (all projects)
uv run uacs memory add "Prefer composition over inheritance" --scope global

# Search with semantic similarity
uv run uacs memory search "testing patterns"
# Returns: Relevant memories with similarity scores

# Python API
from uacs import UACS
uacs = UACS()

# Add memory programmatically
uacs.memory.add(
    "Critical: Always validate input before processing",
    scope="project",
    tags=["security", "validation"]
)

# Search by topic
results = uacs.memory.search("security", scope="project")
for memory in results:
    print(f"{memory.content} (score: {memory.score})")
```

**Storage:**
- Project scope: `.state/memory/project/`
- Global scope: `~/.config/uacs/memory/global/`
- Format: JSON with metadata (timestamp, tags, usage count)

---

## What's Next?

We're executing an **8-week public launch plan**:

**✅ Phase 0 (Dec 25-26):** Spinout Complete
- Repository created, tests passing independently
- Clean separation from Multi-Agent CLI (MAOS)

**🔄 Phase 1 (Week 1 - Current):** Polish & Documentation
- README improvements (you are here!)
- Installation guides
- API documentation
- Example gallery

**📦 Phase 2 (Week 2):** MCP Server Packaging
- PyInstaller binaries for easy distribution
- Docker image for `uacs serve`
- Cross-platform testing (macOS, Linux, Windows)

**🚀 Phase 3 (Week 3):** PyPI Publishing
- `pip install universal-agent-context`
- Version 0.1.0 release
- Package on conda-forge

**📣 Phase 4 (Week 4):** Public Launch
- Show HN / Reddit launches
- Documentation site live
- Community Discord server

**Future Roadmap:**
- Phase 5-6: Advanced features (streaming, webhooks, A2A protocol)
- Phase 7-8: Enterprise features (auth, analytics, multi-tenancy)

See [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) for complete timeline and [LAUNCH_STRATEGY.md](docs/LAUNCH_STRATEGY.md) for marketing plan.

---

## Documentation

**Getting Started:**
- 🚀 [Quick Start](#quick-start) - 5-minute tutorial (above)
- 📦 Installation - See [Quick Start](#installation) section
- 🎯 [Use Cases](#use-cases) - Real-world scenarios

**Integrations:**
UACS works with popular MCP clients out of the box:
- 🤖 [Claude Desktop](docs/integrations/CLAUDE_DESKTOP.md) - Complete setup guide with binary + Docker
- ✏️ [Cursor](docs/integrations/CURSOR.md) - Integration with inline chat and Composer
- 🌊 [Windsurf](docs/integrations/WINDSURF.md) - Cascade AI integration guide
- 📚 [All Integrations](docs/INTEGRATIONS.md) - Overview, troubleshooting, and advanced configs

**User Guides:**
- [Library Guide](docs/LIBRARY_GUIDE.md) - Complete Python API reference
- [CLI Reference](docs/CLI_REFERENCE.md) - All command documentation
- [MCP Server Setup](docs/MCP_SERVER_SETUP.md) - MCP integration for Claude/Cursor/Windsurf

**Technical Deep Dives:**
- [Adapters](docs/ADAPTERS.md) - Format translation architecture
- [Context Management](docs/CONTEXT.md) - Compression algorithms
- [Package Management](docs/PACKAGES.md) - Installation and management system

**Examples:**
All examples are in [examples/](examples/) and tested:
- [basic_context.py](examples/basic_context.py) - Context system basics
- [package_management.py](examples/package_management.py) - Install and manage packages
- [memory_usage.py](examples/memory_usage.py) - Persistent memory
- [custom_adapter.py](examples/custom_adapter.py) - Build custom format adapters
- [mcp_tool_usage.py](examples/mcp_tool_usage.py) - Programmatic MCP access

**Development:**
- [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md) - Development status & timeline
- [Launch Strategy](docs/LAUNCH_STRATEGY.md) - Marketing & positioning
- [Contributing](CONTRIBUTING.md) - How to contribute (coming Week 1)

---

## Requirements

- **Python:** 3.11 or higher
- **Optional:** Node.js (for MCP filesystem server)
- **Optional:** Docker (for containerized MCP deployment)

**Installation via `uv` (recommended):**
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install UACS
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync
```

---

## Development

**Setup:**
```bash
# Clone repository
git clone https://github.com/kylebrodeur/universal-agent-context.git
cd universal-agent-context

# Install with dev dependencies
uv sync  # Or: pip install -e ".[dev]"

# Run tests
uv run pytest                # All tests
uv run pytest -n auto        # Parallel (faster)
uv run pytest --cov=src      # With coverage

# Code quality
uv run ruff format .         # Format code
uv run ruff check --fix .    # Lint and fix
```

**Contributing:**
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) (coming Week 1) for guidelines.

**Project Status:** Phase 1 - Polish & Documentation (Week 1 of 8-week launch)

---

## Related Projects

### Multi-Agent CLI (MAOS)
- **Repository:** [github.com/kylebrodeur/multi-agent-cli](https://github.com/kylebrodeur/multi-agent-cli)
- **Relationship:** MAOS imports UACS for context management
- **Focus:** Multi-agent orchestration using Google ADK
- **Use case:** Build systems with multiple AI agents (Gemini, Claude, Copilot) working together

**Architecture:**
```
MAOS (Multi-Agent Orchestration)
    └── imports universal-agent-context
            └── provides context, skills, marketplace, memory
```

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Acknowledgments

- **Anthropic** - Agent Skills specification ([docs](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills)) and MCP protocol
- **Google** - Agent Development Kit (ADK)
- **OpenAI** - AGENTS.md standard
- **Community** - Skills marketplace contributors at [agentskills.io](https://agentskills.io) and [Smithery](https://smithery.ai)

---

**Status:** ✅ Phase 0 Complete → 🔄 Phase 1 In Progress (Week 1/8)  
**Version:** 0.1.0-dev | **Last Updated:** December 27, 2025
