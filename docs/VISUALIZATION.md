# UACS Context Graph Visualizer

The UACS Context Graph Visualizer is a web-based visualization tool that runs alongside the MCP server to provide real-time insights into context graphs, token usage, deduplication, and content quality.

## Overview

The visualizer provides five distinct views for monitoring and analyzing UACS context:

1. **Conversation Flow** - Interactive D3.js graph showing context structure
2. **Token Dashboard** - Real-time token usage and compression statistics
3. **Deduplication Heatmap** - Visual analysis of duplicate content
4. **Quality Distribution** - Charts showing content quality scores
5. **Topic Clusters** - Network graph of related topics

## Quick Start

### Starting the Web UI

Start the MCP server with web UI visualization:

```bash
# Start MCP server with web UI on default port (8081)
uacs serve --with-ui

# Specify custom UI port
uacs serve --with-ui --ui-port 3000

# Custom host and ports
uacs serve --host 0.0.0.0 --port 8080 --with-ui --ui-port 8081
```

The web UI will be accessible at `http://localhost:8081` (or your specified port).

### MCP Server Only (No UI)

To run just the MCP server without the web UI:

```bash
uacs serve
```

## Architecture

### Backend Components

#### FastAPI Server (`src/uacs/visualization/web_server.py`)

The visualization server is built with FastAPI and provides:

- **REST API endpoints** for context data
- **WebSocket support** for real-time updates
- **Static file serving** for the web interface
- **Integration with SharedContextManager** for live data

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve main visualization page |
| `/api/graph` | GET | Get context graph data (nodes and edges) |
| `/api/stats` | GET | Get token and compression statistics |
| `/api/topics` | GET | Get topic clusters from entries |
| `/api/deduplication` | GET | Get deduplication statistics |
| `/api/quality` | GET | Get quality distribution of entries |
| `/ws` | WebSocket | Real-time updates every 2 seconds |
| `/health` | GET | Health check endpoint |

### Frontend Components

#### Single-Page Application (`src/uacs/visualization/static/index.html`)

The frontend is a single HTML file with embedded JavaScript and CSS, featuring:

- **D3.js** for interactive graph visualizations
- **Chart.js** for statistical charts
- **WebSocket client** for real-time updates
- **Responsive design** with dark theme
- **Navigation** between five visualization modes

## Visualization Modes

### 1. Conversation Flow

Interactive force-directed graph showing:
- **Entry nodes** (blue circles) - Individual context entries
- **Summary nodes** (orange circles) - Compressed summaries
- **Reference edges** - Relationships between entries
- **Summary edges** - Entries included in summaries

**Interactions:**
- Drag nodes to reposition
- Hover for details
- Click to focus

### 2. Token Dashboard

Real-time statistics display:
- **Token usage donut chart** - Used vs. saved tokens
- **Compression bar chart** - Entries vs. summaries
- **Live statistics** - Entry count, compression ratio, storage size

### 3. Deduplication

Duplicate content analysis:
- **Deduplication metrics** - Unique entries, duplicates prevented
- **Deduplication rate** - Percentage of unique content
- **Visual progress bar** - Shows deduplication effectiveness

### 4. Quality Distribution

Content quality analysis:
- **Quality distribution chart** - High/medium/low quality entries
- **Average quality metric** - Overall quality score (0-1)
- **Quality breakdown** - Count of entries by quality level

Quality factors:
- Content length (penalizes very short entries)
- Presence of code blocks (rewards)
- Error messages (penalizes)
- Substantial content (rewards >100 tokens)

### 5. Topic Clusters

Topic-based visualization:
- **Bubble chart** - Topics sized by frequency
- **Topic list** - Sorted by popularity
- **Entry associations** - Shows which entries use each topic

## Integration with UACS

### Using the Visualizer with SharedContextManager

```python
from pathlib import Path
from uacs.context.shared_context import SharedContextManager
from uacs.visualization.web_server import VisualizationServer
import uvicorn

# Initialize context manager
context_manager = SharedContextManager(storage_path=Path(".state/context"))

# Add some context
context_manager.add_entry(
    "Implemented authentication feature",
    agent="claude",
    topics=["auth", "security"]
)

# Create and run visualization server
viz_server = VisualizationServer(context_manager, host="localhost", port=8081)

config = uvicorn.Config(viz_server.app, host="localhost", port=8081)
server = uvicorn.Server(config)
await server.serve()
```

### Programmatic Access to Visualization Data

```python
from uacs.context.shared_context import SharedContextManager

manager = SharedContextManager()

# Get graph structure
graph = manager.get_context_graph()
# Returns: {"nodes": [...], "edges": [...], "stats": {...}}

# Get statistics
stats = manager.get_stats()
# Returns: {"entry_count": N, "total_tokens": N, ...}

# Get topic clusters
topics = viz_server._get_topic_clusters()
# Returns: {"clusters": [...], "total_topics": N}

# Get quality distribution
quality = viz_server._get_quality_distribution()
# Returns: {"distribution": [...], "average": 0.85, ...}
```

## Real-Time Updates

The visualizer uses WebSocket connections for live updates:

1. **Client connects** to `/ws` endpoint
2. **Server broadcasts** updates every 2 seconds
3. **Client receives** latest graph, stats, topics, and quality data
4. **UI updates** automatically without page refresh

### Update Frequency

Default: 2 seconds between updates. This can be modified in `web_server.py`:

```python
async def _handle_websocket(self, websocket: WebSocket):
    while True:
        await asyncio.sleep(2)  # Change this value
        # Send updates...
```

## Customization

### Changing the Theme

Edit the CSS in `index.html`:

```css
body {
    background: #0f0f23;  /* Dark background */
    color: #cccccc;        /* Light text */
}

.card {
    background: #1a1a2e;   /* Card background */
    border: 1px solid #16213e;  /* Border color */
}
```

### Adding New Visualizations

1. **Add backend endpoint** in `web_server.py`:

```python
@self.app.get("/api/custom")
async def get_custom_data():
    data = self._get_custom_data()
    return JSONResponse(content=data)
```

2. **Add frontend view** in `index.html`:

```html
<div class="view" id="custom-view">
    <div class="card">
        <h3>Custom Visualization</h3>
        <div id="customContainer"></div>
    </div>
</div>
```

3. **Add navigation button**:

```html
<button class="nav-button" data-view="custom">Custom View</button>
```

4. **Implement update logic**:

```javascript
function updateCustomView(data) {
    const container = document.getElementById('customContainer');
    // Your visualization code here
}
```

### Modifying Graph Appearance

Edit D3.js configuration in `updateConversationFlow()`:

```javascript
const simulation = d3.forceSimulation(graph.nodes)
    .force('link', d3.forceLink(graph.edges).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))  // Repulsion
    .force('center', d3.forceCenter(width / 2, height / 2));
```

## Performance Considerations

### Scaling with Large Context Graphs

For large numbers of entries (>100):

1. **Pagination**: Implement pagination in graph view
2. **Filtering**: Add filters for date ranges or agents
3. **Lazy loading**: Load detailed data on demand
4. **Update throttling**: Reduce WebSocket update frequency

### Memory Usage

The visualizer maintains active WebSocket connections. Monitor with:

```python
# In VisualizationServer
print(f"Active connections: {len(self.active_connections)}")
```

## Troubleshooting

### Web UI Not Loading

**Problem**: Browser shows "Connection refused"

**Solutions**:
- Check server is running: `uacs serve --with-ui`
- Verify port is not in use: `lsof -i :8081`
- Check firewall settings
- Try different port: `uacs serve --with-ui --ui-port 8082`

### WebSocket Connection Failed

**Problem**: Status shows "Disconnected"

**Solutions**:
- Check browser console for errors (F12)
- Verify WebSocket protocol (ws:// for http, wss:// for https)
- Check for proxy/firewall blocking WebSockets
- Try refreshing the page

### Graph Not Rendering

**Problem**: Empty view or "No context entries yet"

**Solutions**:
- Add some context entries: `uacs.add_to_context("test", "content")`
- Check API endpoint: `curl http://localhost:8081/api/graph`
- Verify SharedContextManager is initialized
- Check browser console for JavaScript errors

### Slow Performance

**Problem**: UI is laggy with many entries

**Solutions**:
- Reduce update frequency (modify WebSocket interval)
- Limit graph nodes displayed (filter oldest entries)
- Disable animations for large graphs
- Use pagination

## Testing

### Running Tests

```bash
# Run visualization server tests
pytest tests/test_visualization_server.py -v

# Run all tests including visualization
pytest tests/ -v

# Run with coverage
pytest tests/test_visualization_server.py --cov=src/uacs/visualization
```

### Manual Testing

1. **Start server**:
   ```bash
   uacs serve --with-ui
   ```

2. **Open browser**: Navigate to `http://localhost:8081`

3. **Add test data**:
   ```python
   from uacs import UACS
   from pathlib import Path

   uacs = UACS(project_path=Path.cwd())
   uacs.add_to_context("test", "Test content", topics=["testing"])
   ```

4. **Verify**:
   - Check Conversation Flow shows nodes
   - Verify Token Dashboard displays statistics
   - Confirm WebSocket status is "Connected"
   - Switch between all 5 views

### Integration Testing

Test with MCP server:

```bash
# Terminal 1: Start MCP server with UI
uacs serve --with-ui

# Terminal 2: Use MCP client to add context
# (Your MCP client code here)

# Browser: Watch real-time updates at http://localhost:8081
```

## API Reference

### VisualizationServer Class

```python
class VisualizationServer:
    """Web server for context visualization."""

    def __init__(
        self,
        context_manager: SharedContextManager,
        host: str = "localhost",
        port: int = 8081,
    ):
        """Initialize visualization server."""

    async def broadcast_update(self, data: dict[str, Any]):
        """Broadcast update to all connected WebSocket clients."""
```

### Helper Function

```python
async def start_visualization_server(
    context_manager: SharedContextManager,
    host: str = "localhost",
    port: int = 8081,
) -> VisualizationServer:
    """Start the visualization server."""
```

## Examples

### Example 1: Basic Usage

```python
from pathlib import Path
from uacs import UACS

# Initialize UACS
uacs = UACS(project_path=Path.cwd())

# Add context with topics
uacs.add_to_context(
    "claude",
    "Reviewed authentication logic in auth.py",
    topics=["code-review", "security"]
)

uacs.add_to_context(
    "copilot",
    "Generated test cases for login flow",
    topics=["testing", "auth"]
)

# Start visualization (from CLI)
# $ uacs serve --with-ui

# View at: http://localhost:8081
```

### Example 2: Custom Integration

```python
import asyncio
from pathlib import Path
from uacs.context.shared_context import SharedContextManager
from uacs.visualization.web_server import start_visualization_server

async def main():
    # Setup context manager
    manager = SharedContextManager(storage_path=Path(".state/context"))

    # Add sample data
    for i in range(10):
        manager.add_entry(
            f"Context entry {i}",
            agent="test-agent",
            topics=["demo", "testing"]
        )

    # Start visualization server
    print("Starting visualization server...")
    server = await start_visualization_server(manager, host="0.0.0.0", port=8081)
    print("Server running at http://localhost:8081")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Programmatic Data Access

```python
from pathlib import Path
from uacs.context.shared_context import SharedContextManager
from uacs.visualization.web_server import VisualizationServer

# Initialize
manager = SharedContextManager(storage_path=Path(".state/context"))
viz_server = VisualizationServer(manager)

# Get visualization data programmatically
graph_data = manager.get_context_graph()
print(f"Nodes: {len(graph_data['nodes'])}")
print(f"Edges: {len(graph_data['edges'])}")

stats = manager.get_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Compression: {stats['compression_ratio']}")

topics = viz_server._get_topic_clusters()
print(f"Topics: {topics['total_topics']}")

quality = viz_server._get_quality_distribution()
print(f"Average quality: {quality['average']:.2f}")
```

## Security Considerations

### Production Deployment

**Important**: The visualizer is designed for development and debugging. For production:

1. **Add authentication**: Implement JWT or session-based auth
2. **Use HTTPS**: Configure SSL certificates for secure WebSocket (wss://)
3. **Restrict access**: Use firewall rules or network policies
4. **Rate limiting**: Add rate limiting to API endpoints
5. **Input validation**: Sanitize all user inputs

### CORS Configuration

Default configuration allows all origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict to specific origins:

```python
allow_origins=["https://yourdomain.com"]
```

## Future Enhancements

Planned features:

- [ ] Historical timeline view of context evolution
- [ ] Export visualizations as PNG/SVG
- [ ] Filter context by date range
- [ ] Search within context entries
- [ ] Collaborative annotation features
- [ ] Performance metrics dashboard
- [ ] A/B testing visualization for quality improvements
- [ ] Integration with monitoring tools (Prometheus, Grafana)

## Contributing

To contribute to the visualizer:

1. Fork the repository
2. Create a feature branch
3. Make your changes in `src/uacs/visualization/`
4. Add tests in `tests/test_visualization_server.py`
5. Update this documentation
6. Submit a pull request

## License

Same as UACS: MIT License

## Support

For issues or questions:
- GitHub Issues: https://github.com/kylebrodeur/universal-agent-context/issues
- Documentation: https://github.com/kylebrodeur/universal-agent-context/tree/main/docs
