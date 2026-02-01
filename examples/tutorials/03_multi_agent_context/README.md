# Demo 3: Multi-Agent Context Sharing

## What

This demo shows how multiple AI agents can share context through UACS without manual synchronization. You'll see:

- Two agents (Claude and Gemini) working on the same project
- Agent 1 adds code review notes to shared context
- Agent 2 retrieves and builds on those notes
- Automatic context synchronization
- No repeated explanations needed

This demonstrates UACS as a **context middleware layer** between agents.

## Why

**Value Proposition:** In multi-agent systems, context sharing is typically:
- Manual and error-prone (copy-paste between conversations)
- Incomplete (summarization loses details)
- Expensive (repeated context in every agent call)
- Time-consuming (explaining the same thing multiple times)

**UACS solves this by providing a shared memory layer:**
- One agent writes → All agents can read
- Automatic deduplication
- Compression applied once, used everywhere
- Topic-based filtering per agent

**Real-world Impact:**
- Save time on agent handoffs
- Reduce token costs in multi-agent systems
- Enable complex workflows with specialized agents
- Maintain context continuity across agent boundaries

## When

Use multi-agent context sharing when:
- Building systems with multiple specialized agents
- Handing off tasks between agents (e.g., researcher → writer → reviewer)
- Running parallel agents on different aspects of a problem
- Coordinating agents from different LLM providers (Claude + Gemini + GPT)

**Examples:**
- Software development: Architect → Coder → Reviewer → Tester
- Content creation: Researcher → Writer → Editor → SEO optimizer
- Data analysis: Data collector → Analyst → Visualizer → Reporter
- Customer support: Classifier → Handler → Escalation → Follow-up

## How

### Architecture

```
Agent 1 (Claude)              Agent 2 (Gemini)
     |                              |
     | write context                | read context
     v                              v
  ┌──────────────────────────────────────┐
  │      UACS Shared Context             │
  │  - Deduplication                     │
  │  - Topic tagging                     │
  │  - Quality scoring                   │
  │  - Compression                       │
  └──────────────────────────────────────┘
           ^                    ^
           |                    |
     Agent 3 (GPT)         Agent 4 (Custom)
```

### Workflow Example

1. **Agent 1 (Security Reviewer)** analyzes code:
   ```python
   uacs.add_to_context(
       key="security-agent",
       content="Found SQL injection vulnerability at line 42",
       topics=["security", "finding"]
   )
   ```

2. **Agent 2 (Code Fixer)** retrieves findings:
   ```python
   context = uacs.build_context(
       query="Fix security issues",
       agent="code-fixer",
       topics=["security", "finding"]
   )
   # Context includes Agent 1's findings automatically
   ```

3. **Agent 2** adds fix:
   ```python
   uacs.add_to_context(
       key="code-fixer",
       content="Fixed SQL injection using parameterized query",
       topics=["security", "fix"]
   )
   ```

4. **Agent 3 (Verifier)** checks the fix:
   ```python
   context = uacs.build_context(
       query="Verify security fixes",
       agent="verifier",
       topics=["security"]  # Gets both findings and fixes
   )
   ```

### Key Benefits

1. **Automatic Synchronization:**
   - No manual context passing
   - No risk of forgetting to share information
   - Real-time updates available to all agents

2. **Cost Efficiency:**
   - Compression applied once
   - Each agent gets only relevant context
   - No duplicate token costs

3. **Topic-Based Routing:**
   - Security agent sees security context
   - Performance agent sees performance context
   - Coordination agent sees all context

4. **Provider Independence:**
   - Works with any LLM (Claude, GPT, Gemini, etc.)
   - Agents don't need to know about each other
   - Common format across providers

## Output

Running this demo produces:

```
Agent 1 (Security Reviewer) analyzing code...
Added 3 security findings to shared context

Agent 2 (Code Fixer) retrieving context...
Retrieved context: 234 tokens
Found 3 issues to fix:
  - SQL injection (line 42)
  - Weak passwords (line 78)
  - Predictable tokens (line 156)

Agent 2 fixing issues...
Added 3 fixes to shared context

Agent 3 (Verifier) checking fixes...
Retrieved context: 345 tokens
Verified 3 fixes successfully

Context Statistics:
  Total entries: 7 (3 findings + 3 fixes + 1 summary)
  Total tokens: 892
  Avg per agent: 297 tokens (67% compression)
  Cost savings: $0.006/call × 3 agents = $0.018 saved
```

## What You Learned

1. **Shared Context is Simple:**
   - Same API for all agents
   - Write once, read from anywhere
   - No coordination code needed

2. **Topic-Based Routing Works:**
   - Each agent filters by relevant topics
   - Reduces noise and cost
   - Enables specialized agents

3. **Handoffs are Seamless:**
   - Agent 2 automatically sees Agent 1's work
   - No manual synchronization
   - Context continuity maintained

4. **Cost Scales with Agents:**
   - More agents = more savings
   - Compression applied once, used N times
   - Linear cost reduction

5. **Provider Independence Matters:**
   - Claude and Gemini share the same context
   - No vendor lock-in
   - Mix and match based on task

## Architecture Patterns

### Pattern 1: Sequential Pipeline

```
Agent 1 → Agent 2 → Agent 3 → Agent 4
(Research) → (Write) → (Edit) → (Publish)
```

Each agent:
- Reads context from previous agents
- Adds its own contributions
- Passes to next agent automatically

### Pattern 2: Parallel Specialists

```
         Agent 1 (Security)
              ↓
         UACS Context ← Agent 2 (Performance)
              ↓
         Agent 3 (Testing)
```

Agents work in parallel:
- Each analyzes different aspects
- All write to shared context
- Coordinator reads all topics

### Pattern 3: Hierarchical Coordination

```
        Coordinator Agent
         ↓    ↓    ↓
    Agent1 Agent2 Agent3
    (tasks to specialists)
         ↓    ↓    ↓
      UACS Shared Context
         ↓
    Coordinator (synthesis)
```

Coordinator:
- Assigns tasks with topics
- Specialists write results
- Coordinator reads all, synthesizes

## Next Steps

1. **Demo 4: Topic-Based Retrieval** - Advanced filtering for large contexts
2. **Demo 5: Claude Code Integration** - The killer use case
3. **See architecture.md** - Detailed multi-agent patterns

## Running the Demo

```bash
# From the project root
uv run python examples/03_multi_agent_context/demo.py
```

Expected runtime: < 2 seconds

## Key Concepts

- **Shared Context:** Single source of truth for all agents
- **Topics:** Enable routing context to relevant agents
- **Agent Keys:** Identify which agent contributed what
- **Compression:** Applied once, benefits all agents
- **Independence:** Agents don't need to know about each other

## Common Questions

**Q: Do agents need to know about each other?**
A: No. Agents only interact with UACS, not with each other directly.

**Q: What if two agents write conflicting information?**
A: Both entries are stored. Use topics or recency to prioritize. Consider adding metadata like "version" or "status".

**Q: Can I have private context per agent?**
A: Yes. Use agent-specific topics or separate UACS instances per agent.

**Q: How do I coordinate agent execution order?**
A: UACS handles context, not execution. Use a workflow orchestrator (e.g., LangGraph, Google ADK) for execution order.

**Q: What about agent-to-agent messages?**
A: Add metadata like `to_agent="code-fixer"` and filter by that in `build_context()`.

## Troubleshooting

**Issue:** Agent 2 doesn't see Agent 1's context
**Solution:**
- Check that both use the same project_path
- Verify topics match between write and read
- Check that context was committed (not in-memory only)

**Issue:** Context is too large for Agent 2
**Solution:**
- Use topic filtering: `topics=["relevant-topic"]`
- Reduce token budget: `max_tokens=2000`
- Filter by agent: pass agent name to `build_context()`

**Issue:** Agents are overwriting each other's entries
**Solution:**
- Use unique agent keys: "security-agent", "fixer-agent"
- Use different topics: "security-finding", "security-fix"
- Add metadata to distinguish versions

## Related Documentation

- [Library Guide](../../docs/LIBRARY_GUIDE.md) - API reference
- [architecture.md](./architecture.md) - Multi-agent patterns
- [Context Management](../../docs/CONTEXT.md) - Deep dive
