# UACS Visualization Module

This module provides real-time web-based visualization of UACS context graphs.

## Structure

```
visualization/
├── __init__.py           # Module exports
├── visualization.py      # Terminal-based Rich visualizations
├── web_server.py        # FastAPI web server for browser UI
├── static/              # Static web assets
│   └── index.html       # Single-page web application
└── README.md           # This file
```

## Quick Start

### From CLI

```bash
# Start MCP server with web UI
uacs serve --with-ui

# Custom port
uacs serve --with-ui --ui-port 3000
```

### From Python

```python
from pathlib import Path
from uacs.context.shared_context import SharedContextManager
from uacs.visualization.web_server import VisualizationServer
import uvicorn

# Initialize
manager = SharedContextManager(Path(".state/context"))
viz_server = VisualizationServer(manager, host="localhost", port=8081)

# Run server
config = uvicorn.Config(viz_server.app, host="localhost", port=8081)
server = uvicorn.Server(config)
await server.serve()
```

## Components

### Terminal Visualization (`visualization.py`)

Rich-based terminal visualizations for CLI usage:
- Context graph as tree structure
- Token usage meters
- Agent interaction flow
- Live dashboard with auto-refresh

### Web Visualization (`web_server.py`)

FastAPI server providing:
- REST API endpoints for context data
- WebSocket support for real-time updates
- Static file serving for web UI

### Web UI (`static/index.html`)

Single-page application with:
- D3.js for interactive graphs
- Chart.js for statistics
- 5 visualization modes
- Real-time WebSocket updates

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main visualization page |
| `GET /api/graph` | Context graph data |
| `GET /api/stats` | Token statistics |
| `GET /api/topics` | Topic clusters |
| `GET /api/deduplication` | Deduplication data |
| `GET /api/quality` | Quality distribution |
| `WS /ws` | WebSocket for real-time updates |
| `GET /health` | Health check |

## Visualization Modes

1. **Conversation Flow** - Interactive D3.js force-directed graph
2. **Token Dashboard** - Real-time token usage charts
3. **Deduplication** - Duplicate content analysis
4. **Quality Distribution** - Content quality metrics
5. **Topic Clusters** - Topic network visualization

## Documentation

For complete documentation, see: [docs/VISUALIZATION.md](../../../docs/VISUALIZATION.md)

## Testing

```bash
# Run tests
pytest tests/test_visualization_server.py -v

# Run demo
python examples/visualization_demo.py
```

## Development

### Adding New Endpoints

1. Add method to `VisualizationServer._setup_routes()`
2. Implement data processing method
3. Add frontend update function in `index.html`

### Modifying Visualizations

Edit `static/index.html`:
- CSS for styling (in `<style>` section)
- JavaScript for behavior (in `<script>` section)
- D3.js/Chart.js configuration for visualizations

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- WebSockets - Real-time communication
- D3.js (CDN) - Graph visualization
- Chart.js (CDN) - Statistical charts

## License

MIT License (same as UACS)
