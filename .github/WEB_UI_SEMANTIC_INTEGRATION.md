# Web UI + Semantic API Integration Plan (v0.3.0)

**Status:** Ready for Implementation
**Priority:** High
**Estimated Effort:** 8-12 hours
**Dependencies:** Task Groups 1 & 2 Complete ✅

---

## Overview

This document combines **Task Group 3 (Semantic Web UI)** with the existing **Trace Visualization work** to create a unified, comprehensive web interface for UACS v0.3.0.

### What We Have ✅

1. **Semantic API (v0.3.0)** - Complete
   - `UACS` class with unified API in src/uacs/api.py:91-152
   - Methods: `add_user_message()`, `add_assistant_message()`, `add_tool_use()`
   - Knowledge: `add_decision()`, `add_convention()`, `add_learning()`, `add_artifact()`
   - Search: `search()` - Semantic search across all context
   - Storage in `.state/conversations/`, `.state/knowledge/`, `.state/embeddings/`

2. **Claude Code Hooks** - Complete (.claude-plugin/hooks/)
   - `uacs_capture_message.py` - UserPromptSubmit hook (captures messages)
   - `uacs_store_realtime.py` - PostToolUse hook (captures tool executions)
   - `uacs_extract_knowledge.py` - SessionEnd hook (extracts decisions/conventions)
   - All using v0.3.0 semantic API

3. **Web Visualizer (Partial)** - Needs Integration
   - FastAPI server exists (src/uacs/visualization/web_server.py)
   - Frontend exists (src/uacs/visualization/static/index.html)
   - 5 visualization modes (conversation flow, tokens, deduplication, quality, topics)
   - Real-time WebSocket updates
   - **BUT:** Uses old SharedContextManager, not semantic API

4. **Trace Storage Models** - Complete
   - Session and Event models (src/uacs/visualization/models.py)
   - JSONL storage layer (src/uacs/visualization/storage.py)
   - **BUT:** Not integrated with semantic API

### What We Need ⏳

Integrate the semantic API with the web visualizer to create a unified interface that shows:

1. **Semantic Search UI** - Natural language search across conversations and knowledge
2. **Conversation Timeline** - Visualize user messages → assistant responses → tool uses
3. **Knowledge Browser** - Browse decisions, conventions, learnings, and artifacts
4. **Session Traces** - LangSmith-style trace view of Claude Code sessions
5. **API Endpoints** - REST APIs that expose semantic data

---

## Architecture Integration

### Data Flow (New)

```
Claude Code Session
       ↓
Semantic Hooks (v0.3.0)
       ↓
UACS Semantic API
       ↓
Storage (.state/)
   ├── conversations/
   ├── knowledge/
   └── embeddings/
       ↓
Web Server (FastAPI)
       ↓
   [REST API]  ←→  [WebSocket]
       ↓              ↓
   HTTP Response   Live Updates
       ↓              ↓
   Browser (React/Vue/HTML)
       ↓
   User Interface
```

### Storage Structure

```
.state/
├── conversations/              # From ConversationManager
│   ├── conversation_001.json   # UserMessage, AssistantMessage, ToolUse
│   ├── conversation_002.json
│   └── ...
│
├── knowledge/                  # From KnowledgeManager
│   └── knowledge/
│       ├── conventions.json    # Convention objects
│       ├── decisions.json      # Decision objects
│       ├── learnings.json      # Learning objects
│       └── artifacts.json      # Artifact objects
│
└── embeddings/                 # From EmbeddingManager
    ├── index.faiss            # Vector index
    └── metadata.json          # Embedding metadata
```

---

## Task Breakdown

### Phase 1: Backend API Integration (4-5 hours)

#### 1.1 Update Web Server with Semantic Endpoints

**File to modify:** `src/uacs/visualization/web_server.py`

Add new API endpoints that use the semantic API:

**Semantic Search:**
```
POST /api/search
  Body: {"query": "how did we implement authentication?", "types": ["decision"], "limit": 10}
  Returns: List[SearchResult] with similarity scores
```

**Conversation Endpoints:**
```
GET /api/conversations
  Query: ?session_id=xxx&skip=0&limit=20
  Returns: List of conversations with messages

GET /api/conversations/{conversation_id}
  Returns: Full conversation with all messages and tool uses

GET /api/conversations/{conversation_id}/timeline
  Returns: Timeline view (user msg → assistant → tools)
```

**Knowledge Endpoints:**
```
GET /api/knowledge/decisions
  Query: ?session_id=xxx&skip=0&limit=20
  Returns: List[Decision]

GET /api/knowledge/conventions
  Query: ?topics=security&skip=0&limit=20
  Returns: List[Convention]

GET /api/knowledge/learnings
  Query: ?category=security_best_practice
  Returns: List[Learning]

GET /api/knowledge/artifacts
  Query: ?session_id=xxx&type=file
  Returns: List[Artifact]
```

**Session Endpoints (for trace view):**
```
GET /api/sessions
  Query: ?skip=0&limit=20&sort=timestamp_desc
  Returns: List of sessions with metadata

GET /api/sessions/{session_id}
  Returns: Full session with all events (LangSmith-style)

GET /api/sessions/{session_id}/events
  Query: ?type=tool_use&skip=0&limit=50
  Returns: Events timeline for session
```

**Analytics Endpoints:**
```
GET /api/analytics/overview
  Returns: {"total_conversations": 42, "total_knowledge_items": 87, ...}

GET /api/analytics/topics
  Returns: Topic clusters with frequencies

GET /api/analytics/tokens
  Query: ?days=30
  Returns: Token usage over time
```

#### 1.2 Integrate UACS Semantic API

**Current:** Web server uses `SharedContextManager` (old API)
**New:** Web server should use `UACS` semantic API

Implementation pattern:

```python
from uacs import UACS
from pathlib import Path

class VisualizationServer:
    def __init__(self, project_path: Path):
        self.uacs = UACS(project_path=project_path)

    async def search(self, query: str, types: List[str] = None, limit: int = 10):
        """Semantic search endpoint."""
        results = self.uacs.search(
            query=query,
            types=types,
            limit=limit,
            min_confidence=0.7
        )
        return [self._serialize_search_result(r) for r in results]

    async def get_conversations(self, session_id: str = None):
        """Get conversations from ConversationManager."""
        # Access conversation_manager directly from UACS instance
        conversations = self.uacs.conversation_manager.list_conversations(
            session_id=session_id
        )
        return conversations

    async def get_decisions(self, session_id: str = None):
        """Get decisions from KnowledgeManager."""
        decisions = self.uacs.knowledge_manager.list_decisions(
            session_id=session_id
        )
        return decisions
```

#### 1.3 WebSocket Updates for Real-time Data

Add WebSocket broadcasts for:
- New messages captured by hooks
- New decisions/conventions extracted
- Search results updates
- Token usage changes

### Phase 2: Frontend Enhancement (4-5 hours)

#### 2.1 UI Framework Decision

**Option A: Extend Existing HTML (Faster - RECOMMENDED)**
- Add new tabs to existing `static/index.html`
- Use vanilla JavaScript + D3.js/Chart.js (already loaded)
- No build step required
- Consistent with existing visualization
- Estimated time: 4-5 hours

**Option B: React/Vue App (Better UX, More Work)**
- Create `src/uacs/visualization/frontend/` with Vite
- Modern component-based architecture
- Better state management
- Requires build step
- Estimated time: 8-10 hours

**Recommendation:** Start with Option A (extend HTML), migrate to Option B later if needed.

#### 2.2 Required UI Components

**1. Semantic Search Tab**
- Search input with natural language placeholder
- Type filters (checkboxes for: messages, decisions, conventions, artifacts)
- Results list with:
  - Similarity score (0-100%)
  - Content type badge
  - Preview text
  - Click to expand details

**2. Conversation Timeline Tab**
- Session selector dropdown
- Chronological event list:
  - User messages (blue icon)
  - Assistant responses (green icon)
  - Tool executions (orange icon) with latency
  - Decisions/conventions (purple icon)
- Expandable detail view for each event

**3. Knowledge Browser Tab**
- Tab switcher: Decisions | Conventions | Learnings | Artifacts
- **Decisions view:**
  - Question/Decision/Rationale format
  - Alternatives considered (if any)
  - Session link
  - Timestamp
- **Conventions view:**
  - Convention text
  - Source session
  - Confidence level
  - Topics
- **Learnings view:**
  - Pattern description
  - Source sessions
  - Category
  - Confidence score
- **Artifacts view:**
  - File/function/class name
  - Description
  - Created in session
  - Topics

**4. Session Trace View (LangSmith-Style)**
- Sessions list:
  - Session ID + timestamp
  - Duration, turn count, token usage
  - Topics tags
  - Quality score
  - Click to expand
- Session detail:
  - Token usage chart over time
  - Events timeline
  - Compression events highlighted
  - Export button

#### 2.3 Security Considerations

**CRITICAL:** Prevent XSS vulnerabilities

- **DO NOT** use `innerHTML` with untrusted content
- **USE** `textContent` for plain text
- **USE** `createElement()` + `appendChild()` for structured content
- **USE** DOMPurify library if HTML rendering is required
- **SANITIZE** all user input before display
- **ESCAPE** special characters in search queries

Example of secure rendering:
```javascript
// BAD (XSS vulnerability):
container.innerHTML = `<div>${userInput}</div>`;

// GOOD (safe):
const div = document.createElement('div');
div.textContent = userInput;  // Automatically escapes
container.appendChild(div);
```

### Phase 3: Testing & Polish (2-3 hours)

#### 3.1 Integration Tests

Create `tests/test_semantic_web_ui.py`:

```python
import pytest
from fastapi.testclient import TestClient
from uacs.visualization.web_server import create_app
from pathlib import Path

@pytest.fixture
def client():
    app = create_app(project_path=Path("test_project"))
    return TestClient(app)

def test_search_endpoint(client):
    response = client.post("/api/search", json={
        "query": "authentication",
        "types": ["decision", "convention"],
        "limit": 10
    })
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)

def test_conversations_endpoint(client):
    response = client.get("/api/conversations")
    assert response.status_code == 200
    conversations = response.json()
    assert "conversations" in conversations

def test_knowledge_decisions_endpoint(client):
    response = client.get("/api/knowledge/decisions")
    assert response.status_code == 200
    decisions = response.json()
    assert isinstance(decisions, list)

def test_sessions_list_endpoint(client):
    response = client.get("/api/sessions")
    assert response.status_code == 200
    sessions = response.json()
    assert "sessions" in sessions
    assert "total" in sessions
```

#### 3.2 UI Polish Checklist

- [ ] Add loading states (spinners) for all async operations
- [ ] Add error handling with toast notifications
- [ ] Add empty states ("No results found", "No sessions yet")
- [ ] Make responsive (mobile-friendly layouts)
- [ ] Add keyboard shortcuts:
  - `/` - Focus search
  - `Esc` - Close modals/details
  - Arrow keys - Navigate results
- [ ] Add dark/light theme toggle
- [ ] Add export functionality (JSON download)

#### 3.3 Documentation Updates

Files to update:
- `docs/VISUALIZATION.md` - Add semantic features section
- `README.md` - Add web UI screenshots and examples
- `.claude-plugin/HOOKS_GUIDE.md` - Mention web UI integration

---

## File Changes Required

### New Files
1. `tests/test_semantic_web_ui.py` - Integration tests for new endpoints
2. `.github/WEB_UI_IMPLEMENTATION_STATUS.md` - Track progress during implementation

### Files to Modify
1. `src/uacs/visualization/web_server.py` - Add semantic API endpoints
2. `src/uacs/visualization/static/index.html` - Add new UI tabs and components
3. `docs/VISUALIZATION.md` - Document new semantic features
4. `README.md` - Add semantic web UI section with examples

### Files to Reference (DO NOT MODIFY)
- `src/uacs/api.py:91-152` - UACS semantic API implementation
- `src/uacs/conversations/manager.py` - ConversationManager interface
- `src/uacs/knowledge/manager.py` - KnowledgeManager interface
- `src/uacs/embeddings/manager.py` - EmbeddingManager interface
- `.claude-plugin/hooks/*.py` - Hook implementations

---

## Success Criteria

### Functional Requirements ✅

**Search:**
- [ ] Semantic search works with natural language queries
- [ ] Results show similarity scores (0-100%)
- [ ] Can filter by content type (messages, decisions, conventions, artifacts)
- [ ] Results link to full detail view
- [ ] Search responds in < 500ms

**Timeline:**
- [ ] Shows chronological conversation flow
- [ ] Displays user messages, assistant responses, tool uses
- [ ] Can filter by session ID
- [ ] Click event to see full details
- [ ] Timeline loads in < 1s

**Knowledge Browser:**
- [ ] List all decisions with full context (question, decision, rationale, alternatives)
- [ ] List all conventions with sources and confidence
- [ ] List all learnings with confidence scores and categories
- [ ] List all artifacts with descriptions and session links

**Sessions (Trace View):**
- [ ] List all sessions with metadata (duration, tokens, topics, quality)
- [ ] Click session to see full trace
- [ ] Show token usage over time (chart)
- [ ] Display topics and quality metrics
- [ ] Export session as JSON

### Non-Functional Requirements ✅

**Performance:**
- [ ] Search responds in < 500ms
- [ ] Timeline loads in < 1s
- [ ] WebSocket updates every 2s
- [ ] Handles 1000+ entries smoothly
- [ ] Virtual scrolling for long lists (optional enhancement)

**Security:**
- [ ] No XSS vulnerabilities (all user input properly escaped)
- [ ] CORS configured appropriately
- [ ] API rate limiting (optional enhancement)
- [ ] Input validation on all endpoints

**UX:**
- [ ] Loading states for all async operations
- [ ] Error messages for failures (toast/snackbar)
- [ ] Empty states for no data
- [ ] Keyboard shortcuts work
- [ ] Responsive design (mobile-friendly)
- [ ] Consistent styling with existing UI

**Integration:**
- [ ] Works with existing hooks (no changes needed to hooks)
- [ ] Compatible with MCP server (runs on different port)
- [ ] Backward compatible (old APIs still work)
- [ ] No breaking changes to existing visualization

---

## Dependencies

### Python Packages (Already Installed ✅)
- `fastapi>=0.104.0`
- `websockets>=12.0`
- `uvicorn>=0.20.0`
- `starlette>=0.27.0`

### Frontend Libraries (CDN - Already Included ✅)
- D3.js v7
- Chart.js v4

### No New Dependencies Required ✅

---

## Timeline Estimate

### Phase 1: Backend (4-5 hours)
- **Hour 1-2:** Add semantic API endpoints (search, conversations, knowledge)
- **Hour 3:** Add session/trace endpoints
- **Hour 4:** WebSocket integration for real-time updates
- **Hour 5:** Testing and refinement with curl/Postman

### Phase 2: Frontend (4-5 hours)
- **Hour 1-2:** Semantic search UI + results display
- **Hour 2-3:** Timeline view + knowledge browser tabs
- **Hour 3-4:** Session trace view (LangSmith-style)
- **Hour 4-5:** Polish, styling, empty/loading states

### Phase 3: Testing & Documentation (2-3 hours)
- **Hour 1:** Write integration tests (pytest)
- **Hour 2:** Manual testing and bug fixes
- **Hour 3:** Documentation updates (README, VISUALIZATION.md)

**Total Estimate: 10-13 hours** (1.5-2 days of focused work)

---

## Risk Mitigation

### Risk 1: Performance with Large Datasets
**Mitigation:**
- Implement pagination (max 50 items per page)
- Add virtual scrolling for long lists (optional)
- Cache search results (5-minute TTL)
- Use database indexes (FAISS already optimized)

### Risk 2: WebSocket Connection Drops
**Mitigation:**
- Auto-reconnect logic on disconnect
- Show connection status indicator (green/red dot)
- Fall back to polling if WebSocket fails
- Clear error messages

### Risk 3: Browser Compatibility
**Mitigation:**
- Test on Chrome, Firefox, Safari
- Use ES6+ features (supported by all modern browsers)
- Graceful degradation for missing features
- Add browser version check with warning

### Risk 4: XSS Vulnerabilities
**Mitigation:**
- Never use innerHTML with user content
- Always use textContent or createElement
- Add DOMPurify if HTML rendering needed
- Security audit before release

---

## Implementation Prompt

Use this prompt with a new agent or team of agents:

```
# Task: Implement UACS v0.3.0 Semantic Web UI

## Context
You are implementing a web-based UI for UACS v0.3.0 that integrates the new semantic API (conversations, knowledge, embeddings) with the existing web visualizer.

## Reference Documents
- Implementation Plan: .github/WEB_UI_SEMANTIC_INTEGRATION.md (THIS FILE)
- Trace Design: .github/TRACE_VISUALIZATION_DESIGN.md
- Current Web UI: .github/VISUALIZATION_FEATURE_SUMMARY.md
- Hooks Guide: .claude-plugin/HOOKS_GUIDE.md

## Key Files
- Semantic API: src/uacs/api.py (lines 91-152)
- Web Server: src/uacs/visualization/web_server.py (TO MODIFY)
- Frontend: src/uacs/visualization/static/index.html (TO MODIFY)
- Models: src/uacs/conversations/models.py, src/uacs/knowledge/models.py

## Your Task
Follow the implementation plan in .github/WEB_UI_SEMANTIC_INTEGRATION.md:

1. **Phase 1 (Backend):** Add semantic API endpoints to web_server.py
2. **Phase 2 (Frontend):** Add UI components to static/index.html
3. **Phase 3 (Testing):** Write tests and update docs

## Success Criteria
- All 4 new views work (Search, Timeline, Knowledge, Sessions)
- Integration tests pass
- No XSS vulnerabilities
- Documentation updated

## Important Notes
- Use textContent, NOT innerHTML (security)
- Follow existing code style
- Test each endpoint before moving on
- Commit after each working feature
```

---

## Questions to Clarify Before Starting

1. **UI Framework:**
   - Start with Option A (extend HTML) or Option B (React app)?
   - **Recommendation:** Option A for speed

2. **Search Results:**
   - Show full content or summary preview?
   - **Recommendation:** Preview first, expand on click

3. **Real-time Updates:**
   - How often to poll for new data?
   - **Recommendation:** WebSocket every 2s (existing pattern)

4. **Session Grouping:**
   - Auto-group conversations by session_id?
   - **Recommendation:** Yes, use session_id from hooks

5. **Export Format:**
   - JSON, CSV, or both?
   - **Recommendation:** Start with JSON, add CSV later if needed

---

## References

### Code References
- **Semantic API:** src/uacs/api.py:91-152
- **ConversationManager:** src/uacs/conversations/manager.py
- **KnowledgeManager:** src/uacs/knowledge/manager.py
- **EmbeddingManager:** src/uacs/embeddings/manager.py
- **Web Server:** src/uacs/visualization/web_server.py
- **Frontend:** src/uacs/visualization/static/index.html

### Documentation References
- **Hooks Guide:** .claude-plugin/HOOKS_GUIDE.md
- **Trace Design:** .github/TRACE_VISUALIZATION_DESIGN.md
- **Trace Status:** .github/TRACE_VIZ_IMPLEMENTATION_STATUS.md
- **Current UI:** .github/VISUALIZATION_FEATURE_SUMMARY.md
- **Visualization Docs:** docs/VISUALIZATION.md

### Architecture References
- **Session Model:** src/uacs/visualization/models.py
- **Storage Layer:** src/uacs/visualization/storage.py
- **Hook Examples:** .claude-plugin/hooks/*.py

---

## Status Tracking

Create `.github/WEB_UI_IMPLEMENTATION_STATUS.md` during implementation to track progress:

```markdown
# Web UI Implementation Status

## Phase 1: Backend ⏳
- [ ] POST /api/search endpoint
- [ ] GET /api/conversations endpoints
- [ ] GET /api/knowledge/* endpoints
- [ ] GET /api/sessions endpoints
- [ ] WebSocket updates integration
- [ ] Manual testing with curl

## Phase 2: Frontend ⏳
- [ ] Semantic search tab
- [ ] Conversation timeline tab
- [ ] Knowledge browser tab
- [ ] Session trace tab
- [ ] Loading/empty/error states
- [ ] Security review (no innerHTML)

## Phase 3: Testing ⏳
- [ ] Integration tests written
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Manual test pass complete

## Blockers
- None

## Notes
- [Add implementation notes here]
```

---

**Status:** ✅ Ready for Implementation
**Next Step:** Read this document thoroughly, then start Phase 1 (Backend)
