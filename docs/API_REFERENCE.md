# UACS v0.3.0 API Reference

Complete API documentation for Universal Agent Context System v0.3.0.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [UACS Class](#uacs-class)
- [Conversation Methods](#conversation-methods)
  - [add_user_message()](#add_user_message)
  - [add_assistant_message()](#add_assistant_message)
  - [add_tool_use()](#add_tool_use)
- [Knowledge Methods](#knowledge-methods)
  - [add_decision()](#add_decision)
  - [add_convention()](#add_convention)
  - [add_learning()](#add_learning)
  - [add_artifact()](#add_artifact)
- [Search Method](#search-method)
  - [search()](#search)
- [Statistics Methods](#statistics-methods)
  - [get_stats()](#get_stats)
  - [get_capabilities()](#get_capabilities)
  - [get_token_stats()](#get_token_stats)
- [Legacy Methods](#legacy-methods)
- [Data Models](#data-models)

---

## Overview

UACS v0.3.0 provides a semantic API for structured conversation tracking and knowledge extraction. All methods return Pydantic models and automatically generate embeddings for semantic search.

### Key Features

- **Structured Conversations**: Track user messages, assistant responses, and tool executions
- **Knowledge Extraction**: Capture decisions, conventions, learnings, and artifacts
- **Semantic Search**: Natural language queries across all stored context
- **Automatic Embeddings**: All data indexed with FAISS for fast retrieval
- **Type Safety**: Pydantic models with validation
- **Claude Code Hooks**: Automatic capture during development sessions

---

## Installation

```bash
# Option 1: From source
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
uv sync

# Option 2: PyPI (coming soon)
pip install universal-agent-context
```

### Basic Setup

```python
from uacs import UACS
from pathlib import Path

# Initialize with project path
uacs = UACS(project_path=Path("."))

# Storage locations:
# - Conversations: .state/conversations/
# - Knowledge: .state/knowledge/
# - Embeddings: .state/embeddings/
```

---

## UACS Class

The main entry point for all UACS operations.

### Constructor

```python
UACS(project_path: Path)
```

**Parameters:**
- `project_path` (Path): Path to the project root directory

**Returns:**
- UACS instance with initialized managers (conversation, knowledge, embedding)

**Example:**

```python
from uacs import UACS
from pathlib import Path

# Initialize for current project
uacs = UACS(project_path=Path("."))

# Initialize for specific project
uacs = UACS(project_path=Path("/path/to/project"))
```

---

## Conversation Methods

Track structured conversation elements with automatic embedding generation.

### add_user_message()

Add a user message to conversation history.

```python
add_user_message(
    content: str,
    turn: int,
    session_id: str,
    topics: Optional[List[str]] = None
) -> UserMessage
```

**Parameters:**
- `content` (str): User prompt text (required, min length 1)
- `turn` (int): Turn number in conversation (required, 1-indexed)
- `session_id` (str): Session identifier (required, min length 1)
- `topics` (Optional[List[str]]): Topic tags for categorization

**Returns:**
- `UserMessage`: Created user message with timestamp

**Example:**

```python
user_msg = uacs.add_user_message(
    content="Help me implement JWT authentication",
    turn=1,
    session_id="session_001",
    topics=["security", "feature"]
)

print(f"Message ID: {user_msg.session_id}")
print(f"Topics: {user_msg.topics}")
print(f"Timestamp: {user_msg.timestamp}")
```

**Storage:**
- Location: `.state/conversations/conversation_*.json`
- Indexed: Yes (automatic embedding generation)
- Searchable: Yes (via `search()` method)

---

### add_assistant_message()

Add an assistant response to conversation history.

```python
add_assistant_message(
    content: str,
    turn: int,
    session_id: str,
    tokens_in: Optional[int] = None,
    tokens_out: Optional[int] = None,
    model: Optional[str] = None
) -> AssistantMessage
```

**Parameters:**
- `content` (str): Assistant response text (required, min length 1)
- `turn` (int): Turn number in conversation (required, 1-indexed)
- `session_id` (str): Session identifier (required, min length 1)
- `tokens_in` (Optional[int]): Input token count (prompt tokens)
- `tokens_out` (Optional[int]): Output token count (response tokens)
- `model` (Optional[str]): Model identifier (e.g., "claude-sonnet-4")

**Returns:**
- `AssistantMessage`: Created assistant message with timestamp and token tracking

**Example:**

```python
assistant_msg = uacs.add_assistant_message(
    content="I'll help you implement JWT authentication. First, let's...",
    turn=1,
    session_id="session_001",
    tokens_in=42,
    tokens_out=156,
    model="claude-sonnet-4"
)

print(f"Response: {assistant_msg.content[:50]}...")
print(f"Token usage: {assistant_msg.tokens_in} in, {assistant_msg.tokens_out} out")
```

**Token Tracking:**

Token counts are optional but recommended for cost tracking and analytics.

```python
# Access token statistics later
stats = uacs.get_stats()
print(f"Total tokens: {stats['semantic']['conversations']['total_tokens']}")
```

---

### add_tool_use()

Add a tool execution to conversation history.

```python
add_tool_use(
    tool_name: str,
    tool_input: Dict[str, Any],
    tool_response: Optional[str],
    turn: int,
    session_id: str,
    latency_ms: Optional[int] = None,
    success: bool = True
) -> ToolUse
```

**Parameters:**
- `tool_name` (str): Name of the tool (required, min length 1)
- `tool_input` (Dict[str, Any]): Tool input parameters (required)
- `tool_response` (Optional[str]): Tool execution result
- `turn` (int): Turn number in conversation (required, 1-indexed)
- `session_id` (str): Session identifier (required, min length 1)
- `latency_ms` (Optional[int]): Tool execution time in milliseconds
- `success` (bool): Whether tool execution succeeded (default: True)

**Returns:**
- `ToolUse`: Created tool use record with timestamp and execution metadata

**Example:**

```python
tool_use = uacs.add_tool_use(
    tool_name="Edit",
    tool_input={
        "file_path": "src/auth.py",
        "old_string": "# TODO: Implement auth",
        "new_string": "def authenticate(token): ..."
    },
    tool_response="Successfully edited auth.py",
    turn=2,
    session_id="session_001",
    latency_ms=2300,
    success=True
)

print(f"Tool: {tool_use.tool_name}")
print(f"Latency: {tool_use.latency_ms}ms")
print(f"Success: {tool_use.success}")
```

**Supported Tools:**

All Claude Code tools are supported:
- `Edit` - File editing
- `Bash` - Command execution
- `Read` - File reading
- `Write` - File writing
- `Grep` - Content search
- `Glob` - File pattern matching

---

## Knowledge Methods

Capture architectural knowledge with semantic indexing.

### add_decision()

Add an architectural decision to knowledge base.

```python
add_decision(
    question: str,
    decision: str,
    rationale: str,
    session_id: str,
    alternatives: Optional[List[str]] = None,
    decided_by: str = "claude-sonnet-4",
    topics: Optional[List[str]] = None
) -> Decision
```

**Parameters:**
- `question` (str): Question or problem addressed (required, min length 1)
- `decision` (str): Decision that was made (required, min length 1)
- `rationale` (str): Reasoning behind the decision (required, min length 1)
- `session_id` (str): Session where decision was made (required, min length 1)
- `alternatives` (Optional[List[str]]): Alternative approaches considered
- `decided_by` (str): Who/what made the decision (default: "claude-sonnet-4")
- `topics` (Optional[List[str]]): Topic tags

**Returns:**
- `Decision`: Created decision with timestamp and metadata

**Example:**

```python
decision = uacs.add_decision(
    question="How should we handle API authentication?",
    decision="Use JWT tokens with refresh token rotation",
    rationale="Provides good security balance, is stateless, and works well with microservices architecture",
    session_id="session_001",
    alternatives=[
        "Session-based authentication (doesn't scale horizontally)",
        "OAuth2 only (too complex for our use case)",
        "API keys (less secure, no expiration)"
    ],
    topics=["authentication", "api", "security"]
)

print(f"Question: {decision.question}")
print(f"Decision: {decision.decision}")
print(f"Alternatives: {len(decision.alternatives)}")
```

**Architecture Decision Records (ADR):**

Decisions follow the ADR pattern, capturing context, decision, and consequences. Use them for:
- Technology choices (libraries, frameworks, languages)
- Architecture patterns (microservices, monolith, event-driven)
- Implementation approaches (REST vs GraphQL, SQL vs NoSQL)
- Process decisions (testing strategy, deployment approach)

---

### add_convention()

Add a project convention or pattern to knowledge base.

```python
add_convention(
    content: str,
    topics: Optional[List[str]] = None,
    source_session: Optional[str] = None,
    confidence: float = 1.0
) -> Convention
```

**Parameters:**
- `content` (str): Convention description (required, min length 1)
- `topics` (Optional[List[str]]): Topic tags
- `source_session` (Optional[str]): Session where convention was established
- `confidence` (float): Confidence score 0.0-1.0 (default: 1.0)

**Returns:**
- `Convention`: Created convention with timestamps and confidence tracking

**Example:**

```python
convention = uacs.add_convention(
    content="We always use Pydantic models for data validation and API contracts",
    topics=["validation", "data-models", "best-practice"],
    source_session="session_001",
    confidence=1.0
)

# Inferred convention (lower confidence)
inferred_convention = uacs.add_convention(
    content="Tests should be colocated with source files",
    topics=["testing", "project-structure"],
    source_session="session_002",
    confidence=0.7  # Observed pattern, not explicitly stated
)

print(f"Convention: {convention.content}")
print(f"Confidence: {convention.confidence}")
```

**Use Cases:**

- **Coding Standards**: "Use Black for code formatting"
- **Naming Conventions**: "API endpoints use kebab-case"
- **Architecture Patterns**: "Services communicate via message queue"
- **Testing Practices**: "All async functions must have async tests"
- **Security Practices**: "Always validate user input before database queries"

---

### add_learning()

Add a cross-session learning or insight to knowledge base.

```python
add_learning(
    pattern: str,
    learned_from: List[str],
    category: str = "general",
    confidence: float = 1.0
) -> Learning
```

**Parameters:**
- `pattern` (str): Learned pattern or insight (required, min length 1)
- `learned_from` (List[str]): Session IDs where pattern was observed (required, min length 1)
- `category` (str): Category of learning (default: "general")
- `confidence` (float): Confidence score 0.0-1.0 (default: 1.0)

**Returns:**
- `Learning`: Created learning with timestamp and session tracking

**Example:**

```python
learning = uacs.add_learning(
    pattern="When implementing authentication, always add rate limiting to prevent brute force attacks",
    learned_from=["session_001", "session_002", "session_005"],
    category="security_best_practice",
    confidence=0.95
)

# Performance learning
perf_learning = uacs.add_learning(
    pattern="Database queries with LIKE on large tables are slow, use full-text search instead",
    learned_from=["session_010", "session_015"],
    category="performance",
    confidence=1.0
)

print(f"Pattern: {learning.pattern}")
print(f"Learned from: {len(learning.learned_from)} sessions")
print(f"Category: {learning.category}")
```

**Categories:**

Common learning categories:
- `performance` - Performance optimizations
- `security_best_practice` - Security patterns
- `usability` - User experience insights
- `maintainability` - Code maintainability patterns
- `testing` - Testing strategies
- `debugging` - Debugging approaches
- `architecture` - Architectural insights

---

### add_artifact()

Add a code artifact reference to knowledge base.

```python
add_artifact(
    type: str,
    path: str,
    description: str,
    created_in_session: str,
    topics: Optional[List[str]] = None
) -> Artifact
```

**Parameters:**
- `type` (str): Artifact type (required, min length 1)
- `path` (str): File path or identifier (required, min length 1)
- `description` (str): Human-readable description (required, min length 1)
- `created_in_session` (str): Session where artifact was created (required, min length 1)
- `topics` (Optional[List[str]]): Topic tags

**Returns:**
- `Artifact`: Created artifact with metadata

**Example:**

```python
# File artifact
file_artifact = uacs.add_artifact(
    type="file",
    path="src/auth.py",
    description="JWT authentication implementation with refresh token support",
    created_in_session="session_001",
    topics=["auth", "security"]
)

# Class artifact
class_artifact = uacs.add_artifact(
    type="class",
    path="src/uacs/api.py::UACS",
    description="Main UACS API entry point with semantic methods",
    created_in_session="session_003",
    topics=["api", "core"]
)

# Function artifact
function_artifact = uacs.add_artifact(
    type="function",
    path="src/utils/validation.py::validate_jwt",
    description="JWT token validation with expiration checking",
    created_in_session="session_001",
    topics=["auth", "validation"]
)

print(f"Artifact: {file_artifact.path}")
print(f"Type: {file_artifact.type}")
print(f"Description: {file_artifact.description}")
```

**Artifact Types:**

- `file` - Source code files
- `class` - Class definitions
- `function` - Function/method definitions
- `module` - Python modules
- `config` - Configuration files
- `test` - Test files
- `script` - Utility scripts
- `document` - Documentation files

---

## Search Method

Natural language semantic search across all stored context.

### search()

Search across conversations and knowledge with natural language.

```python
search(
    query: str,
    types: Optional[List[str]] = None,
    min_confidence: float = 0.7,
    session_id: Optional[str] = None,
    limit: int = 10
) -> List[SearchResult]
```

**Parameters:**
- `query` (str): Natural language search query (required)
- `types` (Optional[List[str]]): Filter by type (user_message, assistant_message, tool_use, convention, decision, learning, artifact)
- `min_confidence` (float): Minimum confidence threshold 0.0-1.0 (default: 0.7)
- `session_id` (Optional[str]): Filter by specific session
- `limit` (int): Maximum results to return (default: 10)

**Returns:**
- `List[SearchResult]`: Results sorted by relevance (highest first)

**Example:**

```python
# Basic search
results = uacs.search("how did we implement authentication?", limit=10)
for result in results:
    print(f"[{result.metadata['type']}] {result.text}")
    print(f"Relevance: {result.similarity:.2f}\n")

# Type-specific search
decisions = uacs.search(
    "authentication decisions",
    types=["decision"],
    limit=5
)

# Session-specific search
session_results = uacs.search(
    "what did we discuss?",
    session_id="session_001",
    limit=20
)

# High-confidence only
confident_results = uacs.search(
    "security best practices",
    types=["convention", "learning"],
    min_confidence=0.9,
    limit=10
)
```

**Search Result Fields:**

```python
result = results[0]
print(f"Type: {result.metadata['type']}")        # user_message, decision, etc.
print(f"Text: {result.text}")                    # Content
print(f"Similarity: {result.similarity}")        # 0.0-1.0 relevance score
print(f"Session: {result.metadata.get('session_id')}")
print(f"Topics: {result.metadata.get('topics', [])}")
```

**Supported Types:**

- **Conversation Types:**
  - `user_message` - User prompts
  - `assistant_message` - Assistant responses
  - `tool_use` - Tool executions

- **Knowledge Types:**
  - `convention` - Project conventions
  - `decision` - Architectural decisions
  - `learning` - Cross-session learnings
  - `artifact` - Code artifacts

**Search Examples:**

```python
# Find security-related context
security = uacs.search("security vulnerabilities", limit=15)

# Find implementation details
impl = uacs.search("how did we implement the feature?", types=["tool_use", "artifact"])

# Find decision rationale
why = uacs.search("why did we choose this approach?", types=["decision"])

# Find conventions
patterns = uacs.search("coding patterns we follow", types=["convention", "learning"])

# Find recent context
recent = uacs.search("what happened in the last session?", session_id="session_001")
```

---

## Statistics Methods

Access system statistics and capabilities.

### get_stats()

Get comprehensive UACS statistics.

```python
get_stats() -> Dict[str, Any]
```

**Returns:**
- Dictionary with statistics from all components

**Example:**

```python
stats = uacs.get_stats()

print(f"Project: {stats['project_path']}")

# Adapter stats
print(f"Agent skills: {stats['adapters']['agent_skills']['count']}")
print(f"AGENTS.md loaded: {stats['adapters']['agents_md']['loaded']}")

# Package stats
print(f"Installed packages: {stats['packages']['installed_count']}")

# Context stats (v0.2.0)
print(f"Total entries: {stats['context']['entry_count']}")
print(f"Total tokens: {stats['context']['total_tokens']}")
print(f"Compression ratio: {stats['context']['compression_ratio']}")

# Semantic stats (v0.3.0)
print(f"Conversations: {stats['semantic']['conversations']}")
print(f"Knowledge entries: {stats['semantic']['knowledge']}")
print(f"Embeddings: {stats['semantic']['embeddings']}")
```

**Response Structure:**

```python
{
    "project_path": "/path/to/project",
    "adapters": {
        "agent_skills": {"count": 3, "paths": [...]},
        "agents_md": {"loaded": True, "path": "..."}
    },
    "packages": {
        "installed_count": 5,
        "skills_dir": ".agent/skills"
    },
    "context": {
        "entry_count": 127,
        "total_tokens": 45234,
        "compression_ratio": 0.85
    },
    "semantic": {
        "conversations": {
            "user_messages": 45,
            "assistant_messages": 43,
            "tool_uses": 89,
            "total_tokens": 127500
        },
        "knowledge": {
            "conventions": 12,
            "decisions": 8,
            "learnings": 5,
            "artifacts": 23
        },
        "embeddings": {
            "total_vectors": 177,
            "index_size_mb": 2.3
        }
    },
    "capabilities": {...}
}
```

---

### get_capabilities()

Get available capabilities for an agent.

```python
get_capabilities(agent: Optional[str] = None) -> Dict[str, Any]
```

**Parameters:**
- `agent` (Optional[str]): Agent name to filter capabilities (default: None for all)

**Returns:**
- Dictionary of available capabilities

**Example:**

```python
# Get all capabilities
all_caps = uacs.get_capabilities()
print(f"Agent skills: {len(all_caps.get('agent_skills', []))}")

# Get capabilities for specific agent
claude_caps = uacs.get_capabilities(agent="claude")
print(f"Claude capabilities: {claude_caps}")
```

---

### get_token_stats()

Get token usage and compression statistics.

```python
get_token_stats() -> Dict[str, int]
```

**Returns:**
- Dictionary of token counts

**Example:**

```python
token_stats = uacs.get_token_stats()

print(f"Total tokens: {token_stats.get('total_tokens', 0)}")
print(f"Compressed tokens: {token_stats.get('compressed_tokens', 0)}")
print(f"Tokens saved: {token_stats.get('tokens_saved', 0)}")
print(f"Compression ratio: {token_stats.get('compression_ratio', 0)}")
```

---

## Legacy Methods

### add_to_context() (DEPRECATED)

**Status:** Deprecated in v0.3.0, removed in v0.5.0

```python
add_to_context(
    key: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    topics: Optional[List[str]] = None
)
```

**Deprecation Warning:**

```python
DeprecationWarning: add_to_context() is deprecated in v0.3.0.
Use structured methods like add_user_message(), add_convention(),
add_decision() for better semantic search.
```

**Migration:**

See [Migration Guide](MIGRATION.md) for complete upgrade instructions.

**Quick replacement guide:**

```python
# OLD (deprecated)
uacs.add_to_context(key="user", content="Help me...", topics=["dev"])

# NEW (recommended)
uacs.add_user_message(content="Help me...", turn=1, session_id="s1", topics=["dev"])
```

---

## Data Models

UACS v0.3.0 uses Pydantic models for type safety and validation.

### Conversation Models

Located in `src/uacs/conversations/models.py`:

- **UserMessage**: User prompt with turn, session_id, topics, timestamp
- **AssistantMessage**: Assistant response with turn, session_id, tokens, model, timestamp
- **ToolUse**: Tool execution with tool_name, input, response, turn, session_id, latency, success, timestamp

### Knowledge Models

Located in `src/uacs/knowledge/models.py`:

- **Decision**: Architectural decision with question, decision, rationale, alternatives, decided_by, session_id, topics, timestamp
- **Convention**: Project convention with content, topics, source_session, confidence, created_at, last_verified
- **Learning**: Cross-session learning with pattern, learned_from, category, confidence, created_at
- **Artifact**: Code artifact with type, path, description, created_in_session, topics

### Search Models

Located in `src/uacs/embeddings/manager.py`:

- **SearchResult**: Search result with type, text, similarity, metadata (includes session_id, topics, etc.)

### Model Validation

All models use Pydantic validation:

```python
from uacs import UACS

# This will raise validation error (turn must be >= 1)
try:
    uacs.add_user_message(content="test", turn=0, session_id="s1")
except ValueError as e:
    print(f"Validation error: {e}")

# This will raise validation error (content must be non-empty)
try:
    uacs.add_user_message(content="", turn=1, session_id="s1")
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Complete Example

Here's a complete example showing all v0.3.0 features:

```python
from uacs import UACS
from pathlib import Path

# Initialize
uacs = UACS(project_path=Path("."))

# Session ID (in Claude Code, this is automatically provided)
session_id = "session_001"

# Track conversation
user_msg = uacs.add_user_message(
    content="Help me implement JWT authentication for the API",
    turn=1,
    session_id=session_id,
    topics=["security", "feature", "api"]
)

assistant_msg = uacs.add_assistant_message(
    content="I'll help you implement JWT authentication. First, let's install the required packages...",
    turn=1,
    session_id=session_id,
    tokens_in=52,
    tokens_out=178,
    model="claude-sonnet-4"
)

# Track tool usage
tool_use = uacs.add_tool_use(
    tool_name="Bash",
    tool_input={"command": "pip install pyjwt bcrypt"},
    tool_response="Successfully installed pyjwt-2.8.0 bcrypt-4.1.2",
    turn=2,
    session_id=session_id,
    latency_ms=1200,
    success=True
)

# Capture decision
decision = uacs.add_decision(
    question="Which JWT library should we use?",
    decision="Use PyJWT with bcrypt for password hashing",
    rationale="PyJWT is well-maintained, widely used, and provides good security defaults. Bcrypt is the industry standard for password hashing.",
    session_id=session_id,
    alternatives=[
        "python-jose (less popular)",
        "authlib (too heavy for our needs)"
    ],
    topics=["security", "dependencies"]
)

# Add convention
convention = uacs.add_convention(
    content="We always use httpOnly cookies for storing JWT tokens to prevent XSS attacks",
    topics=["security", "auth"],
    source_session=session_id,
    confidence=1.0
)

# Add learning
learning = uacs.add_learning(
    pattern="When implementing authentication, always add rate limiting to prevent brute force attacks",
    learned_from=[session_id],
    category="security_best_practice",
    confidence=1.0
)

# Track artifact
artifact = uacs.add_artifact(
    type="file",
    path="src/auth.py",
    description="JWT authentication implementation with bcrypt password hashing and httpOnly cookie support",
    created_in_session=session_id,
    topics=["auth", "security"]
)

# Search semantically
print("\nSearching for authentication implementation...")
results = uacs.search("how did we implement authentication?", limit=5)
for i, result in enumerate(results, 1):
    print(f"\n{i}. [{result.metadata['type']}] (relevance: {result.similarity:.2f})")
    print(f"   {result.text[:100]}...")

# Get statistics
print("\nSystem Statistics:")
stats = uacs.get_stats()
print(f"  Conversations: {stats['semantic']['conversations']}")
print(f"  Knowledge: {stats['semantic']['knowledge']}")
print(f"  Embeddings: {stats['semantic']['embeddings']}")
```

---

## Next Steps

- Read the [Migration Guide](MIGRATION.md) to upgrade from v0.2.x
- See the [Hooks Guide](../.claude-plugin/HOOKS_GUIDE.md) for Claude Code integration
- Check the [README](../README.md) for project overview
- Explore [examples/](../examples/) for more code samples

---

**Version:** v0.3.0
**Last Updated:** 2026-02-02
**Repository:** https://github.com/kylebrodeur/universal-agent-context
