# Migrating from v0.2.x to v0.3.0

## Overview

UACS v0.3.0 introduces a new **semantic API** that provides structured conversation tracking and knowledge extraction. The old API (`add_to_context()`) is deprecated but still works for backward compatibility.

**Key Changes:**
- Unified entry point (`from uacs import UACS` - no changes needed)
- Structured methods replace generic `add_to_context()`
- Semantic search across all context with natural language queries
- Automatic embedding generation for all stored data
- Claude Code hooks for automatic capture

## Breaking Changes

### None! 🎉

v0.3.0 is **fully backward compatible**. Your existing code will continue to work, but you'll see deprecation warnings encouraging you to migrate to the new semantic API.

## What's New in v0.3.0

### 1. Unified Entry Point (No Changes Required)

The import statement remains the same:

**Before (v0.2.x):**
```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path("."))
```

**After (v0.3.0):**
```python
from uacs import UACS  # Same import
from pathlib import Path

uacs = UACS(project_path=Path("."))  # Same initialization
```

### 2. Structured Methods Replace Generic add_to_context()

The new semantic API provides structured methods for different types of context:

**Before (v0.2.x):**
```python
# Everything was generic context
uacs.add_to_context(
    key="decision_001",
    content="We decided to use JWT because it's stateless",
    topics=["security"],
    metadata={"type": "decision"}  # Manual typing
)
```

**After (v0.3.0):**
```python
# Structured decision capture
uacs.add_decision(
    question="Which auth method should we use?",
    decision="JWT tokens",
    rationale="Stateless and scalable",
    session_id="session_001",
    topics=["security"]
)
```

### 3. Semantic Search Across All Context

Natural language queries replace topic-only filtering:

**Before (v0.2.x):**
```python
# Limited to topic-based search
entries = uacs.shared_context.search_by_topic("security")
```

**After (v0.3.0):**
```python
# Natural language search across everything
results = uacs.search(
    "how did we implement authentication?",
    types=["user_message", "decision", "convention"],
    limit=10
)

for result in results:
    print(f"[{result.metadata['type']}] {result.text}")
    print(f"Relevance: {result.similarity:.2f}\n")
```

### 4. Automatic Embedding Generation

All data is automatically indexed with semantic embeddings:

**Before (v0.2.x):**
```python
# No automatic embeddings
# Had to manually manage indexing
```

**After (v0.3.0):**
```python
# Automatic embeddings for all entries
uacs.add_convention("Use Pydantic for validation", topics=["dev"])
# Now searchable with: uacs.search("what validation library do we use?")
```

## Migration Steps

### Step 1: Update Imports (No Changes Needed!)

Your imports remain the same:

```python
from uacs import UACS
from pathlib import Path
```

### Step 2: Replace add_to_context() Calls

Find all calls to `add_to_context()` and replace with appropriate semantic methods based on the content type:

#### For User Messages

**Before:**
```python
uacs.add_to_context(
    key="user_msg",
    content="Help me implement authentication",
    topics=["security"]
)
```

**After:**
```python
uacs.add_user_message(
    content="Help me implement authentication",
    turn=1,
    session_id="session_001",
    topics=["security"]
)
```

#### For Assistant Responses

**Before:**
```python
uacs.add_to_context(
    key="assistant_msg",
    content="I'll help you implement JWT authentication...",
    topics=["security"]
)
```

**After:**
```python
uacs.add_assistant_message(
    content="I'll help you implement JWT authentication...",
    turn=1,
    session_id="session_001",
    tokens_in=42,
    tokens_out=156,
    model="claude-sonnet-4"
)
```

#### For Tool Executions

**Before:**
```python
uacs.add_to_context(
    key="tool_edit",
    content="Edited auth.py",
    topics=["code"]
)
```

**After:**
```python
uacs.add_tool_use(
    tool_name="Edit",
    tool_input={"file_path": "auth.py", "changes": "..."},
    tool_response="Successfully edited auth.py",
    turn=2,
    session_id="session_001",
    latency_ms=2300,
    success=True
)
```

#### For Architectural Decisions

**Before:**
```python
uacs.add_to_context(
    key="decision",
    content="Decided to use JWT for authentication",
    topics=["security", "architecture"]
)
```

**After:**
```python
uacs.add_decision(
    question="Which authentication method should we use?",
    decision="JWT tokens",
    rationale="Stateless, scalable, works well with microservices",
    session_id="session_001",
    alternatives=["Session-based authentication", "OAuth2"],
    topics=["security", "architecture"]
)
```

#### For Project Conventions

**Before:**
```python
uacs.add_to_context(
    key="convention",
    content="We always use httpOnly cookies for auth tokens",
    topics=["security"]
)
```

**After:**
```python
uacs.add_convention(
    content="We always use httpOnly cookies for auth tokens",
    topics=["security"],
    source_session="session_001",
    confidence=1.0
)
```

#### For Code Artifacts

**Before:**
```python
uacs.add_to_context(
    key="artifact",
    content="Created auth.py with JWT implementation",
    topics=["code", "security"]
)
```

**After:**
```python
uacs.add_artifact(
    type="file",
    path="src/auth.py",
    description="JWT authentication implementation",
    created_in_session="session_001",
    topics=["code", "security"]
)
```

### Step 3: Update Search Calls

Replace topic-based searches with semantic queries:

**Before:**
```python
# Topic-only search
entries = uacs.shared_context.search_by_topic("auth")
for entry in entries:
    print(entry.content)
```

**After:**
```python
# Natural language semantic search
results = uacs.search("authentication implementation", limit=20)
for result in results:
    print(f"[{result.metadata['type']}] {result.text}")
    print(f"Relevance: {result.similarity:.2f}\n")
```

### Step 4: Update Hook Usage (If Using Plugin)

If you're using the Claude Code plugin, update to the semantic hooks:

**Before (v0.2.x):**
```bash
# Old plugin config
cp .claude-plugin/plugin-proactive.json ~/.claude/plugin.json
```

**After (v0.3.0):**
```bash
# New semantic plugin config
cp .claude-plugin/plugin-semantic.json ~/.claude/plugin.json
cp .claude-plugin/hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py
```

The semantic plugin includes:
- **UserPromptSubmit**: Captures user messages with topic extraction
- **PostToolUse**: Tracks tool executions with full context
- **SessionEnd**: Extracts decisions and conventions from conversations

See [Hooks Guide](../.claude-plugin/HOOKS_GUIDE.md) for details.

## Deprecation Timeline

| Version | Status | Action Required |
|---------|--------|-----------------|
| **v0.3.0** | `add_to_context()` deprecated with warnings | Start migrating to semantic API |
| **v0.4.0** | `add_to_context()` still works with warnings | Continue migration |
| **v0.5.0** | `add_to_context()` removed | Migration must be complete |

**Recommendation:** Migrate to the semantic API now to avoid breaking changes in v0.5.0.

## Testing Your Migration

### 1. Update Imports

No changes needed - imports remain the same.

### 2. Replace add_to_context() Calls

Use the guidelines above to replace all `add_to_context()` calls with structured methods.

### 3. Run Your Tests

```bash
pytest tests/ -v
```

### 4. Check for Deprecation Warnings

Run your code with warnings enabled:

```bash
python -W all your_script.py
```

You should see warnings like:
```
DeprecationWarning: add_to_context() is deprecated in v0.3.0.
Use structured methods like add_user_message(), add_convention(), add_decision()
for better semantic search.
```

### 5. Verify Semantic Search Works

Test the new search functionality:

```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path("."))

# Add some test data
uacs.add_convention(
    content="Use Pydantic for all data validation",
    topics=["validation"]
)

# Search for it
results = uacs.search("what validation library do we use?", limit=5)
assert len(results) > 0
print(f"Found {len(results)} results!")
```

## Example: Full Migration

Here's a complete before/after example:

### Before (v0.2.x)

```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path("."))

# Generic context entries
uacs.add_to_context("user", "Help with auth", topics=["security"])
uacs.add_to_context("decision", "Use JWT", topics=["security"])
uacs.add_to_context("code", "Implemented auth.py", topics=["security"])

# Topic-based search
entries = uacs.shared_context.search_by_topic("security")
for entry in entries:
    print(entry.content)
```

### After (v0.3.0)

```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path("."))

# Structured semantic entries
uacs.add_user_message(
    content="Help with auth",
    turn=1,
    session_id="session_001",
    topics=["security"]
)

uacs.add_decision(
    question="Which auth method?",
    decision="JWT tokens",
    rationale="Stateless and scalable",
    session_id="session_001",
    alternatives=["Session-based"],
    topics=["security"]
)

uacs.add_artifact(
    type="file",
    path="auth.py",
    description="Auth implementation",
    created_in_session="session_001",
    topics=["security"]
)

# Natural language semantic search
results = uacs.search("security implementation", limit=10)
for result in results:
    print(f"[{result.metadata['type']}] {result.text}")
    print(f"Relevance: {result.similarity:.2f}\n")
```

## Benefits of Migrating

### ✅ Better Search

Natural language queries instead of topic-only filtering:
- "how did we implement authentication?" finds relevant decisions, conventions, and code
- Relevance-ranked results (not just matching topics)
- Cross-type search (find decisions, conventions, and artifacts together)

### ✅ Structured Data

Explicit types (decisions, conventions, learnings) instead of generic context:
- Type-specific fields (question/decision/rationale for decisions)
- Better validation (Pydantic models enforce structure)
- Easier to query and filter by type

### ✅ Automatic Embeddings

Semantic indexing for all entries:
- No manual embedding management
- Consistent indexing across all data types
- Fast semantic search (FAISS backend)

### ✅ Hooks Integration

Seamless Claude Code integration:
- Automatic capture of user messages
- Tool execution tracking
- Decision and convention extraction from conversations

### ✅ Future-Proof

Ready for v0.5.0+ features:
- Cross-session learning patterns
- Workflow suggestion system
- Advanced analytics and insights

## Getting Help

### Documentation

- [API Reference](API_REFERENCE.md) - Complete v0.3.0 API documentation
- [Hooks Guide](../.claude-plugin/HOOKS_GUIDE.md) - Claude Code integration
- [README](../README.md) - Project overview

### Support

- **Issues**: [GitHub Issues](https://github.com/kylebrodeur/universal-agent-context/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kylebrodeur/universal-agent-context/discussions)

## Common Migration Questions

### Q: Do I need to update my imports?

**A:** No! The import statement remains the same: `from uacs import UACS`.

### Q: Will my old code break?

**A:** No! v0.3.0 is fully backward compatible. `add_to_context()` still works but shows deprecation warnings.

### Q: When will add_to_context() be removed?

**A:** v0.5.0 (estimated Q3 2026). You have plenty of time to migrate.

### Q: Can I use both APIs during migration?

**A:** Yes! You can gradually migrate your codebase. Old and new methods work together.

### Q: How do I disable deprecation warnings?

**A:** You can suppress them temporarily:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

But we recommend migrating instead of suppressing warnings.

### Q: What if I don't know which method to use?

**A:** Use this decision tree:

- **User prompt?** → `add_user_message()`
- **Assistant response?** → `add_assistant_message()`
- **Tool execution?** → `add_tool_use()`
- **Architectural decision?** → `add_decision()`
- **Project convention/pattern?** → `add_convention()`
- **Cross-session learning?** → `add_learning()`
- **Code artifact?** → `add_artifact()`

### Q: Do I need to reindex my old data?

**A:** No! Old data stored with `add_to_context()` is automatically included in searches. However, for best results, consider re-capturing important context with the structured methods.

### Q: How do I migrate my Claude Code hooks?

**A:** Replace `plugin-proactive.json` with `plugin-semantic.json`:

```bash
cp .claude-plugin/plugin-semantic.json ~/.claude/plugin.json
```

The new hooks use the semantic API automatically.

## Migration Checklist

Use this checklist to track your migration progress:

- [ ] Read this migration guide
- [ ] Update dependencies (`pip install --upgrade universal-agent-context`)
- [ ] Find all `add_to_context()` calls in your codebase
- [ ] Replace with appropriate structured methods
- [ ] Update search calls to use `search()` instead of `search_by_topic()`
- [ ] Update Claude Code hooks (if using plugin)
- [ ] Run tests and verify functionality
- [ ] Check for deprecation warnings
- [ ] Test semantic search functionality
- [ ] Update your documentation/README

## Next Steps

Once you've migrated:

1. **Explore semantic search**: Try natural language queries to find relevant context
2. **Use Claude Code hooks**: Enable automatic capture during development sessions
3. **Read the API Reference**: Learn about all available methods and parameters
4. **Share feedback**: Let us know how the migration went!

---

**Version:** v0.3.0
**Last Updated:** 2026-02-02
**Migration Deadline:** v0.5.0 (Q3 2026)
