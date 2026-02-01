# UACS Demos and Examples

This document provides an overview of all UACS demonstrations, a recommended learning path, and cross-references to help you understand when and how to use each feature.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Learning Path](#learning-path)
3. [Demo Overview](#demo-overview)
4. [Demo Descriptions](#demo-descriptions)
5. [Use Case Matrix](#use-case-matrix)
6. [Running the Demos](#running-the-demos)
7. [Additional Resources](#additional-resources)

---

## Quick Start

**New to UACS?** Start here:

```bash
# Run all demos in sequence (recommended for first-time users)
uv run python examples/01_basic_setup/demo.py
uv run python examples/02_context_compression/demo.py
uv run python examples/03_multi_agent_context/demo.py
uv run python examples/04_topic_based_retrieval/demo.py
uv run python examples/05_claude_code_integration/demo.py

# Or jump to a specific demo
uv run python examples/<demo_name>/demo.py
```

**Total time:** ~15 minutes to run all demos

---

## Learning Path

Follow this recommended path to build understanding progressively:

### Path 1: Developer Learning UACS (Recommended)

```
Demo 1: Basic Setup
    ↓
    Learn: Core UACS workflow, initialization, context entries
    Time: 5 minutes
    ↓
Demo 2: Context Compression
    ↓
    Learn: 70% token savings, cost optimization
    Time: 5 minutes
    ↓
Demo 3: Multi-Agent Context
    ↓
    Learn: Agent coordination, context sharing
    Time: 5 minutes
    ↓
Demo 4: Topic-Based Retrieval
    ↓
    Learn: Focused context, topic filtering
    Time: 5 minutes
    ↓
Demo 5: Claude Code Integration
    ↓
    Learn: The killer use case, production integration
    Time: 10 minutes
```

**Total:** ~30 minutes for complete understanding

### Path 2: Quick Evaluation (If You're in a Hurry)

```
1. Demo 2: Context Compression (see the savings)
2. Demo 5: Claude Code Integration (see the value)
```

**Total:** ~15 minutes

### Path 3: Specific Use Case

| Your Use Case | Start With | Then See |
|--------------|-----------|----------|
| Reduce API costs | Demo 2 | Demo 4 |
| Build multi-agent system | Demo 3 | Demo 1, Demo 4 |
| Integrate with Claude Code | Demo 5 | Demo 1, Demo 2 |
| Large project context | Demo 4 | Demo 2 |
| General exploration | Demo 1 | All demos in order |

---

## Demo Overview

| Demo | Focus | Key Takeaway | Time | Difficulty |
|------|-------|--------------|------|-----------|
| **01_basic_setup** | Fundamentals | Core UACS workflow | 5 min | Beginner |
| **02_context_compression** | Cost savings | 70% token reduction | 5 min | Beginner |
| **03_multi_agent_context** | Coordination | Seamless agent collaboration | 5 min | Intermediate |
| **04_topic_based_retrieval** | Precision | Focused context filtering | 5 min | Intermediate |
| **05_claude_code_integration** | Production | Perfect conversation fidelity | 10 min | Advanced |

---

## Demo Descriptions

### Demo 1: Basic Setup

**Location:** `examples/01_basic_setup/`

**What You'll Learn:**
- Initializing UACS for a project
- Adding context entries
- Building compressed context
- Checking token statistics

**Why This Matters:**
This is the foundation. Every UACS feature builds on these basic operations.

**Key Concepts:**
- Shared context
- Context entries
- Compression
- Token counting

**Files:**
- `README.md` - Detailed walkthrough
- `demo.py` - Runnable example
- `output.txt` - Expected output

**Next Demo:** Demo 2 (Context Compression)

---

### Demo 2: Context Compression

**Location:** `examples/02_context_compression/`

**What You'll Learn:**
- Achieving 70%+ token savings
- Compression strategies (deduplication, quality filtering, topic filtering)
- Real-world cost calculations
- Before/after token comparisons

**Why This Matters:**
Token costs add up fast in production. This demo shows how to save 70%+ without losing information.

**Key Concepts:**
- Deduplication
- Quality scoring
- Compression ratios
- Cost savings

**Files:**
- `README.md` - Detailed walkthrough
- `demo.py` - Runnable example
- `comparison.md` - Side-by-side token analysis

**ROI Example:**
- Before: $300/month @ 100 calls/day
- After: $90/month
- Savings: $210/month (70%)

**Next Demo:** Demo 3 (Multi-Agent Context) or Demo 4 (Topic-Based Retrieval)

---

### Demo 3: Multi-Agent Context Sharing

**Location:** `examples/03_multi_agent_context/`

**What You'll Learn:**
- Sharing context between multiple agents
- Sequential workflows (Agent 1 → Agent 2 → Agent 3)
- Topic-based routing per agent
- Cost savings in multi-agent systems

**Why This Matters:**
Multi-agent systems require coordination. UACS provides a shared memory layer that eliminates manual synchronization.

**Key Concepts:**
- Shared context
- Agent coordination
- Topic routing
- Sequential pipelines

**Files:**
- `README.md` - Detailed walkthrough
- `demo.py` - Runnable example (3 agents)
- `architecture.md` - Multi-agent patterns

**Architecture Patterns:**
- Sequential Pipeline
- Parallel Specialists
- Hierarchical Coordination
- Iterative Refinement
- Broadcast-Gather

**Next Demo:** Demo 4 (Topic-Based Retrieval)

---

### Demo 4: Topic-Based Retrieval

**Location:** `examples/04_topic_based_retrieval/`

**What You'll Learn:**
- Topic-based filtering for focused context
- Hierarchical topic taxonomies
- Multi-topic queries
- Scaling to massive contexts (100K+ tokens)

**Why This Matters:**
Large contexts contain noise. Topic filtering gives you exactly what you need, reducing tokens by 50-80%.

**Key Concepts:**
- Topic filtering
- Hierarchical topics
- Focused retrieval
- Massive context scaling

**Files:**
- `README.md` - Detailed walkthrough
- `demo.py` - Runnable example (4 topics)
- `use_cases.md` - Real-world topic patterns

**Use Cases:**
- Software development (security, performance, testing)
- Customer support (billing, technical, escalation)
- Content creation (research, draft, review, publish)
- Data analysis (collection, analysis, visualization)

**Next Demo:** Demo 5 (Claude Code Integration)

---

### Demo 5: Claude Code Integration - THE KILLER USE CASE

**Location:** `examples/05_claude_code_integration/`

**What You'll Learn:**
- How Claude Code could integrate UACS
- Perfect conversation fidelity (vs. lossy summarization)
- Topic-based conversation retrieval
- Production integration architecture

**Why This Matters:**
This is THE killer use case. Claude Code (and other AI CLIs) currently use summarization, which loses details. UACS provides perfect fidelity through compression + topic-based retrieval.

**Key Concepts:**
- Conversation compaction
- Perfect fidelity
- Summarization loss
- Production integration

**Files:**
- `README.md` - Detailed walkthrough
- `demo.py` - Proof of concept
- `DESIGN.md` - Complete integration design (15 pages)

**Value Proposition:**
- **Fidelity:** 100% vs. 60% (summarization)
- **User Experience:** "Claude remembers everything"
- **Cost:** Comparable (compression offsets storage)
- **Competitive Advantage:** Unique feature

**Integration Phases:**
1. Phase 1: Passive storage (2 weeks)
2. Phase 2: Active retrieval (4 weeks)
3. Phase 3: Intelligent topics (4 weeks)
4. Phase 4: Advanced features (2 weeks)

**This is the demo to show decision-makers.**

---

## Use Case Matrix

### When to Use Each Feature

| Feature | Use When | Demo | Cost Impact | Complexity |
|---------|----------|------|-------------|-----------|
| **Basic Context** | Starting with UACS | Demo 1 | Neutral | Low |
| **Compression** | Reducing API costs | Demo 2 | -70% | Low |
| **Multi-Agent** | Building agent systems | Demo 3 | -50% | Medium |
| **Topic Filtering** | Large/multi-topic contexts | Demo 4 | -80% | Medium |
| **Claude Code Integration** | Perfect conversation fidelity | Demo 5 | Varies | High |

### By Project Type

| Project Type | Recommended Demos | Key Features |
|-------------|------------------|--------------|
| **Single Agent** | 1, 2, 4 | Compression, Topics |
| **Multi-Agent System** | 1, 2, 3, 4 | All features |
| **Cost Optimization** | 2, 4 | Compression, Topics |
| **Long-Running Project** | 1, 2, 4 | Compression, Topics, History |
| **AI CLI Integration** | 5, then 1-4 | Full integration |

### By Team Size

| Team Size | Focus | Demos |
|-----------|-------|-------|
| **Solo Developer** | Cost, simplicity | 1, 2, 4 |
| **Small Team (2-5)** | Coordination, cost | 1, 2, 3, 4 |
| **Large Team (6+)** | Integration, scale | All demos, especially 3, 5 |

---

## Running the Demos

### Prerequisites

```bash
# Install UACS
cd universal-agent-context
uv sync  # Or: pip install -e .

# Verify installation
uv run uacs --version
```

### Running Individual Demos

```bash
# From project root
uv run python examples/01_basic_setup/demo.py
uv run python examples/02_context_compression/demo.py
uv run python examples/03_multi_agent_context/demo.py
uv run python examples/04_topic_based_retrieval/demo.py
uv run python examples/05_claude_code_integration/demo.py
```

### Running All Demos

```bash
# Bash script to run all demos
for demo in 01_basic_setup 02_context_compression 03_multi_agent_context 04_topic_based_retrieval 05_claude_code_integration; do
    echo "Running $demo..."
    uv run python examples/$demo/demo.py
    echo ""
done
```

### Expected Runtime

- Demo 1: ~1 second
- Demo 2: ~2 seconds
- Demo 3: ~2 seconds
- Demo 4: ~2 seconds
- Demo 5: ~2 seconds

**Total:** ~10 seconds for all demos

### Troubleshooting

**Issue:** `ImportError: No module named 'uacs'`
```bash
# Solution: Install UACS
uv sync
```

**Issue:** `Permission denied` when creating `.demo_state/`
```bash
# Solution: Run from project root
cd /path/to/universal-agent-context
uv run python examples/01_basic_setup/demo.py
```

**Issue:** Demo output differs from expected
```bash
# Solution: This is normal - token counts may vary slightly
# As long as the demo runs without errors, you're good
```

---

## Additional Resources

### Documentation

- [README.md](../README.md) - Project overview
- [LIBRARY_GUIDE.md](./LIBRARY_GUIDE.md) - Complete API reference
- [CLI_REFERENCE.md](./CLI_REFERENCE.md) - Command-line interface
- [CONTEXT.md](./CONTEXT.md) - Context management deep dive
- [ADAPTERS.md](./ADAPTERS.md) - Format translation
- [PACKAGES.md](./PACKAGES.md) - Package management

### Integration Guides

- [Claude Desktop](./integrations/CLAUDE_DESKTOP.md) - Claude Desktop integration
- [Cursor](./integrations/CURSOR.md) - Cursor IDE integration
- [Windsurf](./integrations/WINDSURF.md) - Windsurf integration
- [All Integrations](./INTEGRATIONS.md) - Overview

### Example Code

All examples are in [`examples/`](../examples/):
- `basic_context.py` - Simple usage
- `compression_example.py` - Compression demo
- `memory_usage.py` - Memory system
- `package_install.py` - Package management
- `custom_adapter.py` - Format translation

### Community

- GitHub Issues: [Report bugs or request features](https://github.com/kylebrodeur/universal-agent-context/issues)
- Discussions: Share use cases and ask questions
- Contributing: See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Demo Comparison Table

### Feature Coverage

| Feature | Demo 1 | Demo 2 | Demo 3 | Demo 4 | Demo 5 |
|---------|--------|--------|--------|--------|--------|
| Context entries | ✅ | ✅ | ✅ | ✅ | ✅ |
| Compression | ✅ | ✅ | ✅ | ✅ | ✅ |
| Token statistics | ✅ | ✅ | ✅ | ✅ | ✅ |
| Topics | ⚠️ | ⚠️ | ✅ | ✅ | ✅ |
| Multi-agent | ❌ | ❌ | ✅ | ❌ | ❌ |
| Topic filtering | ❌ | ⚠️ | ✅ | ✅ | ✅ |
| Cost analysis | ⚠️ | ✅ | ✅ | ✅ | ✅ |
| Production integration | ❌ | ❌ | ❌ | ❌ | ✅ |

Legend: ✅ Core focus | ⚠️ Mentioned | ❌ Not covered

### Complexity Progression

```
Demo 1: Basic Setup
  Complexity: ⭐ (Simple)
  Prerequisites: None
  Time: 5 minutes

Demo 2: Context Compression
  Complexity: ⭐⭐ (Moderate)
  Prerequisites: Demo 1
  Time: 5 minutes

Demo 3: Multi-Agent Context
  Complexity: ⭐⭐⭐ (Intermediate)
  Prerequisites: Demo 1, Demo 2
  Time: 5 minutes

Demo 4: Topic-Based Retrieval
  Complexity: ⭐⭐⭐ (Intermediate)
  Prerequisites: Demo 1, Demo 2
  Time: 5 minutes

Demo 5: Claude Code Integration
  Complexity: ⭐⭐⭐⭐ (Advanced)
  Prerequisites: All previous demos
  Time: 10 minutes
```

---

## FAQ

### Q: Do I need to run the demos in order?

**A:** Recommended but not required. Each demo is self-contained, but they build on each other conceptually.

### Q: Can I modify the demos?

**A:** Absolutely! The demos are meant to be educational. Modify them to explore features or test your use cases.

### Q: How do I integrate UACS into my project?

**A:** Start with Demo 1 to understand basics, then see Demo 5 for integration patterns. Check [LIBRARY_GUIDE.md](./LIBRARY_GUIDE.md) for complete API reference.

### Q: What if a demo fails?

**A:** Check troubleshooting section above. If issues persist, file a GitHub issue with the error message.

### Q: Are there more examples?

**A:** Yes! See [`examples/`](../examples/) directory for additional code samples beyond the 5 main demos.

### Q: Can I use UACS in production?

**A:** Yes! UACS is production-ready. See Demo 5 for integration considerations and [LAUNCH_STRATEGY.md](./LAUNCH_STRATEGY.md) for roadmap.

---

## Conclusion

**Start here:** Demo 1 (Basic Setup)
**Most impactful:** Demo 2 (Context Compression) and Demo 5 (Claude Code Integration)
**Most technical:** Demo 3 (Multi-Agent Context) and Demo 4 (Topic-Based Retrieval)

**Total learning time:** 30 minutes for all demos
**Total value:** Unlimited (70% cost savings + perfect context fidelity)

**Ready to start?**
```bash
uv run python examples/01_basic_setup/demo.py
```

---

**Document Version:** 1.0
**Last Updated:** 2025-01-31
**Related:** [README.md](../README.md), [LIBRARY_GUIDE.md](./LIBRARY_GUIDE.md)
