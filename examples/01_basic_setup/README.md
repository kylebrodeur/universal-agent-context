# Demo 1: Basic Setup

## What

This demo introduces the core UACS workflow, showing how to:
- Initialize UACS in a project
- Add context entries to shared memory
- Build compressed context for AI agents
- Check token statistics

This is your "Hello World" for UACS - the foundational workflow that all other features build upon.

## Why

**Value Proposition:** Understanding basic UACS operations is essential for:
- Onboarding new users to the UACS ecosystem
- Learning the fundamental context management workflow
- Building a mental model of how context flows through the system
- Preparing for more advanced features (compression, multi-agent, topics)

**Real-world Impact:**
- Get started with UACS in under 5 minutes
- Understand the core API that powers all features
- Build confidence before tackling complex use cases

## When

Use this workflow when:
- Starting a new project with UACS
- Teaching others about UACS fundamentals
- Testing your UACS installation
- Building your first UACS integration

**This is the entry point for all UACS users.**

## How

### Step 1: Initialize UACS

```python
from uacs import UACS
from pathlib import Path

# Initialize UACS for your project
uacs = UACS(project_path=Path.cwd())
```

UACS creates a `.state/context/` directory to store shared context between sessions.

### Step 2: Add Context Entries

```python
# Add a user request
uacs.add_to_context(
    key="user",
    content="Please review the authentication module for security issues.",
    topics=["security", "code-review"]
)

# Add an agent response
uacs.add_to_context(
    key="claude",
    content="Found potential timing attack in password comparison at line 42.",
    topics=["security", "finding"]
)
```

Each entry is automatically:
- Timestamped
- Tagged with topics for retrieval
- Deduplicated (identical content is stored once)
- Scored for quality

### Step 3: Build Context

```python
# Build compressed context for an agent
context = uacs.build_context(
    query="Continue the security review",
    agent="claude",
    max_tokens=4000,
    topics=["security"]
)

print(context)
```

UACS automatically:
- Retrieves relevant entries based on topics
- Applies compression (deduplication, summarization)
- Stays within token budget
- Returns formatted context ready for LLM

### Step 4: Check Statistics

```python
# Get token usage statistics
stats = uacs.get_token_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Compression ratio: {stats['compression_ratio']}%")
```

## Output

Running this demo produces:

```
Initializing UACS...
Project path: /Users/you/project
State directory: /Users/you/project/.state/context

Adding context entries...
Added entry: user (topics: security, code-review)
Added entry: claude (topics: security, finding)

Building context...
Context built: 234 tokens (compressed from 456 tokens)

Token Statistics:
  total_tokens: 456
  compressed_tokens: 234
  compression_ratio: 48.7%
  tokens_saved: 222
```

## What You Learned

- **Initialization:** UACS uses project-local storage (`.state/context/`)
- **Context Entries:** Simple key-value pairs with automatic metadata
- **Topics:** Enable semantic filtering and focused retrieval
- **Compression:** Happens automatically when building context
- **Statistics:** Real-time visibility into token usage

## Next Steps

1. **Demo 2: Context Compression** - Deep dive into compression algorithms and 70%+ savings
2. **Demo 3: Multi-Agent Context** - Share context between multiple agents
3. **Demo 4: Topic-Based Retrieval** - Advanced filtering for large contexts

## Running the Demo

```bash
# From the project root
cd examples/01_basic_setup
uv run python demo.py

# Or directly
uv run python examples/01_basic_setup/demo.py
```

Expected runtime: < 1 second

## Key Concepts

- **Shared Context:** All agents access the same context store
- **Topics:** Semantic tags for filtering (e.g., "security", "testing", "performance")
- **Compression:** Automatic token reduction while preserving information
- **Quality Scoring:** Entries are scored based on length, topics, and recency

## Common Questions

**Q: Where is the context stored?**
A: In `.state/context/` within your project directory. This is persistent between sessions.

**Q: What happens if I add duplicate content?**
A: UACS automatically deduplicates based on content hash. Duplicates are stored once but tracked for frequency.

**Q: Can I use UACS without topics?**
A: Yes, topics are optional. Without topics, all context is retrieved in chronological order.

**Q: How does compression work?**
A: See Demo 2 for a detailed breakdown. In brief: deduplication, quality filtering, and LLM-based summarization.

## Troubleshooting

**Issue:** `ImportError: No module named 'uacs'`
**Solution:** Make sure you've installed UACS with `uv sync` or `pip install -e .`

**Issue:** `Permission denied` when creating `.state/context/`
**Solution:** Check write permissions in your project directory.

**Issue:** Context is empty when building
**Solution:** Make sure you've added entries before calling `build_context()`.

## Related Documentation

- [Library Guide](../../docs/LIBRARY_GUIDE.md) - Complete API reference
- [Context Management](../../docs/CONTEXT.md) - Deep dive into context system
- [CLI Reference](../../docs/CLI_REFERENCE.md) - Command-line interface
