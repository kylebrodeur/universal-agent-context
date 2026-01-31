# UACS Architecture

**Universal Agent Context System - System Design & Architecture**

---

## Table of Contents

- [High-Level Overview](#high-level-overview)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Integration Points](#integration-points)
- [Design Decisions](#design-decisions)
- [Technology Stack](#technology-stack)

---

## High-Level Overview

UACS is middleware for AI agent context management. It sits between your agent application and AI models, providing:

1. **Universal Format Translation** - One source of truth → multiple formats
2. **Intelligent Compression** - 70%+ token savings via deduplication, summarization, and quality scoring
3. **Package Management** - Simple installation for skills + MCP servers
4. **Persistent Memory** - Project-scoped and global memory storage
5. **Multiple Integration Points** - Python API, CLI, and MCP server

### System Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                                │
├────────────────┬──────────────────────┬───────────────────────────────┤
│  Python API    │     CLI Tool         │      MCP Server               │
│                │                      │                               │
│  from uacs     │  $ uacs skills list  │  Server: uacs serve           │
│  import UACS   │  $ uacs marketplace  │  Client: Claude Desktop       │
│                │    search "testing"  │          Cursor, Cline        │
└────────┬───────┴──────────┬───────────┴──────────┬────────────────────┘
         │                  │                      │
         └──────────────────┴──────────────────────┘
                            │
         ┌──────────────────▼──────────────────────┐
         │          UNIFIED API (uacs/api.py)      │
         │   - High-level operations               │
         │   - Orchestrates components             │
         │   - Error handling & validation         │
         └──────────────────┬──────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───▼───────────┐  ┌────────▼────────┐  ┌──────────▼────────┐
│   ADAPTERS    │  │    PACKAGES     │  │     CONTEXT       │
│ (Translation) │  │  (Management)   │  │   (Management)    │
├───────────────┤  ├─────────────────┤  ├───────────────────┤
│               │  │                 │  │                   │
│ • Skills      │  │ • Git clone     │  │ • Unified Context │
│ • AGENTS.md   │  │ • Local copy    │  │ • Shared Memory   │
│ • Gemini      │  │ • Validation    │  │ • Compression     │
│ • .cursorrules│  │ • Install/list  │  │ • Agent Context   │
│ • .clinerules │  │ • Update/remove │  │                   │
│               │  │                 │  │                   │
└───────────────┘  └─────────────────┘  └───────────────────┘
         │                  │                      │
         │                  │                      │
┌────────▼──────────────────▼──────────────────────▼────────┐
│                    STORAGE LAYER                           │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  • .agent/skills/           - Installed skills             │
│  • .agent/mcpservers/       - MCP server configs           │
│  • .state/context/          - Runtime context              │
│  • .state/memory/           - Project memory               │
│  • ~/.uacs/memory/          - Global memory                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Adapters (`uacs/adapters/`)

**Purpose:** Bidirectional format translation for agent instructions.

**Components:**
- `base.py` - Abstract `BaseFormatAdapter` interface
- `skills_adapter.py` - SKILLS.md format (Anthropic standard)
- `agents_md_adapter.py` - AGENTS.md format (generic project context)
- `gemini_adapter.py` - GEMINI.md format (Google Gemini)
- `cursorrules_adapter.py` - .cursorrules format (Cursor IDE)
- `clinerules_adapter.py` - .clinerules format (Cline extension)

**Key Features:**
- Registry pattern for dynamic adapter discovery
- Standardized parse → system prompt pipeline
- File pattern matching for auto-detection
- Metadata extraction for each format

**Example Flow:**
```python
# 1. Load SKILLS.md
skills_adapter = SkillsAdapter("SKILLS.md")
parsed = skills_adapter.parse()

# 2. Convert to system prompt
system_prompt = skills_adapter.to_system_prompt()

# 3. Convert to different format
cursor_adapter = CursorRulesAdapter()
cursor_content = cursor_adapter.from_parsed(parsed)
cursor_adapter.save(".cursorrules")
```

### 2. Context Management (`uacs/context/`)

**Purpose:** Runtime context building with intelligent compression.

**Components:**

#### `unified_context.py` - UnifiedContextAdapter
- Combines AGENTS.md + SKILLS.md + conversation history
- Builds agent-specific prompts
- Token counting and budget management
- Query-based filtering

**API:**
```python
adapter = UnifiedContextAdapter()
prompt_data = adapter.build_agent_prompt(
    user_query="Review auth.py",
    agent_name="claude",
    max_context_tokens=8000
)
# → Returns: system prompt + token count + metadata
```

#### `shared_context.py` - SharedContextManager
- Multi-agent conversation history
- Compression strategies:
  1. **Deduplication** - Hash-based duplicate removal
  2. **Summarization** - LLM-based context compression
  3. **Quality scoring** - Keep high-value entries
  4. **Topic filtering** - Semantic relevance

**Compression Algorithm:**
```python
def get_compressed_context(max_tokens: int) -> str:
    1. Deduplicate entries by content hash
    2. Score entries by quality (recency, topic match)
    3. Keep high-quality entries
    4. Summarize old low-quality entries
    5. Return compressed context under token budget
```

**Token Savings:**
- Deduplication: 20-30%
- Summarization: 50-70%
- Combined: 70%+ typical

#### `agent_context.py` - AgentContextBuilder
- Per-agent context filtering
- Instruction injection
- Skill discovery and formatting

### 3. Package Manager (`uacs/packages/`)

**Purpose:** Simple installation and management for skills + MCP servers.

**Components:**
- `manager.py` - Package manager interface
- `installer.py` - Git clone and local copy operations
- `validator.py` - Package structure validation
- `metadata.py` - Installation tracking

**Architecture:**
```python
class PackageManager:
    def install(source: str, type: str = "auto") -> None:
        """Install from GitHub, Git URL, or local path."""
        1. Detect source type (GitHub/Git/local)
        2. Clone or copy package content
        3. Validate package structure (for skills)
        4. Place in appropriate directory
        5. Update metadata (.installed.json)

    def list(type: str = "all") -> List[Package]:
        """List installed packages."""
        → Read from .agent/skills/ and .agent/mcpservers/

    def remove(name: str) -> None:
        """Uninstall package."""
        → Remove from .agent/skills/ or .agent/mcpservers/
```

**Installation tracking:**
- Metadata location: `.agent/skills/.installed.json`
- Tracks: source, install date, version, install method

### 4. Memory (`uacs/memory/`)

**Purpose:** Persistent long-term storage across sessions.

**Scopes:**
- **Project Memory** - `.state/memory/` (workspace-specific)
- **Global Memory** - `~/.uacs/memory/` (user-wide)

**Components:**
- `simple_memory.py` - Key-value store with tags
- `retrieval.py` - Semantic search over memories
- `compression.py` - Memory summarization

**API:**
```python
store = SimpleMemoryStore(scope="project")
store.add_memory(
    content="User prefers TypeScript",
    tags=["preference", "language"]
)

# Retrieve relevant memories
results = store.search_memories(
    query="What language does user prefer?",
    limit=5
)
```

### 5. MCP Server (`uacs/protocols/mcp/`)

**Purpose:** Expose UACS capabilities to Claude Desktop, Cursor, Cline.

**Architecture:**
- Server: `uacs serve` (stdio-based MCP server)
- Client: Claude Desktop connects via MCP protocol
- Tools exposed:
  - `search_marketplace` - Find skills/MCP servers
  - `install_package` - Install from marketplace
  - `get_context` - Build compressed context
  - `list_skills` - Show installed skills
  - `convert_format` - Translate between formats

**Integration:**
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "uacs": {
      "command": "uacs",
      "args": ["serve"]
    }
  }
}
```

---

## Data Flow

### Flow 1: Building Agent Context

```
User Request
    │
    ├─→ UnifiedContextAdapter.build_agent_prompt()
    │       │
    │       ├─→ Load AGENTS.md (AgentsMDAdapter)
    │       ├─→ Load SKILLS.md (SkillsAdapter)
    │       ├─→ Get conversation history (SharedContextManager)
    │       │       └─→ Apply compression (70%+ reduction)
    │       │
    │       └─→ Combine + format
    │               │
    │               └─→ Token count (tiktoken)
    │
    └─→ Return: {system_prompt, token_count, metadata}
```

### Flow 2: Package Installation

```
User: uacs packages install anthropic/skills-testing
    │
    ├─→ PackageManager.install()
    │       │
    │       ├─→ Detect source type (GitHub)
    │       │
    │       ├─→ Clone from GitHub
    │       │       └─→ git clone https://github.com/anthropic/skills-testing
    │       │
    │       ├─→ Validate package structure
    │       │       └─→ Check SKILL.md, frontmatter, directory structure
    │       │
    │       ├─→ Copy to .agent/skills/testing/
    │       │
    │       └─→ Update metadata (.installed.json)
    │
    └─→ Display success message
```

### Flow 3: Format Translation

```
Source File (SKILLS.md)
    │
    ├─→ SkillsAdapter.parse()
    │       └─→ Extract skills, metadata
    │
    ├─→ Convert to target format
    │       ├─→ CursorRulesAdapter.from_parsed()
    │       └─→ Generate .cursorrules content
    │
    └─→ Save to file
```

---

## Integration Points

### 1. Python API

**Target Users:** Developers building agent applications

**Entry Point:** `uacs.api.UACS`

```python
from pathlib import Path
from uacs import UACS

uacs = UACS(Path.cwd())

# Package management
uacs.packages.install("anthropic/skills-testing")  # GitHub
uacs.packages.install("/path/to/local/skill")      # Local path
uacs.packages.list()

# Context
context = uacs.build_context(
    query="Review code",
    max_tokens=8000
)

# Conversion
uacs.convert_format(
    source="SKILLS.md",
    target=".cursorrules"
)
```

**Use Cases:**
- Custom multi-agent orchestrators (like MAOS)
- IDE extensions
- CI/CD pipelines
- Automated agents

### 2. CLI Tool

**Target Users:** Developers using terminal workflows

**Entry Point:** `uacs` command (installed via pip/uv)

```bash
# Skills management
uacs skills list
uacs skills convert --to cursorrules

# Package management
uacs packages install anthropic/skills-testing
uacs packages list
uacs packages remove testing

# Context
uacs context stats
uacs context build --agent claude --max-tokens 8000

# Memory
uacs memory add "User prefers TypeScript" --tags preference
uacs memory search "language preference"
```

**Use Cases:**
- Local development
- Scripting and automation
- Project initialization
- Quick format conversions

### 3. MCP Server

**Target Users:** Users of Claude Desktop, Cursor, Cline

**Entry Point:** `uacs serve` (MCP stdio server)

**Setup:**
```json
// ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "uacs": {
      "command": "uacs",
      "args": ["serve"]
    }
  }
}
```

**Exposed Tools:**
- `install_package` - Install from GitHub, Git, or local
- `list_packages` - Show installed packages
- `get_compressed_context` - Build context with compression
- `convert_format` - Format translation
- `manage_memory` - Memory operations

**Use Cases:**
- Claude Desktop power users
- Cursor IDE integration
- Cline extension users
- Windsurf integration

---

## Design Decisions

### 1. Why Middleware, Not a Framework?

**Decision:** UACS is middleware, not an agent framework.

**Rationale:**
- ✅ Works with existing tools (Claude, Cursor, Gemini)
- ✅ Doesn't replace your workflow
- ✅ Enhances what you already use
- ✅ Can be adopted incrementally

**Alternative Considered:** Building a complete agent framework like LangChain or CrewAI.

**Why Rejected:** Too opinionated. Users already have tools they like. UACS makes those tools better without forcing a new workflow.

### 2. Why Adapter Pattern for Formats?

**Decision:** Use adapter pattern with registry for format translation.

**Rationale:**
- ✅ Easy to add new formats (just implement BaseFormatAdapter)
- ✅ Decoupled from core logic
- ✅ Auto-detection via file patterns
- ✅ Bidirectional translation

**Implementation:**
```python
class BaseFormatAdapter(ABC):
    FORMAT_NAME: str
    SUPPORTED_FILES: List[str]
    
    @abstractmethod
    def parse(self) -> ParsedContent:
        pass
    
    @abstractmethod
    def to_system_prompt(self) -> str:
        pass

@FormatAdapterRegistry.register
class SkillsAdapter(BaseFormatAdapter):
    FORMAT_NAME = "skills"
    SUPPORTED_FILES = ["SKILLS.md"]
```

### 3. Why 70% Compression Target?

**Decision:** Target 70%+ token compression via multiple strategies.

**Rationale:**
- 70% = 10,000 tokens → 3,000 tokens
- Cost savings: $0.10/call → $0.03/call
- Strategies:
  - Deduplication (20-30% savings)
  - Summarization (50-70% savings)
  - Quality filtering (preserve important content)

**Quality Safeguards:**
- Keep recent entries (last 5)
- Preserve high-quality entries (quality score > 0.8)
- Only summarize old, low-value content

### 4. Why Simple Package Manager?

**Decision:** Git-based installation without search/discovery.

**Rationale:**
- ✅ Simple and reliable (no complex indexing)
- ✅ Works like GitHub CLI extensions
- ✅ Users already know sources (GitHub, Git URLs)
- ✅ Consistent installation from any source

**Architecture:**
```python
class Package:
    name: str
    type: str  # "skill" | "mcp"
    source: str
    install_method: str  # "github" | "git" | "local"
    metadata: Dict[str, Any]

# Installation from any source
packages.install("owner/repo")           # GitHub
packages.install("https://...")          # Git URL
packages.install("/path/to/package")     # Local
```

### 5. Why Project + Global Memory?

**Decision:** Two-tier memory system (project + global).

**Rationale:**
- **Project Memory** - `.state/memory/`
  - Workspace-specific facts
  - Architecture decisions
  - Temporary preferences
- **Global Memory** - `~/.uacs/memory/`
  - User preferences (language, style)
  - Reusable patterns
  - Cross-project knowledge

**Use Case:**
- Project: "This repo uses Pydantic for validation"
- Global: "User prefers TypeScript over JavaScript"

### 6. Why Three Integration Points?

**Decision:** Provide Python API, CLI, and MCP server.

**Rationale:**
- **Python API** - For developers building agents
- **CLI** - For local development and scripting
- **MCP Server** - For Claude Desktop, Cursor, Cline

All three use the same core (`uacs/api.py`), ensuring consistency.

---

## Technology Stack

### Core Dependencies

```toml
[dependencies]
python = "^3.11"            # Modern Python with type hints
pydantic = "^2.0"           # Data validation
httpx = "^0.27"             # Async HTTP client (marketplace)
anyio = "^4.0"              # Async abstraction
tiktoken = "^0.7"           # Token counting (OpenAI)
zstandard = "^0.23"         # Compression (shared context)
gitpython = "^3.1"          # Git operations (marketplace)
mcp = "^1.0"                # Model Context Protocol (server)
typer = "^0.9"              # CLI framework
rich = "^13.0"              # Terminal UI

[dev-dependencies]
pytest = "^8.0"             # Testing
pytest-asyncio = "^0.23"    # Async tests
pytest-cov = "^4.1"         # Coverage
ruff = "^0.5"               # Linting + formatting
mypy = "^1.11"              # Type checking
bandit = "^1.7"             # Security scanning
```

### Why These Choices?

**Pydantic:** Type-safe data validation, auto-documentation
**httpx:** Modern async HTTP, needed for marketplace
**tiktoken:** Accurate token counting for OpenAI-compatible models
**zstandard:** Fast compression for context storage
**typer + rich:** Beautiful CLI with minimal code
**pytest:** Industry-standard testing

---

## Performance Characteristics

### Context Building

- **AGENTS.md parsing:** < 10ms
- **SKILLS.md parsing:** < 20ms (up to 50 skills)
- **Compression (10K tokens → 3K):** 50-100ms
- **Total context build time:** < 150ms

### Package Operations

- **Install from GitHub:** 500-2000ms (Git clone + validation)
- **Install from local:** 50-100ms (copy + validation)
- **List packages:** < 10ms (read metadata)
- **Validate package:** 20-50ms (structure check)

### Memory Operations

- **Add memory:** < 5ms (append to JSON)
- **Search memories:** 10-50ms (depends on count)
- **Memory summarization:** 100-300ms (LLM call)

### Scaling Limits

- **Skills:** Tested up to 100 skills (< 50ms parse time)
- **Context entries:** 10,000+ entries (compression keeps prompt under limits)
- **Installed packages:** 1000+ packages (< 10ms list)
- **Memory entries:** 100,000+ entries (indexed search)

---

## Future Architecture Considerations

### Potential Enhancements (Phase 2+)

1. **Package Discovery**
   - Optional package index/registry
   - Search functionality for known packages
   - Community package recommendations

2. **Vector Database Integration**
   - Semantic search over skills/context
   - Better context retrieval

3. **Streaming Compression**
   - Incremental compression during conversation
   - Real-time token budget monitoring

4. **Plugin System**
   - User-defined adapters
   - Custom compression strategies
   - Custom package sources

5. **Multi-Language Support**
   - TypeScript SDK
   - Go SDK
   - Rust SDK

---

## Related Documentation

- [Library Guide](LIBRARY_GUIDE.md) - Python API usage
- [CLI Reference](CLI_REFERENCE.md) - Command-line interface
- [Package Management](PACKAGES.md) - Installation and management
- [Context Management](CONTEXT.md) - Compression strategies
- [MCP Server Setup](MCP_SERVER_SETUP.md) - Claude Desktop integration

