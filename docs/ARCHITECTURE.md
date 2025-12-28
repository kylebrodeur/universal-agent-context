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
3. **Unified Marketplace** - Single API for skills + MCP server discovery
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
│   ADAPTERS    │  │   MARKETPLACE   │  │     CONTEXT       │
│ (Translation) │  │   (Discovery)   │  │   (Management)    │
├───────────────┤  ├─────────────────┤  ├───────────────────┤
│               │  │                 │  │                   │
│ • Skills      │  │ • Git repos     │  │ • Unified Context │
│ • AGENTS.md   │  │ • Skills        │  │ • Shared Memory   │
│ • Gemini      │  │ • MCP servers   │  │ • Compression     │
│ • .cursorrules│  │ • Caching       │  │ • Agent Context   │
│ • .clinerules │  │ • Install/list  │  │                   │
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
│  • ~/.uacs/cache/           - Marketplace cache            │
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

### 3. Marketplace (`uacs/marketplace/`)

**Purpose:** Unified discovery and installation for skills + MCP servers.

**Components:**
- `marketplace.py` - Unified marketplace interface
- `repositories.py` - Git repository management
- `packages.py` - Package metadata handling
- `cache.py` - Local caching layer (expires after 24h)

**Architecture:**
```python
class Marketplace:
    def search(query: str, type: str = "all") -> List[Package]:
        """Search across skills and MCP servers."""
        1. Check cache (24h expiry)
        2. Query Git repositories
        3. Filter by type (skills/mcp/all)
        4. Rank by relevance
        5. Return unified Package objects
    
    def install(package: Package) -> None:
        """Install skill or MCP server."""
        if package.type == "skills":
            → Install to .agent/skills/{name}/
        elif package.type == "mcp":
            → Install to .agent/mcpservers/
```

**Caching Strategy:**
- Cache location: `~/.uacs/cache/marketplace.json`
- Cache TTL: 24 hours
- Invalidation: Manual via `uacs marketplace refresh`

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

### Flow 2: Marketplace Discovery

```
User: uacs marketplace search "testing"
    │
    ├─→ Marketplace.search()
    │       │
    │       ├─→ Check cache (~/.uacs/cache/)
    │       │       │
    │       │       ├─→ Cache hit → Return cached results
    │       │       └─→ Cache miss → Continue
    │       │
    │       ├─→ Query Git repositories
    │       │       ├─→ Anthropic skills repo
    │       │       └─→ MCP servers repo
    │       │
    │       ├─→ Parse package metadata
    │       ├─→ Filter by type (skills/mcp)
    │       ├─→ Rank by relevance
    │       └─→ Cache results (24h TTL)
    │
    └─→ Display to user
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

# Marketplace
results = uacs.search("python testing")
uacs.install(results[0])

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

# Marketplace
uacs marketplace search "testing"
uacs marketplace install anthropic/skills-testing

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
- `search_marketplace` - Search skills/MCP
- `install_package` - Install from marketplace
- `get_compressed_context` - Build context with compression
- `list_installed` - Show installed packages
- `convert_format` - Format translation

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

### 4. Why Unified Marketplace?

**Decision:** Single API for both skills and MCP servers.

**Rationale:**
- ✅ Users don't care about implementation (SKILLS.md vs MCP)
- ✅ Both provide capabilities
- ✅ Single search interface
- ✅ Consistent installation

**Architecture:**
```python
class Package:
    name: str
    type: str  # "skills" | "mcp"
    source: str
    metadata: Dict[str, Any]

# Unified API
marketplace.search("testing")  # Returns both skills and MCP
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

### Marketplace Operations

- **Search (cached):** < 10ms
- **Search (cold):** 500-2000ms (network dependent)
- **Install skill:** 100-500ms (Git clone + copy)
- **Install MCP:** 200-1000ms (npx download)

### Memory Operations

- **Add memory:** < 5ms (append to JSON)
- **Search memories:** 10-50ms (depends on count)
- **Memory summarization:** 100-300ms (LLM call)

### Scaling Limits

- **Skills:** Tested up to 100 skills (< 50ms parse time)
- **Context entries:** 10,000+ entries (compression keeps prompt under limits)
- **Marketplace cache:** 1000+ packages (< 10ms search)
- **Memory entries:** 100,000+ entries (indexed search)

---

## Future Architecture Considerations

### Potential Enhancements (Phase 2+)

1. **Distributed Caching**
   - Redis support for shared cache across machines
   - Team-wide marketplace cache

2. **Vector Database Integration**
   - Semantic search over skills/context
   - Replace keyword search with embeddings

3. **Streaming Compression**
   - Incremental compression during conversation
   - Real-time token budget monitoring

4. **Plugin System**
   - User-defined adapters
   - Custom compression strategies
   - Marketplace source plugins

5. **Multi-Language Support**
   - TypeScript SDK
   - Go SDK
   - Rust SDK

---

## Related Documentation

- [Library Guide](LIBRARY_GUIDE.md) - Python API usage
- [CLI Reference](CLI_REFERENCE.md) - Command-line interface
- [Marketplace Guide](MARKETPLACE.md) - Discovery and installation
- [Context Management](CONTEXT.md) - Compression strategies
- [MCP Server Setup](MCP_SERVER_SETUP.md) - Claude Desktop integration

