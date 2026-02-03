# UACS v0.3.0 Examples

**Learn UACS in 15 minutes with 4 focused examples.**

This directory contains simplified, production-ready examples demonstrating the v0.3.0 semantic API. Each example builds on the previous one, taking you from basics to advanced patterns.

---

## 🚀 Quick Start

Run all examples in sequence (recommended):

```bash
# 1. Core semantic API (5 minutes)
uv run python examples/01_semantic_basics.py

# 2. Claude Code integration (5 minutes)
uv run python examples/02_claude_code_integration.py

# 3. Web UI visualization (3 minutes)
uv run python examples/03_web_ui.py

# 4. Advanced patterns (2 minutes)
uv run python examples/04_search_and_knowledge.py
```

**Total time:** ~15 minutes to understand everything

---

## 📚 Examples Overview

### Example 1: Semantic API Basics
**File:** `01_semantic_basics.py`
**Time:** 5 minutes
**Teaches:**
- Track conversations (`add_user_message`, `add_assistant_message`, `add_tool_use`)
- Capture knowledge (`add_decision`, `add_convention`, `add_learning`, `add_artifact`)
- Search semantically (`search()` with natural language)
- Get statistics (`get_stats()`)

**When to run:** Start here! This is your introduction to the v0.3.0 API.

---

### Example 2: Claude Code Integration
**File:** `02_claude_code_integration.py`
**Time:** 5 minutes
**Teaches:**
- How UserPromptSubmit hook captures user messages automatically
- How PostToolUse hook tracks tool executions in real-time
- How SessionEnd hook extracts decisions and conventions
- How to query captured session data

**When to run:** After example 1, when you want to see the "killer use case"

**Real-world usage:**
```bash
# Install hooks for automatic capture:
cp .claude-plugin/plugin-semantic.json ~/.claude/plugin.json
cp .claude-plugin/hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py

# Now Claude Code automatically captures everything!
```

---

### Example 3: Web UI Visualization
**File:** `03_web_ui.py`
**Time:** 3 minutes
**Teaches:**
- How to populate UACS with rich sample data
- How to start the FastAPI backend (port 8081)
- How to start the Next.js frontend (port 3000)
- What features the Web UI provides

**When to run:** After example 2, when you want to visualize captured data

**To actually start the Web UI:**
```bash
# Single command - bundled UI!
uv run uacs web

# Or with custom options:
uv run uacs web --port 8081 --host localhost

# Then open browser:
open http://localhost:8081
```

💡 **Bundled Architecture:** The Web UI is now bundled into the Python package. The Next.js frontend (static export) is served directly from FastAPI - no separate frontend server needed!

---

### Example 4: Advanced Search & Knowledge
**File:** `04_search_and_knowledge.py`
**Time:** 2 minutes
**Teaches:**
- Type-filtered search (decisions only, conventions only)
- Confidence-filtered search (high-quality items)
- Multi-type search (search across categories)
- Knowledge organization best practices
- Cross-session insight extraction

**When to run:** After examples 1-3, when you want to learn advanced patterns

---

## 🎯 Learning Paths

### Path 1: Complete Learning (Recommended)
```
01_semantic_basics.py
    ↓
    Learn: Core API, conversations, knowledge, search
    ↓
02_claude_code_integration.py
    ↓
    Learn: Hooks, automatic capture, real-world usage
    ↓
03_web_ui.py
    ↓
    Learn: Visualization, Web UI, data exploration
    ↓
04_search_and_knowledge.py
    ↓
    Learn: Advanced patterns, best practices
```

**Total:** ~15 minutes

### Path 2: Quick Evaluation
If you're in a hurry, just run:
1. `01_semantic_basics.py` - See the API
2. `02_claude_code_integration.py` - See the value

**Total:** ~10 minutes

### Path 3: Visual Learner
If you prefer UI over code:
1. `01_semantic_basics.py` - Populate some data
2. `03_web_ui.py` - Start Web UI and explore visually

**Total:** ~8 minutes

---

## 📖 What's Different from v0.2.0?

**Old API (v0.2.0 - DEPRECATED):**
```python
# Generic, unstructured context
uacs.add_to_context(
    key="claude",
    content="Implemented JWT auth",
    topics=["security"]
)

# Generic retrieval
context = uacs.get_compressed_context(
    topic="security",
    max_tokens=4000
)
```

**New API (v0.3.0 - CURRENT):**
```python
# Structured conversations
uacs.add_user_message("Help with JWT auth", turn=1, session_id="s1")
uacs.add_assistant_message("I'll help...", turn=1, session_id="s1")
uacs.add_tool_use("Edit", {...}, "Success", turn=2, session_id="s1")

# Structured knowledge
uacs.add_decision(
    question="Which auth method?",
    decision="JWT with RS256",
    rationale="Stateless, scalable",
    alternatives=["Sessions", "OAuth2"]
)

# Natural language search
results = uacs.search("how did we implement authentication?")
```

**Why the change?**
- ✅ Natural language search vs topic filtering
- ✅ Structured types vs generic content
- ✅ Automatic embeddings for semantic search
- ✅ Better integration with Claude Code hooks

See [Migration Guide](../docs/MIGRATION.md) for full details.

---

## 🗂️ Old Examples (Deprecated)

The previous examples using v0.2.0 API have been archived:
- `tutorials/` - 5 tutorial series (deprecated API)
- `quickstart/` - 8 quickstart examples (deprecated API)

**These still work** (v0.2.0 API is functional but deprecated), but we recommend using the new examples above for v0.3.0.

If you need to reference the old examples, they're still in the repository but use deprecated methods.

---

## 🚀 Next Steps

After running the examples:

1. **Install Claude Code hooks** for automatic capture:
   ```bash
   cp .claude-plugin/plugin-semantic.json ~/.claude/plugin.json
   cp .claude-plugin/hooks/*.py ~/.claude/hooks/
   chmod +x ~/.claude/hooks/*.py
   ```

2. **Start using UACS in your projects**:
   ```python
   from uacs import UACS
   from pathlib import Path

   uacs = UACS(project_path=Path.cwd())
   # Now you can track conversations, capture knowledge, and search!
   ```

3. **Explore the Web UI**:
   - See [03_web_ui.py](03_web_ui.py) for startup instructions
   - Or read [Web UI README](../uacs-web-ui/README.md)

4. **Read the documentation**:
   - [API Reference](../docs/API_REFERENCE.md) - All v0.3.0 methods
   - [Migration Guide](../docs/MIGRATION.md) - Upgrade from v0.2.0
   - [Hooks Guide](../.claude-plugin/HOOKS_GUIDE.md) - Claude Code integration

---

## 💡 Tips

**Running examples:**
- Each example is self-contained and runnable
- They create a `.demo_state/` directory for storage
- Safe to run multiple times (data persists)

**Learning approach:**
- Read the code - it's heavily commented
- Run the examples to see output
- Modify and experiment
- Check the documentation for deep dives

**Getting help:**
- Examples not working? Check `uv run python --version` (needs 3.11+)
- Import errors? Run `uv sync` to install dependencies
- Questions? See [Contributing Guide](../CONTRIBUTING.md)

---

## 📊 Example Statistics

- **Total examples:** 4 focused examples (vs 13 old files)
- **Total time:** ~15 minutes (vs ~30 minutes for old tutorials)
- **API coverage:** 100% of v0.3.0 semantic API
- **Lines of code:** ~600 lines across all examples
- **Topics covered:** Conversations, knowledge, search, hooks, Web UI

**Philosophy:** Less is more. Four focused examples beat 13 scattered files.

---

**Version:** v0.3.0
**Last Updated:** February 3, 2026
**Maintained By:** UACS Team
