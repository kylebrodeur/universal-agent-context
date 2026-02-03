# Universal Agent Context System (UACS)

**Version 0.3.0** - Semantic Conversations & Knowledge Extraction

[![PyPI](https://img.shields.io/badge/pypi-v0.3.0-blue)](https://pypi.org/project/universal-agent-context/)
[![Tests](https://img.shields.io/badge/tests-190%2B%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

> **TL;DR:** Universal context middleware for AI agents with semantic conversation tracking and knowledge extraction. One source of truth → 5+ formats. Perfect recall with smart search. Package management for skills + MCP. Works with Claude, Cursor, Windsurf, Cline, or your own Python code.

---

## Why UACS?

Building AI agent systems today means juggling multiple formats, wasting tokens, and losing context between sessions. **UACS solves this.**

**In 30 seconds:**
- 🔄 Write once → Deploy to Claude, Cursor, Cline, Gemini, Copilot
- 🧠 **NEW v0.3.0:** Semantic API for structured conversations and knowledge
- 🔍 **NEW v0.3.0:** Natural language search across all context
- 📝 **NEW v0.3.0:** Automatic decision and convention extraction
- 🎯 **NEW v0.3.0:** Claude Code hooks for real-time capture
- 🗜️ Never lose context with automatic deduplication (15% immediate savings)
- 🛡️ Proactive compaction prevention for Claude Code (95%+ success rate)
- 🤖 Local LLM tagging via transformers (zero API cost, better quality)
- 📊 LangSmith-style trace visualization (debug any session)
- 📦 Package management for skills + MCP servers (GitHub, Git, local)
- ⚡ Python API + CLI + MCP server = works everywhere

**What makes UACS different:** It's **middleware**, not another agent tool. Claude Desktop gets better when you add UACS. So does Cursor. So does your custom Python agent.

---

## What's New in v0.3.0

### Semantic API

UACS v0.3.0 introduces a powerful semantic API for structured conversation tracking and knowledge extraction:

**Structured Conversations:**
- Track user messages, assistant responses, and tool executions
- Automatic embedding generation for semantic search
- Session-based organization with turn tracking

**Knowledge Extraction:**
- Capture architectural decisions with rationale
- Extract project conventions and patterns
- Store cross-session learnings
- Track code artifacts and their purpose

**Semantic Search:**
- Natural language queries across all stored context
- "How did we implement authentication?"
- Type-specific filtering (messages, decisions, conventions)
- Relevance-ranked results

**Claude Code Integration:**
- Automatic capture via hooks (UserPromptSubmit, PostToolUse, SessionEnd)
- Real-time context storage (crash-resistant)
- Decision and convention extraction from conversations

See [Migration Guide](docs/MIGRATION.md) to upgrade from v0.2.x.

---

## Installation

Choose the installation method that best fits your workflow:

| Method | Best For | Prerequisite |
| :--- | :--- | :--- |
| **Python (pip)** | Developers integrating UACS into Python projects | Python 3.11+ |
| **uvx** | Quick, temporary usage without installing dependencies | `uv` installed |
| **[Binary](docs/guides/MCP_SERVER_BINARY.md)** | Standalone usage, no Python environment needed | None |
| **[Docker](docs/guides/MCP_SERVER_DOCKER.md)** | Server deployments, team environments | Docker |

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

# Optional: For local LLM tagging (better topic extraction)
pip install transformers torch  # ~2GB download on first use
```

### Claude Code Plugin

**v0.3.0: Semantic capture + proactive compaction prevention + real-time storage:**

```bash
# Install semantic plugin
cp .claude-plugin/plugin-semantic.json ~/.claude/plugin.json
cp .claude-plugin/hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py

# Optional: Install transformers for better topic extraction
pip install transformers torch
```

**v0.3.0 Features:**
- 📝 **Semantic Capture**: Automatically captures user messages, tool uses, decisions, and conventions
- 🔍 **Natural Language Search**: Query stored context with "how did we implement auth?"
- 🧠 **Knowledge Extraction**: Identifies decisions and conventions from conversations
- 🎯 **Structured Storage**: All data stored with embeddings for semantic search

**v0.2.0 Features:**
- 🛡️ **Compaction Prevention**: Monitors context, compresses at 50% (before Claude's 75% threshold) - 95%+ success
- 🤖 **Local LLM Tagging**: Uses TinyLlama (1.1B) for topic extraction - zero API cost
- 💾 **Crash-Resistant**: Real-time storage via PostToolUse hook
- 🔄 **Auto-Context**: Injects previous context on session resume

**See:** [Hooks Guide](.claude-plugin/HOOKS_GUIDE.md) | [Migration Guide](docs/MIGRATION.md) | [API Reference](docs/API_REFERENCE.md)

---

## CLI Demo

```bash
# Package management
$ uacs packages install anthropic/skills-testing
✅ Installed to .agent/skills/testing/

# Context compression
$ uacs context stats
📊 45,234 tokens → 38,449 (15% reduction)
💰 Savings: $0.07/call

# Memory search
$ uacs memory search "testing"
🔍 Found 3 relevant memories (scores: 0.92, 0.87, 0.81)
```

**See also:** [CLI Reference](docs/CLI_REFERENCE.md) | [Examples](examples/)

---

## Web UI (NEW v0.3.0)

Modern Next.js web application for exploring UACS data with semantic search and knowledge browsing. Bundled into a single command:

```bash
# Single command - bundled UI!
uv run uacs web

# Or with custom options:
uv run uacs web --port 8081 --host localhost

# Open browser
open http://localhost:8081
```

💡 **Bundled Architecture:** The Next.js frontend (static export) is served directly from FastAPI - no separate frontend server needed!

**Features:**
- 🔍 **Semantic Search** - Natural language search across all content with type filters
- 📅 **Timeline View** - Chronological session events with user/assistant/tool interactions
- 📚 **Knowledge Browser** - Explore decisions, conventions, learnings, and artifacts
- 🔬 **Session Traces** - Expandable session cards with full execution timelines
- 🎨 **Modern UI** - Built with Next.js 15, TypeScript, and shadcn/ui
- 🌙 **Dark Mode** - System preference support

**See:** [Web UI Documentation](uacs-web-ui/README.md) | [Implementation Complete](./.github/NEXT_JS_WEB_UI_COMPLETE.md)

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
> Your existing tools get package management, format conversion, perfect recall with deduplication, and persistent memory - without changing how you work.

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

**With UACS (v0.1.0):**
```python
context = uacs.get_compressed_context(max_tokens=8500)  # Smart retrieval + deduplication
# 15% deduplication savings + perfect recall
# Cost per call: $0.085
# 100 calls/day: $8.50/day = $255/month
# Savings: $45/month (15%)
# Plus: 2 hours/week saved (no re-explaining after context resets)
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

UACS is **middleware**, not another agent tool. It provides format translation, context compression, package management, persistent memory, and MCP server integration in one package - the only solution offering this complete feature set.

---

## Quick Start

### Basic Usage (v0.3.0 Semantic API)

```python
from uacs import UACS
from pathlib import Path

# Initialize
uacs = UACS(project_path=Path("."))

# Track conversation
user_msg = uacs.add_user_message(
    content="Help me implement JWT authentication",
    turn=1,
    session_id="session_001",
    topics=["security", "feature"]
)

assistant_msg = uacs.add_assistant_message(
    content="I'll help you implement JWT. First, let's...",
    turn=1,
    session_id="session_001",
    tokens_in=42,
    tokens_out=156
)

# Capture decisions
decision = uacs.add_decision(
    question="Which auth method should we use?",
    decision="JWT tokens",
    rationale="Stateless, scalable, works with microservices",
    session_id="session_001",
    alternatives=["Session-based (doesn't scale)", "OAuth2 (overkill)"]
)

# Search semantically
results = uacs.search("how did we implement authentication?", limit=10)
for result in results:
    print(f"[{result.metadata['type']}] {result.text[:100]}...")
    print(f"Relevance: {result.similarity:.2f}\n")
```

**See also:** [Full Quickstart Guide](QUICKSTART.md) | [API Reference](docs/API_REFERENCE.md) | [Examples](examples/)

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
    max_tokens=4000  # Smart deduplication + topic filtering
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

**The Solution:** Smart context management with perfect recall.

**Current Implementation (v0.1.0):**
1. **Deduplication** - Hash-based, automatic (15% savings)
2. **Quality Filtering** - Remove noise, keep signal
3. **Topic-Based Retrieval** - Focus on relevant context
4. **Exact Storage** - 100% fidelity, zero information loss

**Coming in v0.2.0:**
5. **LLM Summarization** - Claude Haiku for intelligent compression
6. **Vector Embeddings** - Semantic similarity search
7. **Knowledge Graph** - Context relationship traversal
8. **Target: 70%+ compression** with zero information loss

**Real-world Impact (v0.1.0):**
```python
# Deduplication savings:
- Original context: 10,000 tokens
- After deduplication: 8,500 tokens (15% savings)
- Cost per call: $0.085 (vs $0.10)
- 100 calls/day: $8.50/day vs $10/day
- Monthly savings: $45 (15%)

# Plus time savings:
- Context never lost = no re-explaining
- Save ~2 hours/week for active developers
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

## API Reference (v0.3.0)

### Conversation Methods

Track structured conversation elements with automatic embedding generation:

- **`add_user_message(content, turn, session_id, topics)`** - Track user prompts
- **`add_assistant_message(content, turn, session_id, tokens_in, tokens_out, model)`** - Track assistant responses
- **`add_tool_use(tool_name, tool_input, tool_response, turn, session_id, latency_ms, success)`** - Track tool executions

### Knowledge Methods

Capture architectural knowledge with semantic indexing:

- **`add_decision(question, decision, rationale, session_id, alternatives, decided_by, topics)`** - Capture architectural decisions
- **`add_convention(content, topics, source_session, confidence)`** - Capture project conventions and patterns
- **`add_learning(pattern, learned_from, category, confidence)`** - Capture cross-session learnings
- **`add_artifact(type, path, description, created_in_session, topics)`** - Track code artifacts

### Search Method

Natural language semantic search across all stored context:

- **`search(query, types, min_confidence, session_id, limit)`** - Search with natural language queries
  - Returns ranked results by relevance
  - Filter by type (user_message, assistant_message, tool_use, convention, decision, learning, artifact)
  - Filter by session or confidence threshold

### Statistics Methods

Access system statistics and capabilities:

- **`get_stats()`** - Get comprehensive UACS statistics (entries, tokens, compression, semantic data)
- **`get_capabilities(agent)`** - Get available capabilities for an agent
- **`get_token_stats()`** - Get token usage and compression statistics

**Complete documentation:** [API Reference](docs/API_REFERENCE.md)

---

## Migrating to v0.3.0

UACS v0.3.0 is **backward compatible**. Existing code using `add_to_context()` will continue to work but is deprecated.

### Quick Migration

**Old API (deprecated):**
```python
uacs.add_to_context(
    key="claude",
    content="Implemented feature",
    topics=["dev"]
)
```

**New Semantic API (recommended):**
```python
uacs.add_convention(
    content="Implemented feature",
    topics=["dev"],
    confidence=1.0
)
```

### Migration Benefits

- ✅ **Better Search:** Natural language queries instead of topic-only filtering
- ✅ **Structured Data:** Explicit types (decisions, conventions, learnings) instead of generic context
- ✅ **Automatic Embeddings:** Semantic indexing for all entries
- ✅ **Hooks Integration:** Seamless Claude Code integration with automatic capture
- ✅ **Future-Proof:** Ready for v0.5.0+ (add_to_context removed in v0.5.0)

**Complete migration guide:** [Migration Guide](docs/MIGRATION.md)

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
- 📚 [All Integrations](docs/features/INTEGRATIONS.md) - Overview, troubleshooting, and advanced configs

**User Guides:**
- [Migration Guide](docs/MIGRATION.md) - Upgrade from v0.2.x to v0.3.0 semantic API
- [API Reference](docs/API_REFERENCE.md) - Complete v0.3.0 API documentation with examples
- [Hooks Guide](.claude-plugin/HOOKS_GUIDE.md) - Claude Code hooks for automatic capture
- [Library Guide](docs/LIBRARY_GUIDE.md) - Complete Python API reference
- [CLI Reference](docs/CLI_REFERENCE.md) - All command documentation
- [MCP Server Setup](docs/guides/MCP_SERVER_SETUP.md) - MCP integration for Claude/Cursor/Windsurf

**Technical Deep Dives:**
- [Adapters](docs/features/ADAPTERS.md) - Format translation architecture
- [Context Management](docs/features/CONTEXT.md) - Compression algorithms
- [Package Management](docs/features/PACKAGES.md) - Installation and management system

**Examples:**
All examples use v0.3.0 semantic API and take ~15 minutes total:
- [01_semantic_basics.py](examples/01_semantic_basics.py) - Core API (5 min)
- [02_claude_code_integration.py](examples/02_claude_code_integration.py) - Hooks & auto-capture (5 min)
- [03_web_ui.py](examples/03_web_ui.py) - Web UI visualization (3 min)
- [04_search_and_knowledge.py](examples/04_search_and_knowledge.py) - Advanced patterns (2 min)
- [See examples/README.md](examples/README.md) - Full guide with learning paths

**Development:**
- [Contributing](CONTRIBUTING.md) - How to contribute

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
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Built on Standards

UACS implements and extends these community standards:

**[Agent Skills](https://agentskills.io)** - Universal skill format by Anthropic
UACS supports the Agent Skills specification for skill packaging and discovery.

**[AGENTS.md](https://agents.md)** - Open format for agent context
UACS reads and writes AGENTS.md format, enabling format translation across tools.

---

## Related Projects

### Complementary Tools

**[claude-code-transcripts](https://github.com/simonw/claude-code-transcripts)** - Publish sessions to HTML/Gist
Export and share your Claude Code sessions as beautiful web pages. Pairs with UACS trace visualization.

**[GrepAI](https://github.com/yoanbernabeu/grepai)** - Semantic code search (100% local)
Natural language code search as MCP server. Use together: GrepAI finds code, UACS compresses and manages it as context.

### Content Sources

**[OpenAI Skills](https://github.com/openai/skills)** - Curated skills catalog
Official Codex skills collection. Install via UACS: `uacs packages install openai/skills-[name]`

### Alternative Approaches

**[memcord](https://github.com/ukkit/memcord)** - Privacy-first MCP memory server
Conversation history with summarization. Alternative to UACS's trace visualization - different storage model (MCP server vs JSONL) and different focus (summarization vs compression analytics).

**[claude-mem](https://github.com/thedotmack/claude-mem)** - Session memory with web UI
Similar to UACS trace visualization but with SQLite + Chroma backend. UACS offers broader infrastructure (compaction prevention, format translation, MCP server, packages) while claude-mem provides dedicated memory browsing interface.

**[openskills](https://github.com/numman-ali/openskills)** - Universal skills loader (Node.js)
Progressive disclosure approach to skill loading. Alternative to UACS's compression strategy, Node.js vs Python.

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Acknowledgments

- **Anthropic** - Agent Skills specification ([docs](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills)) and MCP protocol
- **Google** - Agent Development Kit (ADK)
- **OpenAI** - AGENTS.md standard
- **Community** - Skills contributors at [agentskills.io](https://agentskills.io) and [Smithery](https://smithery.ai)

---

**Version:** 0.3.0 | **License:** MIT
