# UACS Trace Visualization - LangSmith-Style Design

**Created:** 2026-02-01
**Status:** Implementation Ready
**Inspired By:** LangSmith, LangFuse, Phoenix, Weights & Biases

---

## Vision

Build a comprehensive trace visualization for UACS that shows:
- **Session traces** - Every Claude Code session with full fidelity
- **Tool usage** - Every tool call with inputs, outputs, latency
- **Token analysis** - Token usage per event, cumulative, compression savings
- **Topic evolution** - How topics emerge and change over time
- **Quality metrics** - Content quality, deduplication rate, compression ratio
- **Search & filter** - Find anything across all sessions

**Goal:** Make UACS context transparent, debuggable, and insightful.

---

## Comparison: What We Have vs What We Need

### Current State

**Terminal Visualization (visualization.py):**
- ✅ Basic stats (entry count, tokens, compression)
- ✅ Context graph tree view
- ❌ No session details
- ❌ No tool-level traces
- ❌ No search/filter
- ❌ Terminal-only (not persistent)

**Web Server (web_server.py):**
- ✅ FastAPI + WebSocket
- ✅ Basic APIs (graph, stats, topics)
- ✅ Real-time updates
- ❌ No frontend (references missing static/index.html)
- ❌ No trace-level views
- ❌ No detailed event inspection

### Target State (LangSmith-Style)

**Features:**
- ✅ **Session List View** - All Claude Code sessions, sortable, searchable
- ✅ **Session Detail View** - Full trace of one session with timeline
- ✅ **Event Inspector** - Click any event to see full details
- ✅ **Token Dashboard** - Real-time token usage across sessions
- ✅ **Topic Explorer** - Topic clusters with session links
- ✅ **Quality Analytics** - Quality distribution, compression metrics
- ✅ **Search & Filter** - By topic, agent, date range, quality
- ✅ **Export** - Export traces to JSON for analysis

---

## Data Model for Traces

### Session Model

```python
{
  "session_id": "claude_code_session_abc123",
  "started_at": "2026-02-01T10:30:00Z",
  "ended_at": "2026-02-01T11:45:00Z",
  "duration_seconds": 4500,
  "turn_count": 42,
  "topics": ["security", "authentication", "testing"],
  "total_tokens": 15234,
  "compressed_tokens": 12987,  # After UACS compression
  "compression_savings": 2247,
  "quality_avg": 0.85,
  "source": "claude-code-posttooluse",  # or "claude-code-sessionend"
  "metadata": {
    "project_dir": "/Users/user/myproject",
    "prevented_compaction": true,
    "early_compression_triggered": 2  # Number of times 50% threshold hit
  },
  "events": [...]  # List of Event objects
}
```

### Event Model

```python
{
  "event_id": "event_001",
  "session_id": "claude_code_session_abc123",
  "type": "tool_use",  # tool_use, user_prompt, assistant_response, compression
  "timestamp": "2026-02-01T10:31:24Z",
  "tool_name": "Bash",  # if type == tool_use
  "tool_input": {
    "command": "pytest tests/"
  },
  "tool_response": "===== 42 passed in 2.3s =====",
  "topics": ["testing"],
  "tokens_in": 45,
  "tokens_out": 120,
  "tokens_cumulative": 165,
  "latency_ms": 2300,
  "quality": 0.9,
  "metadata": {
    "incremental": true,
    "stored_at": "2026-02-01T10:31:26Z"
  }
}
```

### Compression Event Model

```python
{
  "event_id": "compression_001",
  "session_id": "claude_code_session_abc123",
  "type": "compression",
  "timestamp": "2026-02-01T10:45:00Z",
  "trigger": "early_compression",  # early_compression, precompact, sessionend
  "trigger_usage": "52.3%",
  "tokens_before": 10500,
  "tokens_after": 6300,
  "tokens_saved": 4200,
  "compression_ratio": "40.0%",
  "method": "uacs_proactive",
  "turns_archived": 15,
  "metadata": {
    "prevented_compaction": true
  }
}
```

---

## UI Layout (LangSmith-Inspired)

### 1. Sessions List View (Home)

```
┌─────────────────────────────────────────────────────────────────────┐
│  🧠 UACS Session Traces                   [Search...] [Filter ▼]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📊 Overview                                                          │
│  ┌─────────────┬─────────────┬─────────────┬────────────┐           │
│  │ Sessions    │ Total Turns │ Tokens      │ Avg Quality│           │
│  │ 23          │ 487         │ 342,156     │ 0.82       │           │
│  └─────────────┴─────────────┴─────────────┴────────────┘           │
│                                                                       │
│  🕐 Recent Sessions                                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Session abc123                                  2 hours ago  │   │
│  │ Topics: security, authentication  │  42 turns  │  15.2K tokens│   │
│  │ Quality: ████████░░ 82%  │  Compression: 14.7%  │  📄 Details│   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ Session def456                                  5 hours ago  │   │
│  │ Topics: testing, performance      │  28 turns  │  9.8K tokens │   │
│  │ Quality: █████████░ 89%  │  Compression: 18.3%  │  📄 Details│   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ Session ghi789                                  1 day ago    │   │
│  │ Topics: bug-fix, database        │  35 turns  │  12.4K tokens│   │
│  │ Quality: ███████░░░ 75%  │  Compression: 12.1%  │  📄 Details│   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  🎯 Quick Actions                                                     │
│  [Export All] [Compare Sessions] [Topic Explorer] [Token Dashboard] │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. Session Detail View (Trace)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Back to Sessions                                                   │
│  Session abc123 - February 1, 2026 10:30 AM                          │
├─────────────────────────────────────────────────────────────────────┤
│  Topics: security, authentication, testing                            │
│  Duration: 1h 15m  │  Turns: 42  │  Tokens: 15,234 → 12,987 (14.7%)│
│                                                                       │
│  📈 Token Usage Over Time                                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 16K ┤                                              ╭─╮       │    │
│  │ 12K ┤                            ╭────╮         ╭─╯ ╰─╮     │    │
│  │  8K ┤              ╭────────╮   ╯    ╰────╮   ╯      ╰─╮   │    │
│  │  4K ┤  ╭─────────╯          ╰───           ╰──           ╰─ │    │
│  │  0K ┴──┴──────────┴──────────┴──────────┴──────────┴────── │    │
│  │     10:30      10:50      11:10      11:30      11:50       │    │
│  │                                                               │    │
│  │  ⚙️ = Early compression (50%)  │  🔴 = Near compaction (75%)│    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  🔍 Event Timeline                                [Filter: All ▼]    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 10:30:00  USER_PROMPT                              45 tokens │    │
│  │           "Help me implement authentication"                │    │
│  │           Topics: security, authentication                  │    │
│  │           📊 Details                                         │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ 10:30:15  ASSISTANT_RESPONSE                      520 tokens│    │
│  │           "I'll help implement JWT auth..."                 │    │
│  │           Quality: 0.92                                      │    │
│  │           📊 Details                                         │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ 10:31:24  TOOL_USE: Bash                          165 tokens│    │
│  │           Command: pytest tests/                             │    │
│  │           Result: ===== 42 passed in 2.3s =====             │    │
│  │           Latency: 2.3s                                      │    │
│  │           📊 Details                                         │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ 10:45:00  ⚙️ COMPRESSION (Early - 52.3% usage)  -4200 tokens│    │
│  │           Archived 15 turns to UACS                          │    │
│  │           10,500 → 6,300 tokens (40% saved)                 │    │
│  │           ✅ Prevented auto-compaction                      │    │
│  │           📊 Details                                         │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ ... (37 more events)                                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3. Event Inspector (Modal/Drawer)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Event Details - Tool Use                               [✕ Close]    │
├─────────────────────────────────────────────────────────────────────┤
│  Event ID: event_042                                                  │
│  Timestamp: 2026-02-01 10:31:24                                       │
│  Type: tool_use                                                       │
│                                                                       │
│  📝 Tool Information                                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Name: Bash                                                   │    │
│  │ Description: Execute bash command                            │    │
│  │ Latency: 2,300 ms                                            │    │
│  │ Tokens In: 45  │  Tokens Out: 120  │  Total: 165            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  📥 Input                                                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ {                                                            │    │
│  │   "command": "pytest tests/",                                │    │
│  │   "timeout": 120000,                                         │    │
│  │   "description": "Run test suite"                            │    │
│  │ }                                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  📤 Output                                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ ============================= test session starts ==========│    │
│  │ platform darwin -- Python 3.12.0, pytest-8.0.0              │    │
│  │ collected 42 items                                           │    │
│  │                                                              │    │
│  │ tests/test_auth.py ....................................     │    │
│  │ tests/test_db.py .......                                    │    │
│  │                                                              │    │
│  │ ============================= 42 passed in 2.30s ===========│    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  🏷️  Topics: testing                                                 │
│  ⭐ Quality: 0.90                                                     │
│                                                                       │
│  📦 Metadata                                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ incremental: true                                            │    │
│  │ stored_at: 2026-02-01T10:31:26Z                              │    │
│  │ source: claude-code-posttooluse                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  [Copy JSON] [Export Event] [View Related Events]                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 4. Topic Explorer

```
┌─────────────────────────────────────────────────────────────────────┐
│  🏷️  Topic Explorer                                                  │
├─────────────────────────────────────────────────────────────────────┤
│  📊 Topic Clusters                                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                                                              │    │
│  │         ┌─────────┐                                          │    │
│  │         │security │ (45 sessions)                            │    │
│  │         └────┬────┘                                          │    │
│  │              ├── authentication (23)                         │    │
│  │              ├── vulnerability (12)                          │    │
│  │              └── encryption (10)                             │    │
│  │                                                              │    │
│  │     ┌─────────┐                                              │    │
│  │     │testing  │ (38 sessions)                                │    │
│  │     └────┬────┘                                              │    │
│  │          ├── unit-tests (20)                                 │    │
│  │          ├── integration (12)                                │    │
│  │          └── coverage (6)                                    │    │
│  │                                                              │    │
│  │  ┌──────────┐                                                │    │
│  │  │bug-fix   │ (32 sessions)                                  │    │
│  │  └──────────┘                                                │    │
│  │                                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  📋 Sessions by Topic: security                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Session abc123 - JWT authentication (42 turns, 15.2K tokens)│    │
│  │ Session def789 - SQL injection fix (28 turns, 9.8K tokens)  │    │
│  │ Session ghi012 - Password hashing (35 turns, 12.4K tokens)  │    │
│  │ ... (42 more sessions)                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 5. Token Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 Token Analytics Dashboard                                         │
├─────────────────────────────────────────────────────────────────────┤
│  Summary (Last 30 Days)                                               │
│  ┌────────────────┬────────────────┬────────────────┬──────────┐    │
│  │ Total Tokens   │ Compressed     │ Savings        │ Avg/Session│  │
│  │ 342,156        │ 289,843        │ 52,313 (15.3%) │ 14,876     │  │
│  └────────────────┴────────────────┴────────────────┴──────────┘    │
│                                                                       │
│  📈 Token Usage Trend (30 Days)                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 20K ┤             ╭─╮                              ╭─╮       │    │
│  │ 15K ┤      ╭─╮   ╯ ╰╮   ╭─╮   ╭──╮         ╭─╮  ╯ ╰─╮     │    │
│  │ 10K ┤  ╭──╯  ╰─╮╯   ╰──╯  ╰──╯  ╰────╮   ╯  ╰──     ╰─╮   │    │
│  │  5K ┤─╯            Feb 10    Feb 20    Feb 28          ╰─  │    │
│  │  0K ┴──────────────────────────────────────────────────────│    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  💰 Cost Savings (if using Claude API)                                │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Without UACS:    $102.65 (342K tokens @ $0.30/M input)      │    │
│  │ With UACS:       $86.95  (290K tokens @ $0.30/M input)      │    │
│  │ Savings:         $15.70  (15.3% reduction)                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  🔢 Token Distribution by Type                                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ User Prompts:         45,234 tokens (13.2%)                  │    │
│  │ Assistant Responses:  198,765 tokens (58.1%)                 │    │
│  │ Tool Uses:            98,157 tokens (28.7%)                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ⚙️  Compression Events                                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Early Compression (50%):    67 events  │  Avg savings: 4.2K  │    │
│  │ PreCompact (Emergency):      2 events  │  Avg savings: 8.1K  │    │
│  │ SessionEnd:                 23 events  │  Avg savings: 2.3K  │    │
│  │                                                              │    │
│  │ Compaction Prevention Rate: 95.6% (22/23 sessions)          │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints (Backend)

### Session APIs

```python
GET /api/sessions
  # List all sessions with pagination and filtering
  Query params: ?skip=0&limit=20&topic=security&sort=timestamp_desc

GET /api/sessions/{session_id}
  # Get full session details with all events

GET /api/sessions/{session_id}/events
  # Get events for a specific session
  Query params: ?type=tool_use&skip=0&limit=50

GET /api/sessions/{session_id}/tokens
  # Get token usage over time for session

GET /api/sessions/{session_id}/export
  # Export session as JSON
```

### Event APIs

```python
GET /api/events
  # List all events across all sessions
  Query params: ?session_id=xxx&type=tool_use&skip=0&limit=50

GET /api/events/{event_id}
  # Get detailed information about specific event
```

### Analytics APIs

```python
GET /api/analytics/tokens
  # Token usage statistics and trends
  Query params: ?days=30&groupby=day

GET /api/analytics/topics
  # Topic clusters and distribution

GET /api/analytics/quality
  # Quality distribution and averages

GET /api/analytics/compression
  # Compression events and savings
```

### Search API

```python
POST /api/search
  Body: {
    "query": "authentication",
    "filters": {
      "topics": ["security"],
      "date_from": "2026-01-01",
      "date_to": "2026-02-01",
      "quality_min": 0.7
    },
    "limit": 50
  }
  # Search across all sessions and events
```

---

## Implementation Plan

### Phase 1: Backend Enhancements (3-4 hours)

1. **Session Data Model**
   - Create `Session` and `Event` models
   - Add session tracking to hooks
   - Store events in structured format (JSONL or SQLite)

2. **New API Endpoints**
   - Implement all session/event/analytics APIs
   - Add search functionality
   - Add export capabilities

3. **Data Migration**
   - Convert existing UACS context entries to session/event format
   - Preserve backward compatibility

### Phase 2: Frontend Development (6-8 hours)

1. **React/Vue Setup**
   - Choose React (more popular) or Vue (simpler)
   - Setup Vite for fast development
   - TailwindCSS for styling

2. **Core Components**
   - SessionList component
   - SessionDetail component with timeline
   - EventInspector modal
   - TopicExplorer component
   - TokenDashboard component

3. **Data Visualization**
   - Use Chart.js or Recharts for token graphs
   - D3.js for topic clusters (optional)
   - Loading states and error handling

### Phase 3: Polish & Features (2-3 hours)

1. **Search & Filter**
   - Full-text search
   - Multi-select topic filter
   - Date range picker
   - Quality threshold slider

2. **Export & Share**
   - Export session as JSON
   - Copy event details
   - Share session link

3. **Performance**
   - Virtual scrolling for long event lists
   - Lazy loading for event details
   - WebSocket for real-time updates

---

## Technology Stack

### Backend (Python)
- FastAPI (HTTP + WebSocket)
- Pydantic (data validation)
- SQLite or JSONL (storage)
- uvicorn (server)

### Frontend (JavaScript/TypeScript)
- **React** (recommended) or Vue
- **Vite** (build tool)
- **TailwindCSS** (styling)
- **Recharts** or Chart.js (graphs)
- **React Query** or SWR (data fetching)
- **Zustand** or Context API (state management)

---

## File Structure

```
src/uacs/visualization/
├── backend/
│   ├── models.py          # Session, Event data models
│   ├── storage.py         # Session/event storage (SQLite or JSONL)
│   ├── api.py             # FastAPI app with all endpoints
│   └── analytics.py       # Analytics calculation logic
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── SessionList.tsx
│   │   │   ├── SessionDetail.tsx
│   │   │   ├── EventInspector.tsx
│   │   │   ├── TopicExplorer.tsx
│   │   │   ├── TokenDashboard.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── hooks/
│   │   │   ├── useSessions.ts
│   │   │   ├── useEvents.ts
│   │   │   └── useAnalytics.ts
│   │   └── utils/
│   │       ├── api.ts         # API client
│   │       └── formatters.ts   # Date, token formatting
│   └── public/
│       └── index.html
│
└── web_server.py          # Updated with new APIs
```

---

## Next Steps

1. **Implement Backend** - Add session/event models and APIs
2. **Build Frontend** - React app with core components
3. **Test with Real Data** - Use Claude Code plugin to generate traces
4. **Polish UX** - Smooth transitions, loading states, error handling
5. **Document** - Add screenshots and usage guide

---

## Success Metrics

- ✅ View all Claude Code sessions in chronological order
- ✅ Drill down into any session to see full trace
- ✅ Click on any event to inspect full details
- ✅ Search across all sessions by topic/keyword
- ✅ See token usage trends over time
- ✅ Export session data for external analysis
- ✅ Real-time updates via WebSocket
- ✅ Fast loading (<1s for session list, <500ms for session detail)

This makes UACS context completely transparent and debuggable!
