# Trace Visualization Implementation Status

**Created:** 2026-02-01
**Status:** Backend Complete, Frontend Pending

---

## What's Implemented ✅

### Backend (Python)

1. **Data Models** (`src/uacs/visualization/models.py`)
   - ✅ Session model
   - ✅ Event model (tool_use, user_prompt, assistant_response, compression)
   - ✅ EventType and CompressionTrigger enums
   - ✅ Analytics models (TokenAnalytics, TopicAnalytics, CompressionAnalytics)
   - ✅ Search models

2. **Storage Layer** (`src/uacs/visualization/storage.py`)
   - ✅ JSONL-based storage (append-only, simple)
   - ✅ Session CRUD operations
   - ✅ Event CRUD operations
   - ✅ Pagination support
   - ✅ Search across sessions and events
   - ✅ Analytics calculation (tokens, topics, compression)

3. **Web Server** (`src/uacs/visualization/web_server.py`)
   - ✅ Existing FastAPI server
   - ⏳ **TODO:** Add new trace visualization API endpoints
   - ⏳ **TODO:** Add Session/Event endpoints
   - ⏳ **TODO:** Add Analytics endpoints
   - ⏳ **TODO:** Add Search endpoint

---

## What's Pending ⏳

### Backend APIs (Next Step)

Add these endpoints to `web_server.py`:

```python
# Session APIs
GET /api/sessions                    # List sessions
GET /api/sessions/{session_id}       # Get session details
GET /api/sessions/{session_id}/events # Get session events
GET /api/sessions/{session_id}/export # Export session

# Event APIs
GET /api/events                      # List all events
GET /api/events/{event_id}           # Get event details

# Analytics APIs
GET /api/analytics/tokens            # Token analytics
GET /api/analytics/topics            # Topic clusters
GET /api/analytics/compression       # Compression stats

# Search API
POST /api/search                     # Search sessions/events
```

### Frontend (React + Vite)

**TODO:** Build frontend with:
1. Session list view
2. Session detail with timeline
3. Event inspector
4. Topic explorer
5. Token dashboard

---

## MCP Integration Status

### MCP Server (`src/uacs/protocols/mcp/skills_server.py`)

**Already Implemented:** ✅
- `uacs_search_context` - Search stored Claude Code conversations
- `uacs_list_topics` - List all topics
- `uacs_get_recent_sessions` - Get recent sessions

**Works with Plugin:** ✅ YES
- Plugin stores sessions via SessionEnd/PostToolUse hooks
- MCP server reads from same storage (.state/context/)
- Should work out of the box

### Testing MCP + Plugin Integration

**Quick Test:**
```bash
# 1. Start Claude Code with plugin
claude

# 2. Have a conversation (plugin stores context)
> User: Help me implement authentication
> Claude: [responds, uses tools]

# 3. Exit session (SessionEnd hook fires)
> exit

# 4. Test MCP tools via Claude Code
claude --mcp-server uacs

# 5. Use MCP tool to retrieve context
> User: Use uacs_search_context to find "authentication"
> Claude: [calls MCP tool, retrieves stored context]
```

---

## Next Steps (Priority Order)

### 1. Quick Start Guide (User Requested) ⏭️
- Document how to install and test proactive plugin
- Include transformers installation
- Show example session

### 2. README Updates (User Requested) ⏭️
- Add proactive plugin features
- Add transformers requirement
- Add trace visualization overview

### 3. Installation Instructions (User Requested) ⏭️
- Add `pip install transformers torch` to docs
- Optional: Add TinyLlama model download instructions

### 4. Complete Trace Visualization (After User Requests 1-3)
- Finish web_server.py API endpoints
- Build React frontend
- Test with real Claude Code sessions

---

## Integration Architecture

```
Claude Code Session
       │
       ├─> UserPromptSubmit Hook (uacs_monitor_context.py)
       │   └─> Creates Event (type: user_prompt)
       │
       ├─> PostToolUse Hook (uacs_store_realtime.py)
       │   └─> Creates Event (type: tool_use)
       │
       ├─> UserPromptSubmit Hook (uacs_tag_prompt.py)
       │   └─> Adds topics to Event
       │
       ├─> [50% threshold]
       │   └─> Creates Event (type: compression, trigger: early_compression)
       │
       └─> SessionEnd Hook (uacs_store.py)
           └─> Creates Session + Final Events

Storage (.state/context/)
       │
       ├─> sessions.jsonl  (one Session per line)
       └─> events.jsonl    (one Event per line)

Visualization Server (FastAPI)
       │
       ├─> TraceStorage reads JSONL files
       ├─> Exposes REST APIs (/api/sessions, /api/events, etc.)
       └─> Serves React frontend (static/index.html)

MCP Server
       │
       ├─> Reads same storage (.state/context/)
       ├─> Exposes uacs_search_context, uacs_list_topics tools
       └─> Claude Code can query stored context via MCP
```

---

## File Locations

### Backend
- `src/uacs/visualization/models.py` ✅
- `src/uacs/visualization/storage.py` ✅
- `src/uacs/visualization/web_server.py` ⏳ (needs API updates)

### Hooks
- `.claude-plugin/hooks/uacs_monitor_context.py` ✅
- `.claude-plugin/hooks/uacs_tag_prompt.py` ✅
- `.claude-plugin/hooks/uacs_store_realtime.py` ✅ (existing)
- `.claude-plugin/hooks/uacs_store.py` ✅ (existing)

### Frontend (Pending)
- `src/uacs/visualization/frontend/` ⏳
- `src/uacs/visualization/frontend/src/App.tsx` ⏳
- `src/uacs/visualization/frontend/src/components/` ⏳

### Documentation
- `.github/TRACE_VISUALIZATION_DESIGN.md` ✅
- `.github/TRACE_VIZ_IMPLEMENTATION_STATUS.md` ✅ (this file)

---

## Testing Plan

### Phase 1: Test MCP + Plugin
1. Install plugin: `cp .claude-plugin/plugin-proactive.json .claude/plugin.json`
2. Run Claude Code session
3. Verify hooks create events in `.state/context/events.jsonl`
4. Verify MCP tools can read stored context

### Phase 2: Test Trace Storage
1. Run Claude Code session
2. Check `.state/context/sessions.jsonl` has session entry
3. Check `.state/context/events.jsonl` has event entries
4. Use Python to load Session/Event models

### Phase 3: Test Visualization APIs (After API Implementation)
1. Start visualization server
2. Hit `/api/sessions` and verify response
3. Hit `/api/events?session_id=xxx` and verify events
4. Hit `/api/analytics/tokens` and verify stats

### Phase 4: Test Frontend (After Frontend Implementation)
1. Open http://localhost:8081 in browser
2. See session list
3. Click session to see trace
4. Click event to see details

---

## Summary

**Status:**
- ✅ Backend models and storage complete
- ✅ MCP server should work with plugin (needs testing)
- ⏳ API endpoints need to be added to web_server.py
- ⏳ Frontend needs to be built

**User's Priority:**
1. ✅ MCP app works with plugin (should work, needs testing)
2. ⏳ Visualization improved (backend done, APIs + frontend pending)
3. ⏭️ Quick start guide (next task)
4. ⏭️ README updates (next task)
5. ⏭️ Installation instructions (next task)

Let's complete items 3-5 first (as user requested), then come back to finish trace visualization!
