# Multi-Agent Architecture Patterns with UACS

This document describes proven multi-agent architecture patterns using UACS for context sharing.

---

## Pattern 1: Sequential Pipeline

### Description
Agents process information in sequence, each building on the previous agent's work.

### Architecture
```
Agent 1 → Agent 2 → Agent 3 → Agent 4
(Stage 1) → (Stage 2) → (Stage 3) → (Stage 4)
     ↓         ↓          ↓          ↓
        UACS Shared Context
```

### Use Cases
- **Content Pipeline:** Research → Write → Edit → Publish
- **Code Pipeline:** Analyze → Implement → Review → Deploy
- **Data Pipeline:** Collect → Clean → Analyze → Visualize
- **Support Pipeline:** Classify → Handle → Escalate → Close

### Implementation

```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path.cwd())

# Agent 1: Research
uacs.add_to_context(
    key="researcher",
    content="Found 5 relevant papers on topic X...",
    topics=["research", "sources"]
)

# Agent 2: Writer (reads research)
research_context = uacs.build_context(
    query="Write article based on research",
    agent="writer",
    topics=["research"]
)
# ... LLM call with research_context ...
uacs.add_to_context(
    key="writer",
    content="Draft article: ...",
    topics=["draft", "content"]
)

# Agent 3: Editor (reads draft)
draft_context = uacs.build_context(
    query="Edit for clarity and style",
    agent="editor",
    topics=["draft"]
)
# ... LLM call with draft_context ...
uacs.add_to_context(
    key="editor",
    content="Edited article: ...",
    topics=["final", "content"]
)
```

### Benefits
- Clear separation of concerns
- Easy to understand and debug
- Natural error handling (stop pipeline on failure)
- Progressive refinement

### Considerations
- Sequential = slower than parallel
- Bottlenecks at any stage affect entire pipeline
- Consider parallel patterns for independent tasks

---

## Pattern 2: Parallel Specialists

### Description
Multiple agents work simultaneously on different aspects of the same problem.

### Architecture
```
              Coordinator
                   ↓
        ┌──────────┼──────────┐
        ↓          ↓           ↓
    Agent 1    Agent 2     Agent 3
   (Security) (Performance) (Testing)
        ↓          ↓           ↓
           UACS Shared Context
                   ↓
              Coordinator
              (Synthesize)
```

### Use Cases
- **Code Review:** Security + Performance + Style + Tests (parallel)
- **Analysis:** Financial + Technical + Market + Competitive (parallel)
- **Content Creation:** SEO + Readability + Accuracy + Engagement (parallel)
- **Due Diligence:** Legal + Financial + Technical + Market (parallel)

### Implementation

```python
from uacs import UACS
import asyncio

uacs = UACS(project_path=Path.cwd())

# Coordinator assigns work
uacs.add_to_context(
    key="coordinator",
    content="Review codebase for security, performance, and testing",
    topics=["task", "coordination"]
)

# Parallel specialist agents (run concurrently)
async def security_agent():
    context = uacs.build_context(
        query="Review for security issues",
        agent="security",
        topics=["task"]
    )
    # ... analyze security ...
    uacs.add_to_context(
        key="security",
        content="Found 3 security issues: ...",
        topics=["security", "findings"]
    )

async def performance_agent():
    context = uacs.build_context(
        query="Review for performance issues",
        agent="performance",
        topics=["task"]
    )
    # ... analyze performance ...
    uacs.add_to_context(
        key="performance",
        content="Found 2 performance bottlenecks: ...",
        topics=["performance", "findings"]
    )

async def testing_agent():
    context = uacs.build_context(
        query="Review test coverage",
        agent="testing",
        topics=["task"]
    )
    # ... analyze testing ...
    uacs.add_to_context(
        key="testing",
        content="Test coverage is 65%, need more tests for: ...",
        topics=["testing", "findings"]
    )

# Run all agents in parallel
await asyncio.gather(
    security_agent(),
    performance_agent(),
    testing_agent()
)

# Coordinator synthesizes results
all_findings = uacs.build_context(
    query="Synthesize all findings into action plan",
    agent="coordinator",
    topics=["findings"]
)
# ... LLM synthesizes ...
```

### Benefits
- Faster than sequential (parallel execution)
- Specialized agents for complex tasks
- Independent failures (one agent failing doesn't stop others)
- Scalable (add more specialists easily)

### Considerations
- Need orchestration for parallel execution
- Potential for conflicting recommendations
- Coordinator must synthesize diverse outputs

---

## Pattern 3: Hierarchical Coordination

### Description
A coordinator agent delegates sub-tasks to specialist agents, then synthesizes results.

### Architecture
```
                 Coordinator
                      ↓
            (Break into subtasks)
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓              ↓
    Specialist 1  Specialist 2  Specialist 3
        ↓             ↓              ↓
              UACS Shared Context
                      ↓
                 Coordinator
                (Synthesize)
```

### Use Cases
- **Complex Analysis:** Break problem into sub-problems
- **Large Codebase:** Divide by module/component
- **Research:** Break into sub-topics
- **Project Planning:** Break into phases

### Implementation

```python
from uacs import UACS

uacs = UACS(project_path=Path.cwd())

# Coordinator breaks down task
uacs.add_to_context(
    key="coordinator",
    content="Project: Build authentication system. Subtasks: database schema, API endpoints, frontend UI",
    topics=["planning", "coordination"]
)

# Assign subtasks
subtasks = [
    {"agent": "database-specialist", "task": "Design database schema", "topic": "database"},
    {"agent": "backend-specialist", "task": "Implement API endpoints", "topic": "backend"},
    {"agent": "frontend-specialist", "task": "Build login UI", "topic": "frontend"},
]

for subtask in subtasks:
    uacs.add_to_context(
        key="coordinator",
        content=f"Assigned to {subtask['agent']}: {subtask['task']}",
        topics=["assignment", subtask["topic"]]
    )

# Specialists work on their tasks
for subtask in subtasks:
    context = uacs.build_context(
        query=subtask["task"],
        agent=subtask["agent"],
        topics=["assignment", subtask["topic"]]
    )
    # ... specialist works ...
    uacs.add_to_context(
        key=subtask["agent"],
        content=f"Completed {subtask['task']}: ...",
        topics=["completion", subtask["topic"]]
    )

# Coordinator synthesizes
synthesis_context = uacs.build_context(
    query="Synthesize all completed work into project plan",
    agent="coordinator",
    topics=["completion"]
)
```

### Benefits
- Handles complex, multi-faceted problems
- Clear delegation and ownership
- Coordinator maintains big picture
- Specialists focus on their domain

### Considerations
- Coordinator is critical path
- Requires good task decomposition
- More overhead than flat patterns

---

## Pattern 4: Iterative Refinement

### Description
Agents iterate on shared artifacts, each improving quality.

### Architecture
```
Round 1:  Agent 1 → Agent 2 → Agent 3
             ↓         ↓         ↓
           UACS Shared Context
             ↓         ↓         ↓
Round 2:  Agent 1 → Agent 2 → Agent 3
             ↓         ↓         ↓
           UACS Shared Context
```

### Use Cases
- **Document Editing:** Multiple review rounds
- **Code Review:** Implement → Review → Fix → Re-review
- **Design:** Concept → Critique → Refine → Approve
- **Planning:** Propose → Analyze → Revise → Finalize

### Implementation

```python
from uacs import UACS

uacs = UACS(project_path=Path.cwd())

# Iteration 1: Initial draft
uacs.add_to_context(
    key="writer",
    content="Draft v1: ...",
    topics=["draft", "v1"]
)

# Iteration 1: Review
review_context = uacs.build_context(
    query="Review draft for issues",
    agent="reviewer",
    topics=["draft", "v1"]
)
uacs.add_to_context(
    key="reviewer",
    content="Issues found: clarity problems, missing examples",
    topics=["review", "v1"]
)

# Iteration 2: Revised draft
revision_context = uacs.build_context(
    query="Revise draft based on review",
    agent="writer",
    topics=["draft", "v1", "review"]
)
uacs.add_to_context(
    key="writer",
    content="Draft v2: ... (addressed review comments)",
    topics=["draft", "v2"]
)

# Iteration 2: Re-review
review2_context = uacs.build_context(
    query="Re-review draft v2",
    agent="reviewer",
    topics=["draft", "v2"]
)
# ... continue until approved ...
```

### Benefits
- Progressive quality improvement
- Captures iteration history
- Agents learn from previous rounds
- Natural stopping condition (approval)

### Considerations
- Can be slow (many rounds)
- Risk of diminishing returns
- Need clear exit criteria

---

## Pattern 5: Broadcast-Gather

### Description
One agent broadcasts a question/task, multiple agents respond, coordinator gathers responses.

### Architecture
```
        Coordinator (Broadcast)
                 ↓
      ┌──────────┼──────────┐
      ↓          ↓           ↓
   Agent 1    Agent 2    Agent 3
      ↓          ↓           ↓
       UACS Shared Context
                 ↓
        Coordinator (Gather)
```

### Use Cases
- **Decision Making:** Get opinions from multiple agents
- **Estimation:** Multiple agents estimate, coordinator averages
- **Brainstorming:** Generate diverse ideas
- **Voting:** Multiple agents vote on options

### Implementation

```python
from uacs import UACS

uacs = UACS(project_path=Path.cwd())

# Broadcast question
uacs.add_to_context(
    key="coordinator",
    content="Question: Should we use PostgreSQL or MongoDB for this project?",
    topics=["question", "database"]
)

# Agents respond
agents = ["database-expert", "scalability-expert", "cost-analyst"]

for agent in agents:
    context = uacs.build_context(
        query="Answer the database question",
        agent=agent,
        topics=["question", "database"]
    )
    # ... agent thinks ...
    uacs.add_to_context(
        key=agent,
        content=f"{agent} recommends: ... because ...",
        topics=["response", "database", agent]
    )

# Gather responses
responses_context = uacs.build_context(
    query="Gather all responses and make decision",
    agent="coordinator",
    topics=["response", "database"]
)
# ... coordinator decides based on responses ...
```

### Benefits
- Democratic decision making
- Diverse perspectives
- Reduces single-agent bias
- Explicit consensus building

### Considerations
- Can be slow (wait for all responses)
- Conflicting opinions need resolution
- Coordinator must synthesize effectively

---

## Best Practices

### 1. Use Topics Strategically

```python
# Good: Specific topics enable precise filtering
uacs.add_to_context(
    key="agent",
    content="Finding: ...",
    topics=["security", "sql-injection", "critical"]
)

# Bad: Generic topics don't help filtering
uacs.add_to_context(
    key="agent",
    content="Finding: ...",
    topics=["data"]
)
```

### 2. Add Metadata for Coordination

```python
uacs.add_to_context(
    key="agent",
    content="Task completed",
    topics=["completion"],
    metadata={
        "task_id": "auth-123",
        "status": "complete",
        "duration": 45.2,
        "assigned_to": "backend-agent"
    }
)
```

### 3. Version Your Artifacts

```python
# Track versions explicitly
uacs.add_to_context(
    key="writer",
    content="Document content...",
    topics=["document", "v3"],
    metadata={"version": 3, "changes": "Fixed typos"}
)
```

### 4. Use Agent-Specific Topics

```python
# Each agent gets its own namespace
uacs.add_to_context(
    key="security-agent",
    content="Analysis results...",
    topics=["agent:security", "findings"]
)

# Coordinator can filter by agent
context = uacs.build_context(
    query="Get security agent's work",
    agent="coordinator",
    topics=["agent:security"]
)
```

### 5. Implement Handoff Signals

```python
# Agent 1 signals readiness
uacs.add_to_context(
    key="agent1",
    content="Ready for next stage",
    topics=["handoff", "agent1-complete"]
)

# Agent 2 checks for signal
context = uacs.build_context(
    query="Check if agent1 is done",
    agent="agent2",
    topics=["handoff", "agent1-complete"]
)
```

---

## Anti-Patterns to Avoid

### 1. No Topic Organization
**Problem:** All content dumped without topics
**Solution:** Use hierarchical topics: "security/sql-injection", "performance/database"

### 2. Agent Name Collisions
**Problem:** Multiple agents use same key: "agent"
**Solution:** Use descriptive, unique keys: "security-scanner-v2"

### 3. Unbounded Context Growth
**Problem:** Context grows infinitely, costs explode
**Solution:** Use `max_tokens` budget, clean old entries periodically

### 4. Ignoring Compression
**Problem:** Sending all context to every agent
**Solution:** Use topic filtering to reduce tokens per agent

### 5. No Error Handling
**Problem:** One agent failure stops entire workflow
**Solution:** Implement fallbacks, retries, and graceful degradation

---

## Performance Optimization

### 1. Batch Agent Calls

```python
# Bad: Sequential calls
for agent in agents:
    context = uacs.build_context(...)
    result = call_llm(context)
    uacs.add_to_context(key=agent, content=result)

# Good: Parallel calls
import asyncio

async def process_agent(agent):
    context = uacs.build_context(...)
    result = await call_llm_async(context)
    uacs.add_to_context(key=agent, content=result)

await asyncio.gather(*[process_agent(a) for a in agents])
```

### 2. Cache Common Context

```python
# Build base context once, reuse for multiple agents
base_context = uacs.build_context(
    query="Background information",
    agent="any",
    topics=["background"]
)

# Each agent adds specific context
for agent in agents:
    specific = uacs.build_context(
        query="Agent-specific task",
        agent=agent,
        topics=[f"agent:{agent}"]
    )
    full_context = f"{base_context}\n\n{specific}"
```

### 3. Progressive Context Loading

```python
# Start with minimal context
context = uacs.build_context(
    query="Quick answer needed",
    agent="responder",
    max_tokens=1000  # Minimal
)

# If more context needed, expand
if needs_more_context:
    context = uacs.build_context(
        query="Detailed answer needed",
        agent="responder",
        max_tokens=4000  # Expanded
    )
```

---

## Monitoring and Debugging

### 1. Track Token Usage Per Agent

```python
stats = uacs.get_token_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Compression: {stats['compression_ratio']}%")

# Track per-agent costs
for agent in agents:
    context = uacs.build_context(agent=agent, topics=[f"agent:{agent}"])
    tokens = count_tokens(context)
    print(f"{agent}: {tokens} tokens")
```

### 2. Visualize Agent Communication

```python
# Log all agent interactions
uacs.add_to_context(
    key="logger",
    content=f"{agent1} → {agent2}: {message}",
    topics=["communication", "audit"]
)

# Later, reconstruct conversation flow
audit = uacs.build_context(
    query="Show all agent communications",
    agent="auditor",
    topics=["communication"]
)
```

### 3. Set Up Alerts

```python
stats = uacs.get_token_stats()

# Alert if context too large
if stats['total_tokens'] > 50000:
    print(f"WARNING: Context size exceeds 50K tokens")

# Alert if compression low
if stats['compression_ratio'] < 30:
    print(f"WARNING: Low compression, consider adding topics")
```

---

## Conclusion

These patterns provide a foundation for building multi-agent systems with UACS. Key principles:

1. **Use topics for routing** - Direct context to relevant agents
2. **Compress aggressively** - Save tokens = save money
3. **Design for independence** - Agents shouldn't know about each other
4. **Monitor token usage** - Track costs in production
5. **Choose the right pattern** - Sequential, parallel, or hierarchical based on use case

For more examples, see the demo.py file in this directory.
