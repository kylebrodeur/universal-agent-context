# Demo 4: Topic-Based Retrieval

## What

This demo demonstrates UACS's topic-based filtering system for focused context retrieval. You'll see:

- Adding context with multiple topics (security, performance, testing, documentation)
- Retrieving context filtered by specific topics
- Comparing token usage with/without topic filtering
- Building multi-topic queries
- Understanding topic hierarchies

This is the **precision** feature - get exactly the context you need, nothing more.

## Why

**Value Proposition:** Large contexts contain irrelevant information:

- Security review doesn't need testing context
- Performance optimization doesn't need documentation updates
- Bug fixes don't need feature planning discussions

**Without topic filtering:**
- 10,000 token context → Send all 10K tokens
- Cost: $0.10 per call
- Noise: 70% irrelevant content confuses the agent

**With topic filtering:**
- 10,000 token context → Send 2,000 tokens (security only)
- Cost: $0.02 per call (80% savings)
- Clarity: 100% relevant content improves response quality

**Real-world Impact:**
- Reduce token costs by 50-80% on large contexts
- Improve agent response relevance
- Enable massive contexts (100K+ tokens) with focused retrieval
- Support complex multi-topic projects

## When

Use topic-based retrieval when:
- Your project has distinct concerns (security, performance, testing, etc.)
- Context exceeds 5,000 tokens
- Different agents need different context subsets
- You want to reduce noise in agent responses
- You're managing long-running projects with diverse topics

**Essential for:**
- Large codebases with multiple domains
- Long conversations with topic drift
- Multi-agent systems with specialized roles
- Production systems with cost constraints

## How

### Basic Topic Filtering

```python
from uacs import UACS

uacs = UACS(project_path=Path.cwd())

# Add context with topics
uacs.add_to_context(
    key="security-scanner",
    content="Found SQL injection at line 42",
    topics=["security", "sql-injection", "critical"]
)

# Retrieve only security-related context
security_context = uacs.build_context(
    query="Fix security issues",
    agent="fixer",
    topics=["security"]  # Filter by topic
)
```

### Topic Hierarchies

Use hierarchical topics for fine-grained control:

```python
# Hierarchical topics
topics = [
    "security/sql-injection",
    "security/xss",
    "performance/database",
    "performance/caching",
    "testing/unit",
    "testing/integration"
]

# Retrieve all security
security = uacs.build_context(topics=["security"])  # Matches security/*

# Retrieve only SQL injection
sql = uacs.build_context(topics=["security/sql-injection"])  # Specific
```

### Multi-Topic Queries

Combine multiple topics:

```python
# Get security AND performance context
critical = uacs.build_context(
    query="Review critical issues",
    agent="reviewer",
    topics=["security", "performance"]
)

# This includes:
# - All security/* topics
# - All performance/* topics
# - Excludes testing/*, documentation/*, etc.
```

## Output

Running this demo shows topic filtering in action:

```
Adding context across 4 topics:
  Security: 15 entries (3,456 tokens)
  Performance: 12 entries (2,890 tokens)
  Testing: 8 entries (1,567 tokens)
  Documentation: 5 entries (892 tokens)

Total context: 40 entries, 8,805 tokens

Retrieving with topic filters:

1. Security only:
   Retrieved: 15 entries, 3,456 tokens (61% reduction)
   Cost savings: $0.05 per call

2. Performance only:
   Retrieved: 12 entries, 2,890 tokens (67% reduction)
   Cost savings: $0.06 per call

3. Security + Performance:
   Retrieved: 27 entries, 6,346 tokens (28% reduction)
   Cost savings: $0.02 per call

4. No filter (all topics):
   Retrieved: 40 entries, 8,805 tokens (0% reduction)
   Cost: Full price
```

## What You Learned

1. **Topic Filtering is Powerful:**
   - 50-80% token reduction on multi-topic contexts
   - Zero information loss for the focused topic
   - Linear cost reduction with filtering

2. **Topics are Hierarchical:**
   - Use "/" for hierarchy: "security/sql-injection"
   - Query parent matches all children
   - Enables fine-grained control

3. **Multi-Topic Queries Work:**
   - Combine topics with OR logic
   - Include multiple domains in one query
   - Still cheaper than full context

4. **Quality Improves:**
   - Less noise = better agent responses
   - Focused context = more relevant output
   - Reduces hallucination risk

5. **Massive Contexts Become Viable:**
   - Store 100K+ tokens
   - Retrieve 2K-5K tokens per query
   - Cost scales with retrieval, not storage

## Use Case Examples

### 1. Code Review with Multiple Concerns

```python
# Add findings across topics
uacs.add_to_context("scanner", "SQL injection found", topics=["security", "critical"])
uacs.add_to_context("scanner", "N+1 query problem", topics=["performance", "database"])
uacs.add_to_context("scanner", "Missing unit tests", topics=["testing", "coverage"])

# Security agent sees only security
security_context = uacs.build_context(agent="security-fixer", topics=["security"])

# Performance agent sees only performance
perf_context = uacs.build_context(agent="perf-optimizer", topics=["performance"])

# Each agent gets focused, relevant context
```

### 2. Long-Running Project History

```python
# Over time, accumulate diverse context
# Week 1: Security fixes
# Week 2: Performance optimization
# Week 3: Feature development
# Week 4: Bug fixes

# After 4 weeks: 50K tokens total context

# But each query only retrieves what's needed:
bug_fix_context = uacs.build_context(
    query="Fix bug #1234",
    topics=["bugs", "authentication"],
    max_tokens=3000  # Only 6% of total context
)
```

### 3. Multi-Agent Coordination

```python
# Coordinator assigns topics to specialists
specialists = {
    "security": ["security"],
    "performance": ["performance"],
    "testing": ["testing"],
    "documentation": ["documentation"]
}

# Each specialist gets only their context
for agent, topics in specialists.items():
    context = uacs.build_context(
        query=f"Work on {agent} issues",
        agent=agent,
        topics=topics
    )
    # Agent sees only relevant context, no noise
```

## Next Steps

1. **Demo 5: Claude Code Integration** - The killer use case for conversation compaction
2. **See use_cases.md** - More real-world topic-based retrieval examples
3. **Read architecture.md** - How topics enable multi-agent systems

## Running the Demo

```bash
uv run python examples/04_topic_based_retrieval/demo.py
```

Expected runtime: < 2 seconds

## Key Concepts

- **Topics:** Tags for semantic filtering (e.g., "security", "performance")
- **Hierarchies:** Use "/" for nested topics ("security/sql-injection")
- **Multi-Topic:** Combine topics with OR logic
- **Filtering:** Include only matching topics in context
- **Compression:** Topic filtering stacks with other compression strategies

## Common Questions

**Q: How many topics should I use?**
A: 3-7 top-level topics is typical. More topics = finer control but more complexity.

**Q: Should topics be hierarchical?**
A: Yes, if you have subcategories. Example: "security/sql", "security/xss", "security/timing"

**Q: Can I add topics after the fact?**
A: No, topics are set when adding context. Plan your topic taxonomy upfront.

**Q: What if I use the wrong topic?**
A: Content is still stored, just not retrieved. You can query without topic filter to see everything.

**Q: How do topics interact with compression?**
A: Topic filtering happens first, then compression. So you get 80% from topic filtering + 70% from compression = 94% total reduction.

## Troubleshooting

**Issue:** Topic filter returns no results
**Solution:**
- Check spelling of topic names
- Verify entries have that topic
- Try querying without filter to see all topics

**Issue:** Too much context still returned
**Solution:**
- Use more specific topics (hierarchical)
- Combine topic filter with `max_tokens` budget
- Check for entries tagged with multiple topics

**Issue:** Important context missing
**Solution:**
- Add missing topic to entries: `topics=["security", "important"]`
- Use parent topic to match all children
- Remove filter if you need everything

## Related Documentation

- [Context Management](../../docs/CONTEXT.md) - Topic system deep dive
- [Library Guide](../../docs/LIBRARY_GUIDE.md) - API reference
- [use_cases.md](./use_cases.md) - Real-world examples
