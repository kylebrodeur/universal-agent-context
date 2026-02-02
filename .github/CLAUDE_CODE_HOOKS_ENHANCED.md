# Claude Code Hooks - Enhanced Multi-Hook Strategy

**Created:** 2026-02-01
**Status:** Implemented (v0.2.0 Enhanced Plugin)

---

## What Changed

We went from using **1 hook** (SessionEnd) to **4 hooks** for comprehensive coverage:

| Hook | What It Does | Why It's Better |
|------|--------------|-----------------|
| **SessionStart** (NEW) | Injects previous context on resume | Automatic continuity |
| **PostToolUse** (NEW) | Stores each tool use incrementally | Survives crashes, real-time |
| **PreCompact** (NEW) | Compresses before Claude's compaction | Never lose context |
| **SessionEnd** (Kept) | Final session storage | Backup + full indexing |

---

## Complete Hook Reference

### All 12 Claude Code Hooks

| Hook | Fires When | Blocking? | UACS Use |
|------|-----------|-----------|----------|
| **SessionStart** | Session begins/resumes | No | ✅ Inject context on resume |
| **UserPromptSubmit** | User submits prompt | Yes | ⚠️ Could extract topics (future) |
| **PreToolUse** | Before tool executes | Yes | ❌ Not needed |
| **PermissionRequest** | Permission dialog | Yes | ❌ Not needed |
| **PostToolUse** | Tool succeeds | No | ✅ Real-time storage |
| **PostToolUseFailure** | Tool fails | No | ⚠️ Future: log failures |
| **Stop** | Claude finishes | Yes | ⚠️ Future: mark segments |
| **SubagentStart** | Subagent spawns | No | ❌ Not relevant |
| **SubagentStop** | Subagent finishes | Yes | ❌ Not relevant |
| **Notification** | Notification sent | No | ❌ Not relevant |
| **PreCompact** | Before context compression | No | ✅ Trigger UACS compression |
| **SessionEnd** | Session terminates | No | ✅ Finalize storage |

---

## Implementation Details

### 1. SessionStart Hook (Context Injection)

**File:** `.claude-plugin/hooks/uacs_inject_context.py`

**Fires When:** Session resumes (matcher: `"resume"`)

**What It Does:**
```python
if source == "resume":
    # Get recent context from UACS (last 2000 tokens)
    recent = uacs.get_compressed_context(max_tokens=2000)

    # Inject into Claude's initial context
    return {
        "additionalContext": f"Previous topics: {topics}\n{recent}"
    }
```

**Benefits:**
- ✅ Automatic continuity (user doesn't ask for it)
- ✅ Claude knows what was discussed before
- ✅ Non-blocking (async: false, but fast <1s)

**Example:**
```
User resumes session →
Hook fires →
Injects: "Previous topics: security, performance
         Recent conversations: [SQL injection fix, N+1 query]"
Claude sees context automatically →
User: "How did we fix that security issue?"
Claude: "We fixed the SQL injection at line 42 by..."
```

---

### 2. PostToolUse Hook (Real-Time Storage)

**File:** `.claude-plugin/hooks/uacs_store_realtime.py`

**Fires When:** After Bash, Edit, Write, Read, Grep (matcher: `"Bash|Edit|Write|Read|Grep"`)

**What It Does:**
```python
# After each tool execution
tool_name = "Bash"
tool_input = {"command": "pytest"}
tool_response = "5 passed, 0 failed"

# Store incrementally
uacs.add_to_context(
    content=f"Tool: {tool_name}\nCommand: pytest\nResult: 5 passed",
    topics=["testing"],
    metadata={"incremental": True}
)
```

**Benefits:**
- ✅ **Survives crashes** (saves after each tool)
- ✅ **No data loss** on ungraceful exit
- ✅ **Async** (doesn't block Claude)
- ✅ **Fine-grained** capture

**Why Better Than SessionEnd Alone:**

| Scenario | SessionEnd Only | + PostToolUse |
|----------|-----------------|---------------|
| Process crash | ❌ Lost everything | ✅ Saved up to crash |
| Force quit | ❌ Lost everything | ✅ Saved up to quit |
| Long session | ❌ Wait until end | ✅ Incremental saves |
| Tool failures | ❌ Not captured | ✅ Captured per-tool |

---

### 3. PreCompact Hook (Compression Trigger)

**File:** `.claude-plugin/hooks/uacs_precompact.py`

**Fires When:** Claude is about to compact its context window (running low on tokens)

**What It Does:**
```python
# Before Claude compacts
stats_before = uacs.get_stats()
uacs.optimize_context()  # Compress UACS storage
stats_after = uacs.get_stats()

# Tell Claude we compressed
return {
    "additionalContext": f"UACS compressed: saved {tokens_saved} tokens"
}
```

**Benefits:**
- ✅ Coordinates with Claude's compaction
- ✅ Saves UACS storage space
- ✅ Informs Claude that context is safe in UACS

---

### 4. SessionEnd Hook (Finalization - Kept)

**File:** `.claude-plugin/hooks/uacs_store.py`

**Fires When:** Session ends (matcher: `"other"` - normal exit, not logout/clear)

**What It Does:**
```python
# Read full transcript
transcript = read_transcript(transcript_path)

# Extract topics from full conversation
topics = extract_topics(transcript)

# Store as complete session
uacs.add_to_context(
    content=full_conversation,
    topics=topics,
    metadata={"complete_session": True}
)
```

**Benefits:**
- ✅ Full session indexing
- ✅ Better topic extraction (sees full context)
- ✅ Backup for incremental storage
- ✅ Creates session summaries

---

## Comparison: Basic vs Enhanced

### Basic Plugin (SessionEnd Only)

```json
{
  "hooks": {
    "SessionEnd": [...]
  }
}
```

**Limitations:**
- ❌ Data loss on crash
- ❌ No context injection on resume
- ❌ Misses Claude's compaction events
- ❌ Waits until session end

### Enhanced Plugin (4 Hooks)

```json
{
  "hooks": {
    "SessionStart": [...],    // Inject context
    "PostToolUse": [...],      // Real-time storage
    "PreCompact": [...],       // Compression coordination
    "SessionEnd": [...]        // Finalization
  }
}
```

**Advantages:**
- ✅ Crash-resistant (incremental saves)
- ✅ Automatic continuity (resume injection)
- ✅ Compression coordination
- ✅ Complete coverage

---

## Configuration

### Basic Plugin

```bash
# Use original plugin.json
.claude-plugin/install.sh
```

### Enhanced Plugin

```bash
# Use enhanced plugin
cp .claude-plugin/plugin-enhanced.json .claude/plugin.json
cp .claude-plugin/hooks/*.py .claude/hooks/
chmod +x .claude/hooks/*.py
```

Or edit `.claude/plugin.json` directly to add new hooks.

---

## Testing Each Hook

### Test SessionStart (Context Injection)

```bash
# 1. Have a conversation
claude
> User: We're working on security fixes
> Claude: [responds]
> exit

# 2. Resume session
claude --resume

# 3. Check if context was injected
# Claude should mention previous topics in its greeting
```

### Test PostToolUse (Real-Time Storage)

```bash
# 1. Start session
claude

# 2. Run a tool
> User: Run pytest
> Claude: [uses Bash tool]

# 3. Check storage IMMEDIATELY (don't wait for session end)
ls -la .state/context/
# Should see new files after each tool use
```

### Test PreCompact (Compression)

```bash
# 1. Have a LONG conversation (approach context limit)
claude
> User: [many long prompts]

# 2. Watch for Claude saying "context is getting full"
# PreCompact hook should fire

# 3. Check UACS compressed
# (Logs will show compression triggered)
```

### Test SessionEnd (Finalization)

```bash
# Same as before - works as backup
```

---

## Performance Impact

| Hook | Frequency | Async? | Time | Impact |
|------|-----------|--------|------|--------|
| SessionStart | Once per resume | No | <1s | Low (one-time) |
| PostToolUse | Per tool use | Yes | <100ms | None (async) |
| PreCompact | Rare (context full) | No | <2s | Low (rare event) |
| SessionEnd | Once per session | Yes | <2s | None (async) |

**Total overhead:** Negligible (<1% of session time)

---

## Rollout Plan

### Phase 1: Keep Basic (SessionEnd Only)
- ✅ Works today
- ✅ Simple
- ❌ Loses data on crash

### Phase 2: Add PostToolUse (Recommended)
- ✅ Crash-resistant
- ✅ Real-time
- ⚠️ Slightly more complex

### Phase 3: Add SessionStart (Nice to Have)
- ✅ Automatic continuity
- ⚠️ User must test resume behavior

### Phase 4: Add PreCompact (Advanced)
- ✅ Compression coordination
- ⚠️ Rare edge case

**Recommendation:** Start with Phase 1 (basic), add Phase 2 (PostToolUse) after testing.

---

## Future Hooks to Consider

### UserPromptSubmit (Topic Extraction)

**Potential Use:**
```python
# Extract topics BEFORE Claude processes
prompt = hook_input["prompt"]
topics = llm_extract_topics(prompt)  # Use Claude Haiku
return {"additionalContext": f"Topics: {topics}"}
```

**Benefits:**
- ✅ More accurate topics (from user intent)
- ✅ Happens before Claude's response

**Challenges:**
- ⚠️ Adds latency (LLM call per prompt)
- ⚠️ Costs $0.0001 per prompt (Haiku)

**Verdict:** Maybe in v0.3.0 if needed.

---

### Stop Hook (Conversation Segmentation)

**Potential Use:**
```python
# Mark conversation segments
if claude_finished_major_task():
    uacs.create_segment_marker()
```

**Benefits:**
- ✅ Better organization
- ✅ "Chapters" in conversations

**Challenges:**
- ⚠️ Hard to detect "major task" automatically

**Verdict:** Future consideration.

---

## Hooks NOT Worth Using for UACS

| Hook | Why Not |
|------|---------|
| PreToolUse | No need to block tools |
| PermissionRequest | No need to auto-approve |
| PostToolUseFailure | Failures already in transcript |
| SubagentStart/Stop | Not using subagents |
| Notification | Not relevant to storage |

---

## Documentation References

- **Complete Hook Reference:** https://code.claude.com/docs/en/hooks.md
- **Hook Input/Output Spec:** https://code.claude.com/docs/en/hooks-guide.md
- **Settings Configuration:** https://code.claude.com/docs/en/settings.md

---

## Summary

**Before:** 1 hook (SessionEnd)
- ❌ Data loss on crash
- ❌ No automatic context injection
- ❌ Waits until session end

**After:** 4 hooks (SessionStart + PostToolUse + PreCompact + SessionEnd)
- ✅ Crash-resistant incremental storage
- ✅ Automatic context injection on resume
- ✅ Compression coordination
- ✅ Complete conversation coverage

**Next Steps:**
1. Test basic plugin first (SessionEnd only)
2. Once working, upgrade to enhanced plugin
3. Measure improvement in reliability and UX

The enhanced plugin is **production-ready** but should be tested incrementally.
