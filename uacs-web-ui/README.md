# UACS Web UI

**Modern Next.js web application for exploring UACS semantic data**

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-Lyra-teal)](https://ui.shadcn.com/)

> **TL;DR:** A production-ready Next.js 15 application for semantic search, conversation tracking, knowledge management, and session tracing in UACS v0.3.0. Built with TypeScript, shadcn/ui, and Tailwind CSS.

---

## Features

### 🔍 Semantic Search
- Natural language search across all UACS content
- 7 content type filters (messages, decisions, conventions, learnings, artifacts, tool uses)
- Relevance-ranked results with similarity scores
- Expandable result cards with full content and metadata

### 📅 Timeline View
- Chronological session event visualization
- User messages, assistant responses, and tool executions
- Session selector dropdown
- Turn numbers, timestamps, and latency metrics

### 📚 Knowledge Browser
- **Decisions** - Architectural decisions with rationale and alternatives
- **Conventions** - Project conventions and patterns with confidence scores
- **Learnings** - Cross-session learnings with categories
- **Artifacts** - Code artifacts (files, functions, classes) with descriptions

### 🔬 Session Traces
- Session list with expandable cards
- Turn count, message count, and token usage
- Full event timelines within each session
- Visual timeline with colored event markers

---

## Prerequisites

- **Node.js** 18+ (for Next.js 15)
- **pnpm** (recommended package manager)
- **UACS Backend** running on port 8081

---

## Quick Start

### 1. Install Dependencies

```bash
cd uacs-web-ui
pnpm install
```

### 2. Start the Backend

In a separate terminal from the project root:

```bash
# Start FastAPI server
uv run python -c "
from pathlib import Path
from uacs import UACS
from uacs.visualization.web_server import VisualizationServer
import uvicorn

uacs = UACS(project_path=Path.cwd())
server = VisualizationServer(uacs=uacs, host='localhost', port=8081)
uvicorn.run(server.app, host='localhost', port=8081)
"
```

The backend will be available at `http://localhost:8081`.

### 3. Start the Frontend

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment Variables

Create a `.env.local` file in the `uacs-web-ui/` directory (optional):

```bash
# Backend API URL (default: http://localhost:8081)
NEXT_PUBLIC_API_URL=http://localhost:8081
```

**Note:** The default API URL is `http://localhost:8081`. Only create `.env.local` if you need to override this.

---

## Development

### Available Scripts

```bash
# Development server with hot reload
pnpm dev

# Production build
pnpm build

# Start production server (after build)
pnpm start

# Run ESLint
pnpm lint

# Format code
pnpm format
```

### Project Structure

```
uacs-web-ui/
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Home page (Search view)
│   ├── knowledge/
│   │   └── page.tsx            # Knowledge browser
│   ├── sessions/
│   │   └── page.tsx            # Session traces
│   └── timeline/
│       └── page.tsx            # Timeline view
├── components/
│   ├── search-view.tsx         # Semantic search UI
│   ├── timeline-view.tsx       # Timeline UI
│   ├── knowledge-view.tsx      # Knowledge browser UI
│   ├── sessions-view.tsx       # Sessions traces UI
│   ├── navigation.tsx          # Tab navigation
│   └── ui/                     # shadcn/ui components
├── lib/
│   ├── api.ts                  # API client (14 endpoints)
│   ├── types.ts                # TypeScript interfaces
│   └── utils.ts                # Utility functions
├── next.config.ts              # Next.js configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies
```

---

## Technology Stack

- **Framework:** Next.js 15.1.6 with App Router
- **Language:** TypeScript 5.x (strict mode)
- **UI Library:** shadcn/ui (Lyra style preset)
- **Styling:** Tailwind CSS 4.x
- **Icons:** Phosphor Icons (v2.1.10)
- **Notifications:** Sonner toasts
- **Font:** Figtree (Google Fonts)
- **Theme:** Zinc base + Teal accent

---

## API Integration

The frontend connects to the UACS FastAPI backend via HTTP REST API.

### API Endpoints Used

**Search:**
- `POST /api/search` - Semantic search with filters

**Conversations:**
- `GET /api/conversations` - List sessions
- `GET /api/conversations/{id}/timeline` - Get session events

**Knowledge:**
- `GET /api/knowledge/decisions` - List decisions
- `GET /api/knowledge/conventions` - List conventions
- `GET /api/knowledge/learnings` - List learnings
- `GET /api/knowledge/artifacts` - List artifacts

**Sessions:**
- `GET /api/sessions` - List sessions with metadata
- `GET /api/sessions/{id}/events` - Get session event timeline

**Analytics:**
- `GET /api/analytics/overview` - System statistics
- `GET /api/analytics/topics` - Topic clusters
- `GET /api/analytics/tokens` - Token usage timeline

See `lib/api.ts` for complete API client implementation.

---

## Type Safety

All API responses are typed with TypeScript interfaces matching the backend Pydantic models. See `lib/types.ts` for type definitions:

- `SearchResult` - Search result with similarity
- `UserMessage` - User conversation message
- `AssistantMessage` - Assistant response
- `ToolUse` - Tool execution record
- `Decision` - Decision with rationale
- `Convention` - Convention with confidence
- `Learning` - Learning pattern
- `Artifact` - File/function/class artifact
- `Session` - Session summary
- `TimelineEvent` - Timeline event (union type)

---

## Build & Deploy

### Production Build

```bash
pnpm build
```

This generates:
- Static HTML for all 4 routes (/, /knowledge, /sessions, /timeline)
- Optimized JavaScript bundles with code splitting
- TypeScript compilation verification

### Production Server

```bash
pnpm build
pnpm start
```

The production server runs on port 3000 by default.

### Docker (Optional)

Create a `Dockerfile` in `uacs-web-ui/`:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t uacs-web-ui .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://host.docker.internal:8081 uacs-web-ui
```

---

## Security

- ✅ **No innerHTML usage** - All user content uses `textContent`
- ✅ **XSS prevention** - Custom `escapeHtml()` function where needed
- ✅ **Type safety** - Full TypeScript coverage
- ✅ **API error handling** - Graceful degradation
- ✅ **Input validation** - Empty query prevention

---

## Troubleshooting

### Backend Connection Errors

**Problem:** "Network error - Could not connect to server"

**Solutions:**
1. Verify backend is running: `curl http://localhost:8081/health`
2. Check backend logs for errors
3. Verify `.env.local` has correct `NEXT_PUBLIC_API_URL`

### Build Errors

**Problem:** TypeScript compilation errors

**Solutions:**
1. Run `pnpm lint` to check for issues
2. Delete `.next/` and rebuild: `rm -rf .next && pnpm build`
3. Clear node_modules: `rm -rf node_modules pnpm-lock.yaml && pnpm install`

### Blank Search Results

**Problem:** Search returns no results despite data in backend

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify embeddings are generated: Check `.state/embeddings/` directory
3. Test backend directly: `curl -X POST http://localhost:8081/api/search -H "Content-Type: application/json" -d '{"query":"test"}'`

---

## Learn More

**Next.js Documentation:**
- [Next.js 15 Features](https://nextjs.org/docs)
- [App Router](https://nextjs.org/docs/app)
- [TypeScript Support](https://nextjs.org/docs/app/building-your-application/configuring/typescript)

**shadcn/ui Documentation:**
- [Component Library](https://ui.shadcn.com/)
- [Theming Guide](https://ui.shadcn.com/docs/theming)

**UACS Documentation:**
- [API Reference](../docs/API_REFERENCE.md)
- [Migration Guide](../docs/MIGRATION.md)
- [Implementation Complete](../.github/NEXT_JS_WEB_UI_COMPLETE.md)

---

## Contributing

1. Follow existing code style (ESLint + Prettier)
2. Write TypeScript with strict mode
3. Test all views manually before committing
4. Run `pnpm lint` and `pnpm build` before submitting

---

## License

MIT License - see [LICENSE](../LICENSE) for details

---

**Version:** 0.3.0 | **Build Status:** ✅ Passing | **Type Safety:** ✅ 100%
