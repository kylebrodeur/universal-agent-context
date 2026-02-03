# UACS Quick Start Guide

Get UACS up and running in 5 minutes!

**v0.3.0 Update:** This guide now includes semantic API examples for structured conversation tracking and knowledge extraction.

---

## Installation

### 1. Install UACS

```bash
# Using uv (recommended)
uv pip install universal-agent-context

# Or using pip
pip install universal-agent-context

# Initialize project storage
uacs context init   # Creates .state/context/
uacs memory init    # Creates .state/memory/
```

### 2. Install Optional Dependencies

**For Local LLM Tagging (Recommended):**
```bash
# Install transformers + torch for embedded LLM
pip install transformers torch

# Model will auto-download on first use (~2GB)
# Or pre-download: python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0')"
```

**For Visualization (Optional):**
```bash
pip install uvicorn fastapi
```

---

## Quick Test - v0.3.0 Semantic API

Test UACS with the new semantic API:

```python
from uacs import UACS
from pathlib import Path

# Initialize with project path
uacs = UACS(project_path=Path("."))

# Track a conversation
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
    tokens_out=156,
    model="claude-sonnet-4"
)

# Capture a decision
decision = uacs.add_decision(
    question="Which auth method should we use?",
    decision="JWT tokens",
    rationale="Stateless, scalable, works with microservices",
    session_id="session_001",
    alternatives=["Session-based", "OAuth2"]
)

# Add a convention
convention = uacs.add_convention(
    content="We always use httpOnly cookies for JWT storage",
    topics=["security", "auth"],
    source_session="session_001"
)

# Search semantically
results = uacs.search("how did we implement authentication?", limit=5)
for result in results:
    print(f"[{result.metadata['type']}] {result.text[:80]}...")
    print(f"Relevance: {result.similarity:.2f}\n")

# Get statistics
stats = uacs.get_stats()
print(f"Conversations: {stats['semantic']['conversations']}")
print(f"Knowledge: {stats['semantic']['knowledge']}")
print(f"Embeddings: {stats['semantic']['embeddings']}")
```

### Legacy API (v0.2.x - Deprecated)

The old API still works but shows deprecation warnings:

```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path("."))

# OLD API (deprecated, but works)
uacs.add_to_context(
    key="test_entry",
    content="Implemented JWT authentication",
    topics=["security", "authentication"]
)

# Get context (v0.2.0 method)
context = uacs.shared_context.get_compressed_context(max_tokens=1000)
print(context)
```

See [Migration Guide](docs/MIGRATION.md) for upgrading from v0.2.x to v0.3.0.

---

## Claude Code Integration

### v0.3.0 Semantic Plugin Setup

**1. Install Semantic Plugin:**

```bash
# Copy semantic plugin configuration (v0.3.0)
cp .claude-plugin/plugin-semantic.json ~/.claude/plugin.json

# Copy hook scripts
mkdir -p ~/.claude/hooks
cp .claude-plugin/hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py

# Optional: Install transformers for better topic extraction
pip install transformers torch
```

**What's New in v0.3.0 Plugin:**
- 📝 **UserPromptSubmit Hook**: Captures user messages with topic extraction
- 🔧 **PostToolUse Hook**: Tracks tool executions (Edit, Bash, Read, etc.)
- 🧠 **SessionEnd Hook**: Extracts decisions and conventions from conversations
- 🔍 **Semantic Search**: All captured data is indexed with embeddings

**v0.2.0 Plugin (Proactive Compaction):**

If you prefer the proactive compaction plugin without semantic capture:

```bash
# Copy proactive plugin configuration (v0.2.0)
cp .claude-plugin/plugin-proactive.json ~/.claude/plugin.json
```

**2. Verify Installation:**

```bash
# Check hooks are executable
ls -la ~/.claude/hooks/

# You should see:
# uacs_inject_context.py
# uacs_monitor_context.py
# uacs_precompact.py
# uacs_store.py
# uacs_store_realtime.py
# uacs_tag_prompt.py
```

### Test Basic Plugin

**1. Start Claude Code:**

```bash
cd your-project
claude
```

**2. Have a Conversation:**

```
User: Help me implement user authentication

Claude: [responds and uses tools]

User: Create tests for the auth system

Claude: [creates tests, runs pytest]

User: exit
```

**3. Check Stored Context:**

```bash
# View stored sessions
ls .state/context/

# You should see:
# - claude_code_session_*.json (session data)
# - sessions.jsonl (trace storage)
# - events.jsonl (event storage)
```

### Test Proactive Compaction Prevention

**1. Have a Long Conversation:**

```bash
claude

User: Read the entire codebase and explain the architecture
# [Paste large code files]

User: Now create comprehensive documentation
# [Continue with many prompts]
```

**2. Watch for Early Compression:**

You should see messages like:
```
⚙️ UACS Context Management

Context window usage reached 52.3% - triggered early compression.

Archived 15/42 conversation turns to UACS storage.
All history preserved with perfect fidelity.

You can continue working without hitting compaction threshold (75%).
```

**3. Verify Prevention:**

```bash
# Check if compaction was prevented
grep "prevented_compaction" .state/context/events.jsonl

# Should see: "prevented_compaction": true
```

### Test Local LLM Tagging

**1. Verify Transformers Installed:**

```python
python -c "import transformers; print('✅ Transformers installed')"
```

**2. First Prompt (Model Downloads):**

The first time you use UACS, TinyLlama will download (~2GB):

```bash
claude

User: Fix the SQL injection vulnerability in auth.py

# Behind the scenes:
# - Model downloads (first time only, ~2 minutes)
# - Tags prompt with: ["security", "bug-fix", "database"]
```

**3. Subsequent Prompts (Fast):**

```bash
User: Add unit tests for the auth fix

# Model is cached in RAM
# Tags prompt in ~100-200ms
# Topics: ["testing", "security"]
```

### Query Semantic Context (v0.3.0)

After using the semantic plugin, you can query captured context:

```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path("."))

# Natural language search
results = uacs.search("how did we implement authentication?", limit=10)
for result in results:
    print(f"\n[{result.metadata['type']}]")
    print(f"Content: {result.text[:200]}...")
    print(f"Relevance: {result.similarity:.2f}")
    print(f"Session: {result.metadata.get('session_id', 'N/A')}")

# Type-specific search
decisions = uacs.search("authentication", types=["decision"], limit=5)
conventions = uacs.search("coding standards", types=["convention"], limit=5)
tools = uacs.search("file edits", types=["tool_use"], limit=10)

# Session-specific search
session_context = uacs.search(
    "what happened in this session?",
    session_id="session_001",
    limit=20
)

# Get statistics
stats = uacs.get_stats()
print(f"\nCaptured Data:")
print(f"  User messages: {stats['semantic']['conversations'].get('user_messages', 0)}")
print(f"  Tool uses: {stats['semantic']['conversations'].get('tool_uses', 0)}")
print(f"  Decisions: {stats['semantic']['knowledge'].get('decisions', 0)}")
print(f"  Conventions: {stats['semantic']['knowledge'].get('conventions', 0)}")
```

---

## MCP Server Integration

### Start MCP Server

```bash
# Option 1: Run directly
uacs serve

# Option 2: Run with Claude Code
# Add to ~/.claude/mcp_servers.json:
{
  "uacs": {
    "command": "uacs",
    "args": ["serve"],
    "description": "UACS context retrieval"
  }
}
```

### Test MCP Tools

```bash
claude --mcp-server uacs

User: Use uacs_search_context to find conversations about "authentication"

Claude: [calls MCP tool]
# Returns: Stored conversations with "authentication" topic

User: Use uacs_list_topics to see all topics

Claude: [calls MCP tool]
# Returns: ["security", "testing", "performance", ...]
```

---

## Visualization Dashboard

### Start Visualization Server

```bash
# Terminal 1: Start server
python examples/quickstart/visualization_demo.py

# Terminal 2: Open browser
open http://localhost:8081
```

### What You'll See

1. **Session List** - All Claude Code sessions
2. **Token Dashboard** - Real-time token usage
3. **Topic Clusters** - Topic-based visualization
4. **Quality Distribution** - Content quality metrics

---

## Common Issues & Solutions

### Issue: Hooks Not Firing

**Symptom:** No files in `.state/context/`

**Solution:**
```bash
# 1. Check plugin is loaded
cat ~/.claude/plugin.json

# 2. Check hooks are executable
ls -la ~/.claude/hooks/*.py
chmod +x ~/.claude/hooks/*.py

# 3. Check Claude Code version
claude --version
# Requires: claude-code >= 0.1.0
```

### Issue: Transformers Not Working

**Symptom:** "UACS: Ollama not running, tagging skipped" (even with transformers)

**Solution:**
```bash
# Verify transformers installed
pip install transformers torch

# Test model loading
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0')"

# Check hook logs
# The hook should say "Tagged with X topics" not "Ollama not running"
```

### Issue: Model Download Slow

**Symptom:** First prompt takes 5+ minutes

**Solution:**
```bash
# Pre-download model
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; AutoModelForCausalLM.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0'); AutoTokenizer.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0')"

# This downloads ~2GB once
# Subsequent uses are instant (cached)
```

### Issue: High Memory Usage

**Symptom:** RAM usage jumps by 2-3GB

**Solution:**
```bash
# This is normal! TinyLlama loads into RAM for fast inference
# Memory usage: ~2GB (model) + ~500MB (overhead) = ~2.5GB
# If this is too much, disable local LLM tagging:

# Edit ~/.claude/plugin.json:
{
  "configuration": {
    "local_llm_tagging_enabled": false
  }
}

# Falls back to heuristic tagging (still works, but lower quality)
```

---

## Next Steps

### 1. Learn the Semantic API (v0.3.0)

```bash
# Read the complete API reference
cat docs/API_REFERENCE.md

# Or view online
open https://github.com/kylebrodeur/universal-agent-context/blob/main/docs/API_REFERENCE.md
```

**Key methods to learn:**
- `add_user_message()` - Track user prompts
- `add_decision()` - Capture architectural decisions
- `add_convention()` - Store project conventions
- `search()` - Natural language queries

### 2. Migrate from v0.2.x (If Upgrading)

```bash
# Read the migration guide
cat docs/MIGRATION.md

# Key changes:
# - add_to_context() → structured methods
# - Topic search → semantic search
# - Generic context → typed knowledge
```

**Migration resources:**
- [Migration Guide](docs/MIGRATION.md) - Complete upgrade instructions
- [API Reference](docs/API_REFERENCE.md) - New method documentation
- [Hooks Guide](.claude-plugin/HOOKS_GUIDE.md) - Plugin updates

### 3. Explore Package Manager

```bash
# Install packages from GitHub
uacs packages install username/repo

# List installed
uacs packages list

# Validate before installing
uacs packages validate username/repo
```

### 4. Try Agent Skills

```python
from uacs.adapters.agent_skill_adapter import AgentSkillAdapter

# Discover skills
adapters = AgentSkillAdapter.discover_skills()

# Get as system prompt
for adapter in adapters:
    if adapter.parsed:
        print(adapter.to_system_prompt())
```

### 5. Build Custom Visualization

```python
from uacs.visualization.web_server import VisualizationServer
from uacs.context.shared_context import SharedContextManager

# Create context manager
manager = SharedContextManager()

# Add your data
manager.add_entry("Implemented feature X", agent="claude", topics=["feature"])

# Start server
server = VisualizationServer(manager)
# Visit http://localhost:8081
```

### 6. Read Full Documentation

**v0.3.0 Documentation:**
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Migration Guide](docs/MIGRATION.md) - Upgrade from v0.2.x
- [Hooks Guide](.claude-plugin/HOOKS_GUIDE.md) - Semantic hooks explained

**v0.2.0 Documentation:**
- [Plugin Evolution](./.github/PLUGIN_EVOLUTION.md) - Compare plugin versions
- [Compaction Prevention](./.github/COMPACTION_PREVENTION_STRATEGY.md) - How it works
- [Skill Suggestion System](./.github/SKILL_SUGGESTION_SYSTEM.md) - Workflow learning
- [Trace Visualization](./.github/TRACE_VISUALIZATION_DESIGN.md) - LangSmith-style traces

---

## Performance Expectations

### With Basic Plugin (SessionEnd Only)

- Overhead: Negligible (~0ms per prompt)
- Crash resistance: ❌ No
- Context injection: ❌ No
- Compaction prevention: ❌ No

### With Enhanced Plugin (4 Hooks)

- Overhead: ~50ms per prompt
- Crash resistance: ✅ Yes (real-time storage)
- Context injection: ✅ Yes (on resume)
- Compaction prevention: ⚠️ Reactive only

### With Proactive Plugin (6 Hooks + Local LLM)

- Overhead: ~250ms per prompt
  - Monitor: ~100ms
  - LLM tag: ~150ms
- Crash resistance: ✅ Yes
- Context injection: ✅ Yes
- Compaction prevention: ✅ Yes (95%+ success)
- Topic quality: ⭐⭐⭐⭐⭐ (LLM-based)

**Recommendation:** Start with Enhanced, upgrade to Proactive once comfortable.

---

## Getting Help

- **Issues:** https://github.com/kylebrodeur/universal-agent-context/issues
- **Discussions:** https://github.com/kylebrodeur/universal-agent-context/discussions
- **Email:** kyle@example.com

Happy building with UACS! 🚀
