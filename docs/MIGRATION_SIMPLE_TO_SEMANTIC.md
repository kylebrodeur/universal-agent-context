# Migrating from SimpleMemoryStore to Semantic API

**Status:** SimpleMemoryStore is deprecated as of v0.3.0 and will be removed in v1.0.0.

This guide helps you migrate from the legacy `SimpleMemoryStore` to the modern **UACS Semantic API** (v0.3.0+), which provides structured memory with semantic search, rich metadata, and validation.

---

## Why Migrate?

### ❌ SimpleMemoryStore (Legacy)
```python
store = SimpleMemoryStore(project_path=Path("."))
store.store("auth-decision", {
    "note": "We chose JWT",
    "reason": "It's stateless",
    "tags": "security,auth"  # Unstructured strings
}, scope="project")
```

**Problems:**
- ❌ No validation - accepts any dictionary
- ❌ No structure - each entry can be different
- ❌ Basic search - substring matching only
- ❌ Minimal metadata - no topics, confidence, or provenance
- ❌ No type system - all entries are generic

### ✅ Semantic API (Modern)
```python
uacs = UACS(project_path=Path("."))
uacs.add_decision(
    question="How should we handle API authentication?",
    decision="JWT with RS256 asymmetric signing",
    rationale="Stateless, scalable, works well with microservices",
    decided_by="team",
    session_id="migration_001",
    alternatives=["Session-based", "OAuth2", "API keys"],
    topics=["security", "authentication"]
)
```

**Benefits:**
- ✅ **Type validation** - Pydantic models enforce structure
- ✅ **Semantic search** - Find by meaning, not just keywords
- ✅ **Rich metadata** - Topics, confidence, provenance, timestamps
- ✅ **Type system** - Conventions, Decisions, Learnings, Artifacts
- ✅ **Deduplication** - Automatic similarity detection
- ✅ **Quality tracking** - Confidence scores and freshness

---

## Migration Patterns

### 1. Generic Notes → Conventions

**Before:**
```python
store.store("coding-style", {
    "rule": "Use Pydantic for all data validation",
    "applies_to": "validation,data-models"
}, scope="project")
```

**After:**
```python
uacs.add_convention(
    content="Use Pydantic models for all data validation",
    topics=["validation", "data-models"],
    source_session="migration_001",
    confidence=1.0  # High confidence = always follow
)
```

### 2. Decision Records → Decisions

**Before:**
```python
store.store("cache-decision", {
    "question": "How to cache expensive queries?",
    "choice": "Redis with TTL",
    "why": "Fast, distributed, automatic expiration",
    "other_options": "In-memory cache, Memcached"
}, scope="project")
```

**After:**
```python
uacs.add_decision(
    question="How should we cache expensive database queries?",
    decision="Use Redis with TTL-based invalidation",
    rationale="Redis provides fast lookups, distributed caching, and automatic expiration",
    alternatives=["In-memory cache", "Memcached"],
    decided_by="team",
    session_id="performance_session_002",
    topics=["performance", "caching", "database"]
)
```

### 3. Insights → Learnings

**Before:**
```python
store.store("user-preference", {
    "insight": "Users prefer inline validation",
    "confidence": "high",
    "from_sessions": ["session_1", "session_2"]
}, scope="global")
```

**After:**
```python
uacs.add_learning(
    pattern="Users prefer inline validation over submit-time validation",
    confidence=0.85,  # 0.0-1.0 scale
    learned_from=["session_2024_01_10", "session_2024_01_12"],
    category="usability"
)
```

### 4. File References → Artifacts

**Before:**
```python
store.store("auth-module", {
    "file": "src/auth.py",
    "description": "JWT authentication implementation",
    "created": "2024-01-15"
}, scope="project")
```

**After:**
```python
uacs.add_artifact(
    type="file",
    path="src/auth.py",
    description="JWT authentication implementation with RS256 signing",
    created_in_session="auth_session_001",
    topics=["authentication", "jwt", "security"]
)
```

### 5. Conversation History → Messages & Tool Uses

**Before:**
```python
store.store("chat-turn-1", {
    "user": "Help me with auth",
    "assistant": "I'll help you implement JWT...",
    "tokens": 200
}, scope="project")
```

**After:**
```python
# User message
uacs.add_user_message(
    content="Help me implement JWT authentication",
    turn=1,
    session_id="auth_session_001",
    topics=["security", "authentication"]
)

# Assistant response
uacs.add_assistant_message(
    content="I'll help you implement JWT. Let's use PyJWT library...",
    turn=1,
    session_id="auth_session_001",
    tokens_in=42,
    tokens_out=156,
    model="claude-sonnet-4"
)

# Tool execution
uacs.add_tool_use(
    tool_name="Edit",
    tool_input={"file": "auth.py", "operation": "create"},
    tool_response="Created auth.py with JWT implementation",
    turn=2,
    session_id="auth_session_001",
    latency_ms=450,
    success=True
)
```

---

## Migration Script

Use this script to convert existing SimpleMemoryStore entries to Semantic API:

```python
#!/usr/bin/env python3
"""Migrate SimpleMemoryStore to UACS Semantic API."""

from pathlib import Path
from uacs import UACS
from uacs.memory.simple_memory import SimpleMemoryStore

def migrate_memory(project_path: Path, session_id: str = "migration_001"):
    """Migrate SimpleMemoryStore entries to Semantic API.
    
    Args:
        project_path: Path to project root
        session_id: Session ID for migrated entries
    """
    # Initialize both systems
    old_store = SimpleMemoryStore(project_path=project_path)
    uacs = UACS(project_path=project_path)
    
    print(f"🔍 Scanning SimpleMemoryStore entries...")
    entries = old_store.list_entries(scope="both")
    print(f"   Found {len(entries)} entries")
    
    migrated = {"conventions": 0, "decisions": 0, "learnings": 0, "artifacts": 0, "skipped": 0}
    
    for entry in entries:
        data = entry.data
        
        # Detect type based on data structure
        if "rule" in data or "content" in data:
            # Convention
            content = data.get("content") or data.get("rule", "")
            topics = _extract_topics(data)
            uacs.add_convention(
                content=content,
                topics=topics,
                source_session=session_id,
                confidence=_extract_confidence(data)
            )
            migrated["conventions"] += 1
            print(f"   ✅ Migrated convention: {entry.key}")
            
        elif "question" in data and "decision" in data:
            # Decision
            uacs.add_decision(
                question=data.get("question", ""),
                decision=data.get("decision", data.get("choice", "")),
                rationale=data.get("rationale", data.get("why", "")),
                alternatives=_extract_list(data.get("alternatives", data.get("other_options", []))),
                decided_by=data.get("decided_by", "migration"),
                session_id=session_id,
                topics=_extract_topics(data)
            )
            migrated["decisions"] += 1
            print(f"   ✅ Migrated decision: {entry.key}")
            
        elif "pattern" in data or "insight" in data:
            # Learning
            pattern = data.get("pattern") or data.get("insight", "")
            uacs.add_learning(
                pattern=pattern,
                confidence=_extract_confidence(data),
                learned_from=_extract_list(data.get("learned_from", data.get("from_sessions", [session_id]))),
                category=data.get("category", "general")
            )
            migrated["learnings"] += 1
            print(f"   ✅ Migrated learning: {entry.key}")
            
        elif "file" in data or "path" in data:
            # Artifact
            path = data.get("path") or data.get("file", "")
            uacs.add_artifact(
                type=data.get("type", "file"),
                path=path,
                description=data.get("description", f"Migrated from {entry.key}"),
                created_in_session=session_id,
                topics=_extract_topics(data)
            )
            migrated["artifacts"] += 1
            print(f"   ✅ Migrated artifact: {entry.key}")
            
        else:
            # Unknown structure - skip
            migrated["skipped"] += 1
            print(f"   ⚠️  Skipped (unknown structure): {entry.key}")
    
    print(f"\n📊 Migration Summary:")
    print(f"   Conventions: {migrated['conventions']}")
    print(f"   Decisions: {migrated['decisions']}")
    print(f"   Learnings: {migrated['learnings']}")
    print(f"   Artifacts: {migrated['artifacts']}")
    print(f"   Skipped: {migrated['skipped']}")
    print(f"\n✅ Migration complete! Old entries preserved in .state/memory/")
    print(f"   New structured data in .state/knowledge/ and .state/conversations/")

def _extract_topics(data: dict) -> list[str]:
    """Extract topics from various formats."""
    topics = data.get("topics", data.get("tags", []))
    if isinstance(topics, str):
        # Handle comma-separated strings
        return [t.strip() for t in topics.split(",") if t.strip()]
    elif isinstance(topics, list):
        return topics
    return []

def _extract_confidence(data: dict) -> float:
    """Extract confidence score from various formats."""
    conf = data.get("confidence", 1.0)
    if isinstance(conf, str):
        # Handle "high", "medium", "low"
        mapping = {"high": 0.9, "medium": 0.7, "low": 0.5}
        return mapping.get(conf.lower(), 0.8)
    return float(conf)

def _extract_list(value) -> list[str]:
    """Convert various formats to list."""
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return []

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_memory.py <project_path>")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    if not project_path.exists():
        print(f"Error: {project_path} does not exist")
        sys.exit(1)
    
    migrate_memory(project_path)
```

**Usage:**
```bash
python migrate_memory.py /path/to/your/project
```

---

## Search Migration

### Before: Substring Search
```python
store = SimpleMemoryStore(project_path=Path("."))
results = store.search("authentication")  # Substring matching only
for entry in results:
    print(entry.data)
```

### After: Semantic Search
```python
uacs = UACS(project_path=Path("."))

# Natural language search
results = uacs.search("how did we implement authentication?", limit=5)

# Type-filtered search
decisions = uacs.search(
    "authentication method",
    types=["decision"],
    limit=3
)

# Confidence-filtered search
high_confidence = uacs.search(
    "security best practices",
    types=["convention", "learning"],
    min_confidence=0.9
)

# Session-specific search
session_results = uacs.search(
    "security patterns",
    session_id="security_session_001"
)

for result in results:
    print(f"[{result.type}] {result.relevance_score:.2f} - {result.content}")
```

---

## CLI Migration

### Before: SimpleMemoryStore CLI
```bash
# Initialize memory
uacs memory init --scope project

# Store entry
# (No CLI for storing - must use Python API)

# Search
uacs memory search "authentication"

# Stats
uacs memory stats
```

### After: Semantic API (use Python for now)
```python
# Create a quick script for CLI-like usage
from pathlib import Path
from uacs import UACS

uacs = UACS(project_path=Path("."))

# Add knowledge
uacs.add_convention(
    content="Always use RS256 for JWT signing",
    topics=["security", "jwt"]
)

# Search
results = uacs.search("security", limit=10)
for r in results:
    print(f"{r.type}: {r.content}")

# Stats
stats = uacs.get_stats()
print(f"Decisions: {stats['semantic']['knowledge']['decisions']}")
print(f"Conventions: {stats['semantic']['knowledge']['conventions']}")
```

**Future:** A new `uacs knowledge` CLI command will be added in v0.4.0.

---

## Troubleshooting

### Issue: Import Error
```python
ModuleNotFoundError: No module named 'uacs'
```

**Solution:** Install UACS:
```bash
pip install universal-agent-context
# OR for development
pip install -e .
```

### Issue: DeprecationWarning
```
DeprecationWarning: SimpleMemoryStore is deprecated...
```

**Solution:** This is expected - migrate to Semantic API to remove the warning.

### Issue: Missing session_id
```python
ValidationError: field required (session_id)
```

**Solution:** Decisions, tool uses, and messages require a session ID:
```python
uacs.add_decision(
    question="...",
    decision="...",
    rationale="...",
    decided_by="team",
    session_id="my_session_001",  # Required
    topics=["topic1"]
)
```

### Issue: learned_from validation error
```python
ValidationError: Learning must be derived from at least one session
```

**Solution:** Learnings must reference at least one session:
```python
uacs.add_learning(
    pattern="...",
    confidence=0.9,
    learned_from=["session_001"],  # At least one required
    category="security"
)
```

---

## Next Steps

1. ✅ Review this migration guide
2. ✅ Run the migration script on your project
3. ✅ Test semantic search on migrated data
4. ✅ Update your code to use UACS Semantic API
5. ✅ Remove SimpleMemoryStore usage before v1.0.0

---

## Examples

See working examples in the `examples/` directory:
- `examples/01_semantic_basics.py` - Core API usage
- `examples/04_search_and_knowledge.py` - Advanced search patterns

---

## Support

- **Documentation:** [docs/API_REFERENCE.md](API_REFERENCE.md)
- **Issues:** https://github.com/kylebrodeur/universal-agent-context/issues
- **Migration Help:** Create an issue with the `migration` label

---

**Last Updated:** 2026-02-03  
**UACS Version:** v0.3.0+
