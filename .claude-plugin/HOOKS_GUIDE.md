# UACS Semantic Hooks Guide (v0.3.0)

This guide explains the UACS semantic hooks that automatically capture conversation context during Claude Code sessions.

## Overview

UACS v0.3.0 introduces **semantic hooks** that use the new structured API to capture:
- **User messages** with topic extraction
- **Tool executions** with full context
- **Decisions & conventions** from conversations

All data is stored with embeddings for semantic search.

## Available Hooks

### 1. UserPromptSubmit Hook (`uacs_capture_message.py`)

**Fires:** On every user prompt
**Purpose:** Capture user messages with automatic topic extraction

**What it does:**
- Extracts topics from user prompt using heuristics (testing, security, feature, bug-fix, etc.)
- Stores message using `add_user_message()` semantic API
- Enables searching: "what did the user ask about authentication?"

**Example:**
```json
{
  "prompt": "Help me implement JWT authentication",
  "session_id": "abc123",
  "turn": 1
}
```

**Result:**
- UserMessage created with topics: ["security", "feature"]
- Indexed with embeddings for semantic search

### 2. PostToolUse Hook (`uacs_store_realtime.py`)

**Fires:** After each tool execution (Bash, Edit, Write, Read, Grep, Glob)
**Purpose:** Store tool usage incrementally (survives crashes)

**What it does:**
- Captures tool name, input, response, latency, and success status
- Stores using `add_tool_use()` semantic API
- More reliable than SessionEnd (incremental storage)

**Example:**
```json
{
  "tool_name": "Edit",
  "tool_input": {"file_path": "src/auth.py"},
  "tool_response": "File edited successfully",
  "session_id": "abc123",
  "turn": 2,
  "latency_ms": 150,
  "success": true
}
```

**Result:**
- ToolUse created with all metadata
- Indexed for searching: "when did we edit auth.py?"

### 3. SessionEnd Hook (`uacs_extract_knowledge.py`)

**Fires:** When session ends (exit, timeout, crash recovery)
**Purpose:** Extract decisions and conventions from completed conversation

**What it does:**
- Analyzes assistant messages for decision patterns:
  - "We decided to use X because Y"
  - "I chose X over Y because Z"
  - "We'll use X since Y"
- Extracts convention patterns:
  - "We always X"
  - "The convention is to X"
  - "Best practice is to X"
- Stores using `add_decision()` and `add_convention()` semantic APIs

**Example:**
```json
{
  "session_id": "abc123",
  "messages": [
    {"role": "assistant", "content": "We decided to use JWT tokens because they're stateless..."}
  ]
}
```

**Result:**
- Decision created: "Use JWT tokens" (rationale: "stateless")
- Convention created: "We always use httpOnly cookies for tokens"
- Indexed for searching: "why did we choose JWT?"

## Installation

### Option 1: Use Existing Plugin Configuration

Copy the semantic plugin config:
```bash
cp .claude-plugin/plugin-semantic.json .claude-plugin/plugin.json
```

### Option 2: Manual Configuration

Add to your `.claude-plugin/plugin.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude-plugin/hooks/uacs_capture_message.py",
            "async": true,
            "timeout": 2,
            "description": "Capture user messages (v0.3.0)"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash|Edit|Write|Read|Grep|Glob",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude-plugin/hooks/uacs_store_realtime.py",
            "async": true,
            "timeout": 5,
            "description": "Store tool usage (v0.3.0)"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude-plugin/hooks/uacs_extract_knowledge.py",
            "async": true,
            "timeout": 10,
            "description": "Extract decisions/conventions (v0.3.0)"
          }
        ]
      }
    ]
  }
}
```

## Hook Architecture

### Input (stdin)

Hooks receive JSON from Claude Code:

```json
{
  "prompt": "user message...",
  "session_id": "abc123",
  "project_dir": "/path/to/project",
  "turn": 1,
  "tool_name": "Edit",
  "tool_input": {...},
  "tool_response": "..."
}
```

### Output (stdout)

Hooks must return JSON:

```json
{
  "continue": true,
  "message": "UACS v0.3.0: Stored successfully",
  "error": "optional error message"
}
```

- `continue: true` → Proceed normally
- `continue: false` → Block execution (use carefully!)
- All hooks are non-blocking (errors don't interrupt Claude)

### Error Handling

All hooks have try/catch to prevent interrupting the user:

```python
except Exception as e:
    return {
        "continue": True,  # Always continue
        "error": str(e),
        "message": "UACS: Failed (non-critical)"
    }
```

## Semantic API Methods Used

The hooks use these methods from `uacs.api.UACS`:

### `add_user_message()`
```python
uacs.add_user_message(
    content="Help with auth",
    turn=1,
    session_id="abc123",
    topics=["security", "feature"]
)
```

### `add_tool_use()`
```python
uacs.add_tool_use(
    tool_name="Edit",
    tool_input={"file": "auth.py"},
    tool_response="Success",
    turn=2,
    session_id="abc123",
    latency_ms=150,
    success=True
)
```

### `add_decision()`
```python
uacs.add_decision(
    question="Which auth method?",
    decision="JWT tokens",
    rationale="Stateless and scalable",
    session_id="abc123",
    alternatives=["Session-based"]
)
```

### `add_convention()`
```python
uacs.add_convention(
    content="We always use httpOnly cookies",
    source_session="abc123",
    confidence=0.8
)
```

## Storage Location

All data is stored in `.state/`:
```
.state/
├── conversations/          # User messages, tool uses
│   └── conversation_*.json
├── knowledge/             # Decisions, conventions, learnings
│   └── knowledge/*.json
└── embeddings/            # FAISS index for semantic search
    ├── index.faiss
    └── metadata.json
```

## Searching Captured Context

Use the semantic search API:

```python
from uacs import UACS
from pathlib import Path

uacs = UACS(project_path=Path("."))

# Search across all context
results = uacs.search("how did we implement authentication?", limit=10)

for result in results:
    print(f"{result.metadata['type']}: {result.text}")
    print(f"Relevance: {result.similarity:.2f}\n")
```

## Testing Hooks

Run the test suite:

```bash
uv run python /path/to/test_hooks.py
```

Or test individual hooks:

```bash
echo '{"prompt": "test", "session_id": "123", "cwd": ".", "turn": 1}' | \
  python3 .claude-plugin/hooks/uacs_capture_message.py
```

## Migrating from Old Hooks

### Old API (deprecated):
```python
uacs.add_to_context(
    key="tool_123",
    content="Used Edit tool...",
    topics=["code"]
)
```

### New Semantic API (v0.3.0):
```python
uacs.add_tool_use(
    tool_name="Edit",
    tool_input={...},
    tool_response="...",
    turn=2,
    session_id="123"
)
```

**Benefits of new API:**
- ✅ Structured data (not free-form text)
- ✅ Better semantic search (typed entities)
- ✅ Automatic embeddings for all fields
- ✅ Decision/convention extraction

## Troubleshooting

### Hook not firing?

1. Check plugin.json is loaded: `cat .claude-plugin/plugin.json`
2. Verify hook is executable: `chmod +x .claude-plugin/hooks/*.py`
3. Test hook manually with sample JSON

### Hook errors?

Check Claude Code output for hook messages. All hooks return `continue: true` even on error, so they won't block execution.

### No data stored?

1. Check `.state/` directory exists
2. Verify UACS v0.3.0+ is installed: `pip show universal-agent-context`
3. Run hooks manually to see error messages

## Performance

- **UserPromptSubmit**: ~5ms (fast topic extraction with heuristics)
- **PostToolUse**: ~10-50ms (depends on embedding model warmup)
- **SessionEnd**: ~100-500ms (regex extraction + multiple writes)

All hooks are async (non-blocking) - they won't slow down Claude Code.

## Next Steps

1. **Install hooks**: Copy `plugin-semantic.json` to `plugin.json`
2. **Start Claude Code**: Hooks will fire automatically
3. **Query context**: Use `uacs.search()` to find captured knowledge
4. **Customize**: Modify topic extraction or decision patterns to match your needs

## Support

- GitHub: https://github.com/kylebrodeur/universal-agent-context
- Docs: See README.md for full API reference
