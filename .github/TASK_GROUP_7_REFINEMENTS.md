# Task Group 7: Refinements & Polish for v0.3.0

**Status:** Ready for Implementation
**Priority:** Medium (polish)
**Estimated Effort:** 4-6 hours
**Dependencies:** Task Groups 1, 2, 5 Complete ✅

---

## Overview

Polish the v0.3.0 release with performance optimizations, bug fixes, and enhancements identified during implementation.

### Refinement Categories

1. **Search Improvements** - Fix filtered search, improve ranking
2. **Performance** - Add benchmarks, optimize queries
3. **Confidence Decay** - Implement time-based decay for learnings
4. **Error Handling** - Better error messages, validation
5. **Developer Experience** - CLI improvements, better logging

---

## Task Breakdown

### Task 1: Fix Filtered Search by Type (1 hour)

**Issue:** Search type filtering may not work correctly when mixing conversations and knowledge results.

**File:** `src/uacs/api.py:330-363`

**Current Implementation:**
```python
def search(self, query: str, types: Optional[List[str]] = None, ...):
    results = []

    # Search conversations
    if search_conversations:
        conv_results = self.conversation_manager.search(...)
        results.extend(conv_results)

    # Search knowledge
    if search_knowledge:
        knowledge_results = self.knowledge_manager.search(...)
        results.extend(knowledge_results)

    # Sort all results
    results.sort(key=lambda r: r.similarity, reverse=True)
    return results[:limit]
```

**Problem:**
- Sorting uses different field names (similarity vs relevance_score)
- Type filtering logic may be incorrect
- No validation of type names

**Fix:**
```python
def search(self, query: str, types: Optional[List[str]] = None, ...):
    """Search across conversations and knowledge.

    Args:
        types: Optional list of types to search:
            Conversation types: user_message, assistant_message, tool_use
            Knowledge types: convention, decision, learning, artifact
    """
    # Validate types
    valid_types = {
        "user_message", "assistant_message", "tool_use",
        "convention", "decision", "learning", "artifact"
    }
    if types:
        invalid_types = set(types) - valid_types
        if invalid_types:
            raise ValueError(f"Invalid types: {invalid_types}. Valid: {valid_types}")

    results = []

    # Determine which managers to search
    conv_types = {"user_message", "assistant_message", "tool_use"}
    knowledge_types = {"convention", "decision", "learning", "artifact"}

    search_conversations = not types or bool(set(types) & conv_types)
    search_knowledge = not types or bool(set(types) & knowledge_types)

    # Search conversations
    if search_conversations:
        conv_filter = [t for t in (types or []) if t in conv_types] or None
        conv_results = self.conversation_manager.search(
            query=query,
            types=conv_filter,
            session_id=session_id,
            k=limit,
            threshold=min_confidence,
        )
        results.extend(conv_results)

    # Search knowledge
    if search_knowledge:
        knowledge_filter = [t for t in (types or []) if t in knowledge_types] or None
        knowledge_results = self.knowledge_manager.search(
            query=query,
            types=knowledge_filter,
            min_confidence=min_confidence,
            limit=limit,
        )
        results.extend(knowledge_results)

    # Normalize similarity scores (handle both field names)
    def get_similarity(result):
        return getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)

    # Sort by relevance
    results.sort(key=get_similarity, reverse=True)

    return results[:limit]
```

**Test:**
```python
def test_search_filtered_by_type():
    """Test that type filtering works correctly."""
    uacs = UACS(project_path=tmpdir)

    # Add different types
    uacs.add_user_message("message", turn=1, session_id="s1")
    uacs.add_decision("q", "d", "r", session_id="s1")
    uacs.add_convention("conv", topics=[])

    # Search only decisions
    results = uacs.search("test", types=["decision"], limit=10)
    assert all(r.metadata["type"] == "decision" for r in results)

    # Search only user messages
    results = uacs.search("test", types=["user_message"], limit=10)
    assert all(r.metadata["type"] == "user_message" for r in results)

    # Invalid type should raise error
    with pytest.raises(ValueError):
        uacs.search("test", types=["invalid_type"])
```

### Task 2: Performance Benchmarks (1-2 hours)

**Create:** `benchmarks/benchmark_search.py`

Measure search performance at different scales:

```python
"""Performance benchmarks for UACS v0.3.0 semantic search."""

import time
import tempfile
from pathlib import Path
from uacs import UACS

def benchmark_search_performance():
    """Benchmark search performance with different data sizes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        uacs = UACS(project_path=Path(tmpdir))

        # Test at different scales
        scales = [10, 50, 100, 500, 1000]
        results = {}

        for n in scales:
            # Add n items
            print(f"\nBenchmarking with {n} items...")
            for i in range(n):
                uacs.add_user_message(
                    content=f"Test message {i} about various topics",
                    turn=i,
                    session_id=f"session_{i // 10}"
                )

            # Measure search time
            start = time.time()
            search_results = uacs.search("test query", limit=10)
            elapsed = (time.time() - start) * 1000  # ms

            results[n] = elapsed
            print(f"  Search time: {elapsed:.2f}ms")
            print(f"  Results: {len(search_results)}")

        # Print summary
        print("\n=== Performance Summary ===")
        print(f"{'Items':<10} {'Search Time (ms)':<20}")
        print("-" * 30)
        for n, t in results.items():
            print(f"{n:<10} {t:<20.2f}")

        # Performance criteria
        assert results[100] < 500, "Search should be < 500ms for 100 items"
        assert results[1000] < 2000, "Search should be < 2s for 1000 items"

if __name__ == "__main__":
    benchmark_search_performance()
```

**Run benchmarks:**
```bash
python benchmarks/benchmark_search.py
```

**Expected Results:**
- 100 items: < 500ms
- 1000 items: < 2s
- 10,000 items: < 5s

### Task 3: Confidence Decay for Learnings (1-2 hours)

**Issue:** Old learnings should have lower confidence over time.

**File:** `src/uacs/knowledge/manager.py`

**Add method:**
```python
from datetime import datetime, timedelta

def get_learnings_with_decay(
    self,
    decay_days: int = 90,
    decay_rate: float = 0.5,
    min_confidence: float = 0.3
) -> List[Learning]:
    """Get learnings with time-based confidence decay.

    Args:
        decay_days: Days after which confidence decays by decay_rate
        decay_rate: Multiplier for decay (0.5 = half confidence after decay_days)
        min_confidence: Minimum confidence threshold

    Returns:
        List of learnings with adjusted confidence scores

    Example:
        # Learning created 100 days ago with confidence 0.9
        # After 90 days, confidence = 0.9 * 0.5 = 0.45
        learnings = manager.get_learnings_with_decay(decay_days=90, decay_rate=0.5)
    """
    learnings = self.list_learnings()
    now = datetime.now()
    adjusted_learnings = []

    for learning in learnings:
        age_days = (now - learning.created_at).days
        if age_days > decay_days:
            # Apply decay
            periods = age_days / decay_days
            adjusted_confidence = learning.confidence * (decay_rate ** periods)
        else:
            adjusted_confidence = learning.confidence

        # Only include if above min threshold
        if adjusted_confidence >= min_confidence:
            learning.confidence = adjusted_confidence
            adjusted_learnings.append(learning)

    return adjusted_learnings
```

**Test:**
```python
def test_learning_confidence_decay():
    """Test that learnings decay over time."""
    manager = KnowledgeManager(tmpdir)

    # Add learning (created now)
    learning = manager.add_learning(
        pattern="Test pattern",
        learned_from=["session_1"],
        confidence=0.9
    )

    # Manually set created_at to 100 days ago
    learning.created_at = datetime.now() - timedelta(days=100)
    # (In real code, you'd modify the stored JSON)

    # Get with decay (90 days, 0.5 rate)
    decayed = manager.get_learnings_with_decay(
        decay_days=90,
        decay_rate=0.5,
        min_confidence=0.3
    )

    # After 100 days with 90-day half-life:
    # 100/90 = 1.11 periods
    # 0.9 * (0.5 ** 1.11) ≈ 0.43
    assert len(decayed) == 1
    assert 0.40 < decayed[0].confidence < 0.45
```

**Add to UACS class:**
```python
def get_learnings_with_decay(
    self,
    decay_days: int = 90,
    decay_rate: float = 0.5,
    min_confidence: float = 0.3
) -> List[Learning]:
    """Get learnings with time-based confidence decay."""
    return self.knowledge_manager.get_learnings_with_decay(
        decay_days=decay_days,
        decay_rate=decay_rate,
        min_confidence=min_confidence
    )
```

### Task 4: Better Error Messages (1 hour)

**Current:** Generic errors that don't help debugging
**Goal:** Clear, actionable error messages

**Improve validation:**

```python
def add_user_message(
    self,
    content: str,
    turn: int,
    session_id: str,
    topics: Optional[List[str]] = None,
) -> UserMessage:
    """Add a user message."""
    # Validate inputs
    if not content or not content.strip():
        raise ValueError("content cannot be empty")

    if turn < 1:
        raise ValueError(f"turn must be >= 1, got {turn}")

    if not session_id or not session_id.strip():
        raise ValueError("session_id cannot be empty")

    if topics and not isinstance(topics, list):
        raise TypeError(f"topics must be a list, got {type(topics)}")

    if topics and any(not isinstance(t, str) for t in topics):
        raise TypeError("all topics must be strings")

    return self.conversation_manager.add_user_message(
        content=content,
        turn=turn,
        session_id=session_id,
        topics=topics or []
    )
```

**Add helpful error context:**

```python
try:
    uacs.add_user_message("", turn=1, session_id="s1")
except ValueError as e:
    # Error message: "content cannot be empty"
    # Context: "When calling add_user_message(turn=1, session_id='s1')"
```

### Task 5: CLI Improvements (1 hour)

**File:** `src/uacs/cli/main.py`

**Add commands:**

```python
@app.command()
def stats(project_path: Path = Path(".")):
    """Show comprehensive statistics."""
    uacs = UACS(project_path=project_path)
    stats = uacs.get_stats()

    console.print("\n[bold]UACS Statistics[/bold]\n")

    # Project info
    console.print(f"Project: {stats['project_path']}")
    console.print(f"Version: {__version__}\n")

    # Semantic stats
    semantic = stats.get("semantic", {})
    if semantic:
        console.print("[bold]Semantic Context:[/bold]")
        conv = semantic.get("conversations", {})
        console.print(f"  User Messages: {conv.get('total_user_messages', 0)}")
        console.print(f"  Assistant Messages: {conv.get('total_assistant_messages', 0)}")
        console.print(f"  Tool Uses: {conv.get('total_tool_uses', 0)}")
        console.print(f"  Sessions: {conv.get('total_sessions', 0)}")

        knowledge = semantic.get("knowledge", {})
        console.print(f"\n  Decisions: {knowledge.get('decisions', 0)}")
        console.print(f"  Conventions: {knowledge.get('conventions', 0)}")
        console.print(f"  Learnings: {knowledge.get('learnings', 0)}")
        console.print(f"  Artifacts: {knowledge.get('artifacts', 0)}")

        embeddings = semantic.get("embeddings", {})
        console.print(f"\n  Total Embeddings: {embeddings.get('total_vectors', 0)}")
        console.print(f"  Model: {embeddings.get('model_name', 'N/A')}")

@app.command()
def search_cli(
    query: str,
    limit: int = 10,
    types: Optional[str] = None,
    project_path: Path = Path(".")
):
    """Search context with natural language.

    Example:
        uacs search "how did we implement authentication?" --limit 5
        uacs search "security decisions" --types decision,convention
    """
    uacs = UACS(project_path=project_path)

    # Parse types
    type_list = types.split(",") if types else None

    results = uacs.search(query=query, types=type_list, limit=limit)

    console.print(f"\n[bold]Search Results[/bold] ({len(results)} found)\n")

    for i, result in enumerate(results, 1):
        result_type = result.metadata.get("type", "unknown")
        similarity = getattr(result, 'similarity', None) or getattr(result, 'relevance_score', 0)
        text = getattr(result, 'text', None) or getattr(result, 'content', '')

        console.print(f"{i}. [{result_type}] {similarity:.2%}")
        console.print(f"   {text[:100]}...")
        console.print()
```

**Usage:**
```bash
uacs stats
uacs search "how did we implement auth?" --limit 5
uacs search "security" --types decision,convention
```

### Task 6: Logging Improvements (0.5 hour)

**Add structured logging:**

```python
import logging

logger = logging.getLogger("uacs")

# Configure in __init__.py
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Use in code
logger.info(f"Initialized UACS at {project_path}")
logger.debug(f"Created user message: turn={turn}, session={session_id}")
logger.warning(f"Search returned 0 results for query: {query}")
logger.error(f"Failed to add decision: {e}")
```

**Add verbose flag to CLI:**

```python
@app.command()
def serve(
    verbose: bool = False,
    ...
):
    """Start MCP server."""
    if verbose:
        logging.getLogger("uacs").setLevel(logging.DEBUG)
```

### Task 7: Code Quality (0.5 hour)

**Run linters and fix issues:**

```bash
# Type checking
mypy src/uacs/

# Linting
ruff check src/uacs/

# Formatting
black src/uacs/

# Security
bandit -r src/uacs/
```

**Fix common issues:**
- Add missing type hints
- Remove unused imports
- Fix docstring formatting
- Remove dead code

---

## Success Criteria

- [ ] Filtered search works correctly with all type combinations
- [ ] Performance benchmarks pass (< 500ms for 100 items)
- [ ] Confidence decay implemented and tested
- [ ] All error messages are clear and actionable
- [ ] CLI commands enhanced (stats, search)
- [ ] Logging is structured and configurable
- [ ] Code passes linters (mypy, ruff, black, bandit)
- [ ] No security vulnerabilities found

---

## Implementation Prompt

Use this prompt with an agent:

```
# Task: Polish UACS v0.3.0 with Refinements

## Context
You need to polish the v0.3.0 release with bug fixes, performance improvements, and UX enhancements.

## Reference
- Refinements Plan: .github/TASK_GROUP_7_REFINEMENTS.md (THIS FILE)
- Code to refine: src/uacs/api.py, src/uacs/cli/main.py

## Your Task
1. Fix filtered search by type
2. Add performance benchmarks
3. Implement confidence decay for learnings
4. Improve error messages with validation
5. Add CLI commands (stats, search)
6. Improve logging
7. Run linters and fix issues

## Priority
1. Fix filtered search (critical bug)
2. Performance benchmarks (measure quality)
3. CLI improvements (user-facing)
4. Confidence decay (nice enhancement)
5. Error messages (UX improvement)
6. Logging (debugging)
7. Code quality (polish)

## Guidelines
- Test each fix thoroughly
- Add tests for new features
- Update documentation if behavior changes
- Run linters before committing
```

---

## Files to Modify

1. **src/uacs/api.py** - Fix search filtering, add validation
2. **src/uacs/knowledge/manager.py** - Add confidence decay
3. **src/uacs/cli/main.py** - Add stats and search commands
4. **benchmarks/benchmark_search.py** - NEW - Performance benchmarks
5. **tests/** - Add tests for all fixes

---

## Testing Checklist

- [ ] Filtered search works with single type
- [ ] Filtered search works with multiple types
- [ ] Invalid type raises clear error
- [ ] Benchmarks pass at all scales
- [ ] Confidence decay calculates correctly
- [ ] Error messages are helpful
- [ ] CLI stats command works
- [ ] CLI search command works
- [ ] All tests pass
- [ ] Linters pass (mypy, ruff, black)

---

**Status:** ✅ Ready for Implementation
**Next Step:** Start with fixing filtered search (highest priority bug)
