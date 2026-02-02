# UACS Quick Start Guide

Get UACS up and running in 5 minutes!

---

## Installation

### 1. Install UACS

```bash
# Using uv (recommended)
uv pip install universal-agent-context

# Or using pip
pip install universal-agent-context
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

## Quick Test (No Claude Code)

Test UACS basic functionality:

```python
from uacs import UACS

# Initialize
uacs = UACS()

# Add context
uacs.add_to_context(
    key="test_entry",
    content="Implemented JWT authentication with bcrypt password hashing",
    topics=["security", "authentication"],
    metadata={"agent": "claude"}
)

# Retrieve context
context = uacs.shared_context.get_compressed_context(max_tokens=1000)
print(context)

# Get stats
stats = uacs.shared_context.get_stats()
print(f"Entries: {stats['entry_count']}")
print(f"Tokens: {stats['total_tokens']}")
print(f"Compression: {stats['compression_ratio']}")
```

---

## Claude Code Integration

### Setup (One-Time)

**1. Install Claude Code Plugin:**

```bash
# Copy plugin configuration
cp .claude-plugin/plugin-proactive.json ~/.claude/plugin.json

# Copy hook scripts
mkdir -p ~/.claude/hooks
cp .claude-plugin/hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py
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

### 1. Explore Package Manager

```bash
# Install packages from GitHub
uacs install username/repo

# List installed
uacs list

# Validate before installing
uacs validate username/repo
```

### 2. Try Agent Skills

```python
from uacs.adapters.agent_skill_adapter import AgentSkillAdapter

# Discover skills
adapters = AgentSkillAdapter.discover_skills()

# Get as system prompt
for adapter in adapters:
    if adapter.parsed:
        print(adapter.to_system_prompt())
```

### 3. Build Custom Visualization

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

### 4. Read Full Documentation

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
