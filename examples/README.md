# UACS Examples and Demos

Welcome to the UACS examples directory! This contains comprehensive demonstrations and code samples showing when, why, and how to use UACS.

## Quick Navigation

### 🚀 Start Here: 5 Core Demos

Follow these demos in order to build understanding progressively:

1. **[01_basic_setup/](./01_basic_setup/)** - Learn the fundamentals (5 min)
2. **[02_context_compression/](./02_context_compression/)** - Save 70% on token costs (5 min)
3. **[03_multi_agent_context/](./03_multi_agent_context/)** - Coordinate multiple agents (5 min)
4. **[04_topic_based_retrieval/](./04_topic_based_retrieval/)** - Focus context with topics (5 min)
5. **[05_claude_code_integration/](./05_claude_code_integration/)** - THE KILLER USE CASE (10 min)

**Total time:** ~30 minutes for complete mastery

### 📚 Additional Examples

- `basic_context.py` - Simple context usage
- `compression_example.py` - Compression demo
- `memory_usage.py` - Memory system
- `package_install.py` - Package management
- `multi_format_translation.py` - Format conversion
- `custom_adapter.py` - Custom adapters
- `mcp_tool_usage.py` - MCP integration

---

## Demo Details

### Demo 1: Basic Setup
**Location:** `01_basic_setup/`

**What you'll learn:**
- Initialize UACS
- Add context entries
- Build compressed context
- Check token statistics

**Files:**
- `README.md` - Full explanation with What/Why/When/How
- `demo.py` - Runnable demonstration
- `output.txt` - Expected output

**Run it:**
```bash
uv run python examples/01_basic_setup/demo.py
```

---

### Demo 2: Context Compression
**Location:** `02_context_compression/`

**What you'll learn:**
- Achieve 70%+ token reduction
- Understand compression strategies
- Calculate real cost savings
- Compare before/after token usage

**Files:**
- `README.md` - Full explanation
- `demo.py` - Runnable demonstration
- `comparison.md` - Side-by-side token analysis

**Key takeaway:** Save $210/month @ 100 calls/day

**Run it:**
```bash
uv run python examples/02_context_compression/demo.py
```

---

### Demo 3: Multi-Agent Context Sharing
**Location:** `03_multi_agent_context/`

**What you'll learn:**
- Share context between agents
- Sequential workflows (Agent 1 → Agent 2 → Agent 3)
- Topic-based routing
- Architecture patterns

**Files:**
- `README.md` - Full explanation
- `demo.py` - 3-agent demonstration
- `architecture.md` - Multi-agent patterns (5 patterns)

**Key takeaway:** Seamless agent coordination, zero manual synchronization

**Run it:**
```bash
uv run python examples/03_multi_agent_context/demo.py
```

---

### Demo 4: Topic-Based Retrieval
**Location:** `04_topic_based_retrieval/`

**What you'll learn:**
- Filter context by topics
- Hierarchical topic taxonomies
- Multi-topic queries
- Scale to 100K+ token contexts

**Files:**
- `README.md` - Full explanation
- `demo.py` - 4-topic demonstration
- `use_cases.md` - Real-world topic patterns

**Key takeaway:** 50-80% token reduction with topic filtering

**Run it:**
```bash
uv run python examples/04_topic_based_retrieval/demo.py
```

---

### Demo 5: Claude Code Integration - THE KILLER USE CASE
**Location:** `05_claude_code_integration/`

**What you'll learn:**
- How Claude Code could integrate UACS
- Perfect fidelity vs. lossy summarization
- Production integration architecture
- 3-month implementation roadmap

**Files:**
- `README.md` - Full explanation
- `demo.py` - Proof of concept
- `DESIGN.md` - Complete integration design (15 pages!)

**Key takeaway:** 100% fidelity vs. 60% (summarization). Never lose conversation details again.

**Run it:**
```bash
uv run python examples/05_claude_code_integration/demo.py
```

---

## Quick Start

```bash
# Run all demos
for demo in 01_basic_setup 02_context_compression 03_multi_agent_context 04_topic_based_retrieval 05_claude_code_integration; do
    echo "Running $demo..."
    uv run python examples/$demo/demo.py
    echo ""
done
```

**Expected runtime:** ~10 seconds total

---

## Learning Paths

### Path 1: New to UACS
```
Demo 1 → Demo 2 → Demo 3 → Demo 4 → Demo 5
(Complete understanding in 30 minutes)
```

### Path 2: Evaluating UACS
```
Demo 2 → Demo 5
(See cost savings + killer use case in 15 minutes)
```

### Path 3: Specific Use Case

| Your Goal | Start With |
|-----------|-----------|
| Reduce costs | Demo 2, Demo 4 |
| Multi-agent system | Demo 3, Demo 1 |
| Claude Code integration | Demo 5, then all |
| Large project context | Demo 4, Demo 2 |

---

## What You'll Learn

### Core Concepts (Demo 1)
- UACS initialization
- Context entries
- Compression basics
- Token statistics

### Cost Optimization (Demo 2)
- 70% token reduction
- Deduplication
- Quality filtering
- Cost calculations

### Agent Coordination (Demo 3)
- Shared context
- Topic routing
- Sequential workflows
- Architecture patterns

### Focused Retrieval (Demo 4)
- Topic filtering
- Hierarchical topics
- Multi-topic queries
- Massive context scaling

### Production Integration (Demo 5)
- Perfect fidelity
- Summarization problems
- Integration architecture
- Implementation roadmap

---

## File Structure

```
examples/
├── README.md (this file)
│
├── 01_basic_setup/
│   ├── README.md (What/Why/When/How)
│   ├── demo.py (runnable code)
│   └── output.txt (expected output)
│
├── 02_context_compression/
│   ├── README.md
│   ├── demo.py
│   └── comparison.md (before/after analysis)
│
├── 03_multi_agent_context/
│   ├── README.md
│   ├── demo.py
│   └── architecture.md (5 patterns)
│
├── 04_topic_based_retrieval/
│   ├── README.md
│   ├── demo.py
│   └── use_cases.md (real-world examples)
│
├── 05_claude_code_integration/
│   ├── README.md
│   ├── demo.py
│   └── DESIGN.md (15-page integration design)
│
└── [additional examples]
    ├── basic_context.py
    ├── compression_example.py
    ├── memory_usage.py
    └── ...
```

---

## Success Metrics

After completing all demos, you will be able to:

✅ Initialize and use UACS in any project
✅ Achieve 70%+ token compression
✅ Build multi-agent systems with shared context
✅ Use topic filtering for focused retrieval
✅ Understand the Claude Code integration opportunity
✅ Design production UACS integrations

---

## Next Steps

1. **Run the demos** - Start with Demo 1
2. **Read [docs/DEMOS.md](../docs/DEMOS.md)** - Complete guide with learning paths
3. **Try in your project** - Integrate UACS
4. **Join community** - Share your use case

---

## Support

- **Documentation:** [docs/](../docs/)
- **API Reference:** [docs/LIBRARY_GUIDE.md](../docs/LIBRARY_GUIDE.md)
- **Integration Guides:** [docs/INTEGRATIONS.md](../docs/INTEGRATIONS.md)
- **GitHub Issues:** [Report bugs or request features](https://github.com/kylebrodeur/universal-agent-context/issues)

---

## Quick Reference

| Demo | Time | Complexity | Key Value |
|------|------|-----------|-----------|
| Demo 1 | 5 min | ⭐ | Foundation |
| Demo 2 | 5 min | ⭐⭐ | 70% cost savings |
| Demo 3 | 5 min | ⭐⭐⭐ | Agent coordination |
| Demo 4 | 5 min | ⭐⭐⭐ | Focused retrieval |
| Demo 5 | 10 min | ⭐⭐⭐⭐ | Perfect fidelity |

**Start now:**
```bash
uv run python examples/01_basic_setup/demo.py
```

---

**Have fun exploring UACS!** 🚀
