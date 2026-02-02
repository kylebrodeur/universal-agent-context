# Claude Code Integration - Real Implementation TODO

**Status:** 🚧 Not Yet Built (We only have simulation demo)
**Priority:** 🔥 Critical for "Killer Use Case" claim
**Estimated Time:** 4-6 hours

---

## Problem

We claim Claude Code integration as "the killer use case" but only have a simulation demo. To make this real, we need to build an actual Claude Code plugin with hooks.

---

## Solution Architecture

```
┌─────────────────────────────────────────┐
│   Claude Code Session                   │
│                                         │
│  User → Claude → Tools → Response       │
└────────────────────┬────────────────────┘
                     │
          ┌──────────▼──────────┐
          │  SessionEnd Hook    │  ← We need to build this
          │  (fires on session  │
          │   completion)       │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ UACS Hook Script    │  ← We need to build this
          │ • Read transcript   │
          │ • Extract topics    │
          │ • Call UACS SDK     │
          │ • Store with 100%   │
          │   fidelity          │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ UACS Backend        │  ← Already exists!
          │ (Python SDK)        │
          └─────────────────────┘
```

---

## What We Need to Build

### 1. Claude Code Hook Script (2 hours)

**File:** `.claude/hooks/uacs_store.py`

```python
#!/usr/bin/env python3
"""
UACS Hook for Claude Code - Automatic Context Storage

This hook fires on SessionEnd and stores the full conversation
in UACS with perfect fidelity.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def store_session_to_uacs(hook_input: dict):
    """Store Claude Code session in UACS.

    Args:
        hook_input: JSON from Claude Code hook containing:
            - transcript_path: Path to session transcript
            - session_id: Unique session identifier
            - project_dir: Current project directory

    Returns:
        JSON with continue: true/false
    """
    try:
        # Import UACS (lazy import to avoid startup cost)
        from uacs import UACS

        # Get hook inputs
        transcript_path = hook_input.get('transcript_path')
        session_id = hook_input.get('session_id')
        project_dir = hook_input.get('project_dir', '.')

        if not transcript_path:
            return {"continue": True, "error": "No transcript path"}

        # Read transcript (JSONL format)
        transcript = read_transcript(Path(transcript_path))

        if not transcript:
            return {"continue": True, "error": "Empty transcript"}

        # Initialize UACS for this project
        uacs = UACS(project_path=Path(project_dir))

        # Extract conversation content
        full_conversation = format_conversation(transcript)

        # Extract topics (simple heuristics for now)
        topics = extract_topics(full_conversation)

        # Store in UACS
        uacs.add_to_context(
            key=f"session_{session_id}",
            content=full_conversation,
            topics=topics,
            metadata={
                'session_id': session_id,
                'stored_at': datetime.now().isoformat(),
                'turn_count': len(transcript),
                'source': 'claude-code-hook'
            }
        )

        # Success
        return {
            "continue": True,
            "message": f"Stored session {session_id} in UACS ({len(topics)} topics)"
        }

    except Exception as e:
        # Graceful degradation - don't break Claude Code
        return {
            "continue": True,
            "error": str(e),
            "message": "UACS storage failed (non-critical)"
        }

def read_transcript(path: Path) -> list:
    """Read JSONL transcript file."""
    if not path.exists():
        return []

    transcript = []
    with open(path) as f:
        for line in f:
            if line.strip():
                transcript.append(json.loads(line))
    return transcript

def format_conversation(transcript: list) -> str:
    """Format transcript into readable conversation."""
    parts = []
    for turn in transcript:
        role = turn.get('role', 'unknown')
        content = turn.get('content', '')

        if isinstance(content, list):
            # Handle structured content (text + tool uses)
            text_parts = [c.get('text', '') for c in content if c.get('type') == 'text']
            content = ' '.join(text_parts)

        parts.append(f"[{role}] {content}")

    return "\n\n".join(parts)

def extract_topics(content: str) -> list[str]:
    """Extract topics from conversation using simple heuristics.

    TODO: Could use Claude API for better extraction in future.
    """
    topics = set()

    # Technical terms indicate topics
    keywords = {
        'security': ['security', 'vulnerability', 'attack', 'injection', 'xss'],
        'performance': ['performance', 'slow', 'optimize', 'speed', 'n+1'],
        'testing': ['test', 'pytest', 'unittest', 'coverage'],
        'refactor': ['refactor', 'clean', 'technical debt'],
        'bug': ['bug', 'error', 'crash', 'fail'],
        'feature': ['feature', 'implement', 'add'],
        'documentation': ['document', 'readme', 'comment'],
    }

    content_lower = content.lower()
    for topic, terms in keywords.items():
        if any(term in content_lower for term in terms):
            topics.add(topic)

    # Default topic
    if not topics:
        topics.add('general')

    return list(topics)

if __name__ == '__main__':
    # Claude Code hooks receive JSON via stdin
    input_data = json.load(sys.stdin)
    result = store_session_to_uacs(input_data)
    print(json.dumps(result))
    sys.exit(0)  # Exit 0 = continue, exit 2 = block
```

---

### 2. Plugin Manifest (30 minutes)

**File:** `.claude-plugin/plugin.json`

```json
{
  "name": "uacs",
  "version": "0.1.0",
  "description": "Universal Agent Context System - Perfect recall for Claude Code conversations",
  "author": "Kyle Brodeur",
  "repository": "https://github.com/kylebrodeur/universal-agent-context",

  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/uacs_store.py",
            "async": true,
            "description": "Store conversation in UACS"
          }
        ]
      }
    ]
  },

  "skills": [
    {
      "name": "UACS Context Management",
      "path": ".claude/skills/uacs.md"
    }
  ],

  "mcpServers": {
    "uacs": {
      "command": "uacs",
      "args": ["serve"],
      "description": "UACS MCP server for context retrieval"
    }
  },

  "dependencies": {
    "python": ">=3.11",
    "packages": ["universal-agent-context"]
  }
}
```

---

### 3. Skill Definition (15 minutes)

**File:** `.claude/skills/uacs.md`

```markdown
# UACS Context Management

You have access to UACS (Universal Agent Context System) for perfect conversation recall.

## What UACS Does

- Automatically stores all your conversations with 100% fidelity
- Retrieves context by topic when needed
- Never loses details to summarization

## When to Use

- Reference past conversations: "What did we discuss about security?"
- Retrieve specific details: "What was that line number for the SQL injection?"
- Focus on topics: "Show me all performance issues"

## How to Retrieve Context

Use the UACS MCP tools:

- `uacs_search_context(query: str, topics: list[str])` - Search stored conversations
- `uacs_get_context(topic: str, max_tokens: int)` - Get focused context

## Example

```
User: "What security issues did we find?"
Claude: Let me check UACS for security discussions...
[uses uacs_search_context with topics=["security"]]
Claude: We found 3 issues: SQL injection at line 42, timing attack at line 78...
```

## Benefits

- Perfect recall across sessions
- No context resets
- Find exactly what you need by topic
```

---

### 4. MCP Server for Retrieval (1 hour)

**File:** `src/uacs/mcp/claude_code_tools.py`

Add these tools to the existing MCP server:

```python
@mcp.tool()
async def uacs_search_context(
    query: str,
    topics: list[str] | None = None,
    max_tokens: int = 4000
) -> str:
    """Search UACS for stored Claude Code conversations.

    Args:
        query: What to search for
        topics: Optional topic filters (security, performance, etc.)
        max_tokens: Maximum tokens to return

    Returns:
        Relevant conversation context with perfect fidelity
    """
    uacs = get_uacs_instance()

    context = uacs.build_context(
        query=query,
        topics=topics,
        max_tokens=max_tokens,
        agent="claude"
    )

    return context

@mcp.tool()
async def uacs_list_topics() -> list[str]:
    """List all topics in stored conversations.

    Returns:
        List of topic tags
    """
    uacs = get_uacs_instance()

    # Get all unique topics
    topics = set()
    for entry in uacs.shared_context.entries.values():
        topics.update(entry.topics)

    return sorted(list(topics))
```

---

### 5. Installation Script (30 minutes)

**File:** `scripts/install_claude_plugin.sh`

```bash
#!/bin/bash
# Install UACS as Claude Code plugin

set -e

echo "🚀 Installing UACS Claude Code Plugin..."

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ required"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo "❌ Claude Code CLI required"
    exit 1
fi

# Install UACS Python package
echo "📦 Installing UACS Python package..."
pip install universal-agent-context

# Copy plugin files to .claude directory
echo "📁 Setting up plugin files..."
mkdir -p .claude/hooks
mkdir -p .claude/skills

cp .claude-plugin/hooks/uacs_store.py .claude/hooks/
cp .claude-plugin/skills/uacs.md .claude/skills/
chmod +x .claude/hooks/uacs_store.py

# Install plugin via Claude CLI
echo "🔌 Registering plugin with Claude Code..."
claude /plugin install .

echo "✅ UACS plugin installed!"
echo ""
echo "Next steps:"
echo "  1. Start a Claude Code session: claude"
echo "  2. Conversations will be automatically stored in UACS"
echo "  3. Search with: @uacs_search_context"
```

---

### 6. Testing Script (1 hour)

**File:** `tests/test_claude_code_integration.py`

```python
"""Test Claude Code integration."""

import json
import subprocess
from pathlib import Path
import tempfile

def test_hook_stores_session():
    """Test that SessionEnd hook stores to UACS."""

    # Create mock transcript
    transcript = [
        {"role": "user", "content": "Review auth.py for security"},
        {"role": "assistant", "content": "Found SQL injection at line 42"}
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl') as f:
        for turn in transcript:
            f.write(json.dumps(turn) + '\n')
        f.flush()

        # Simulate hook input
        hook_input = {
            "transcript_path": f.name,
            "session_id": "test-session-123",
            "project_dir": "."
        }

        # Run hook script
        result = subprocess.run(
            ["python", ".claude/hooks/uacs_store.py"],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        # Check success
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["continue"] == True
        assert "Stored session" in output.get("message", "")

def test_topic_extraction():
    """Test topic extraction from conversation."""
    from uacs.hooks.uacs_store import extract_topics

    content = "Found SQL injection and XSS vulnerability. Need to optimize performance."
    topics = extract_topics(content)

    assert "security" in topics
    assert "performance" in topics
```

---

## Implementation Priority

### Phase 1: Core Hook (4 hours)
1. ✅ Hook script (`uacs_store.py`)
2. ✅ Plugin manifest
3. ✅ Installation script
4. ✅ Basic testing

**Result:** Automatic storage working

### Phase 2: Retrieval (2 hours)
1. ✅ MCP tools for search
2. ✅ Skill definition
3. ✅ Integration testing

**Result:** Bidirectional integration (store + retrieve)

### Phase 3: Polish (2 hours)
1. ✅ Better topic extraction (optional: use Claude API)
2. ✅ Error handling improvements
3. ✅ Documentation
4. ✅ Demo video showing real integration

**Result:** Production-ready plugin

---

## Launch Implications

### Current State
- ❌ README claims "works with Claude Code"
- ❌ Blog post templates mention automatic storage
- ❌ "Killer use case" is only a simulation

### Honest v0.1.0 Messaging

**What to say:**

> "UACS provides perfect context storage for AI conversations. We have a proof-of-concept integration with Claude Code using hooks. The Claude Code plugin is in active development (Phase 1 complete, Phase 2 in progress). You can use UACS manually today, with automatic integration coming soon."

**What NOT to say:**

> ~~"Never lose Claude Code context"~~ (not automatic yet)
> ~~"Seamless Claude Code integration"~~ (still building it)
> ~~"Drop-in replacement"~~ (requires plugin installation + setup)

---

## Alternative: Launch Without Claude Code Integration

### Option 1: Launch v0.1.0 with manual UACS only
- Focus on MCP server for Claude Desktop (this works!)
- Focus on Cursor/Windsurf (this works!)
- Label Claude Code as "Coming in v0.2.0"

### Option 2: Build the plugin first, then launch
- 4-6 hours to build Phase 1
- Test with real Claude Code sessions
- Launch with working automatic storage

### Option 3: Launch with simulation + roadmap
- Keep simulation demo
- Add clear "Future Work" section
- Show proof-of-concept, promise real integration

---

## Recommendation

**Build Phase 1 (4 hours) before v0.1.0 launch** so you can honestly claim:

✅ "Automatic Claude Code integration via plugin"
✅ "Store every conversation with SessionEnd hook"
✅ "Perfect fidelity, zero loss"

This makes your "killer use case" real, not just a design doc.

**Time investment:** 4 hours to go from simulation → production
**Value:** Can honestly claim automatic Claude Code storage
**Risk:** v0.1.0 launch delayed by 1 day

---

## Next Steps

1. **Decision:** Build now or launch without it?
2. **If build now:** Start with `.claude/hooks/uacs_store.py` (2 hours)
3. **If launch without:** Update docs to say "coming soon"

Your call! 🚀
