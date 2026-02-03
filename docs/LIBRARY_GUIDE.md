# UACS Library Guide

The Universal Agent Context System (UACS) can be used as a Python library to integrate advanced context management into your own AI applications.

## Installation

```bash
pip install universal-agent-context
# or
uv add universal-agent-context
```

## Core Components

### UnifiedContextAdapter

The `UnifiedContextAdapter` is the main entry point for managing context. It combines:
- **Project Context**: From `AGENTS.md`
- **Capabilities**: From `SKILLS.md` or `.agent/skills/`
- **Shared History**: Runtime conversation history

```python
from uacs.context.unified_context import UnifiedContextAdapter

# Initialize adapter (automatically finds config files in current dir)
adapter = UnifiedContextAdapter()

# Build a prompt for an agent
prompt_data = adapter.build_agent_prompt(
    user_query="Review the authentication logic",
    agent_name="claude",
    include_history=True,
    max_context_tokens=8000
)

print(f"System Prompt: {prompt_data.system_prompt}")
print(f"Context Tokens: {prompt_data.token_count}")
```

### SharedContextManager

Manage runtime history with automatic compression.

```python
from uacs.context.shared_context import SharedContextManager

ctx = SharedContextManager()

# Add an entry
ctx.add_entry(
    content="User requested code review",
    agent="user",
    role="user"
)

# Add agent response
ctx.add_entry(
    content="I found a security vulnerability...",
    agent="claude",
    role="assistant",
    topics=["security", "auth"]
)

# Get compressed context
history = ctx.get_compressed_context(max_tokens=2000)
```

### Package Management

Search and install skills programmatically.

```python
from pathlib import Path
from uacs import UACS

uacs = UACS(Path.cwd())

# Search
results = uacs.search("python", package_type="skills")

# Install
if results:
    uacs.install(results[0])
```

### Memory

Persistent storage for long-term memory.

```python
from uacs.memory.simple_memory import SimpleMemoryStore

store = SimpleMemoryStore()

# Store a memory
store.add_memory(
    content="The user prefers TypeScript over JavaScript",
    tags=["preference", "language"]
)

# Retrieve memories
memories = store.search("typescript preference")
```

## Advanced Usage

### Custom Format Adapters

You can create custom adapters to support new configuration formats. See [ADAPTERS.md](./ADAPTERS.md) for details.

### Direct API Access

The `UACS` class provides a high-level facade for common operations.

```python
from uacs import UACS

app = UACS()

# Check capabilities
caps = app.get_capabilities()

# Manage skills
skills = app.list_skills()
```
