# Context Graph Visualizer - Quick Start

The UACS Context Graph Visualizer provides real-time, browser-based visualization of your context graphs, token usage, and quality metrics.

## 🚀 Launch in 30 Seconds

```bash
# Start the MCP server with web UI
uacs serve --with-ui

# Open your browser to:
# http://localhost:8081
```

That's it! You now have a live dashboard showing:
- Interactive context graph
- Real-time token statistics
- Deduplication metrics
- Content quality analysis
- Topic clustering

## 📊 What You'll See

### 1. Conversation Flow (Default View)
Interactive force-directed graph showing:
- Blue nodes = Context entries
- Orange nodes = Compressed summaries
- Lines = References between entries

**Try it:** Drag nodes around to explore relationships!

### 2. Token Dashboard
Real-time charts showing:
- Token usage (donut chart)
- Entry vs. summary counts (bar chart)
- Compression statistics

### 3. Deduplication Analysis
Visual breakdown of:
- Unique entries vs. duplicates prevented
- Deduplication rate percentage
- Storage efficiency

### 4. Quality Distribution
Content quality metrics:
- High/Medium/Low quality entries
- Average quality score (0-1)
- Quality breakdown by category

### 5. Topic Clusters
Bubble chart showing:
- Topics sized by frequency
- Entry associations
- Topic relationships

## 🎯 Quick Examples

### Example 1: View Context from CLI

```bash
# Terminal 1: Start the visualizer
uacs serve --with-ui

# Terminal 2: Add some context
uacs context add "Implemented auth feature" --agent claude --topics auth security

# Browser: Watch it appear in real-time at http://localhost:8081
```

### Example 2: Python Integration

```python
from pathlib import Path
from uacs import UACS

# Initialize
uacs = UACS(project_path=Path.cwd())

# Add context entries
uacs.add_to_context(
    "claude",
    "Reviewed authentication logic",
    topics=["security", "code-review"]
)

# Start visualizer (from terminal)
# $ uacs serve --with-ui

# View at: http://localhost:8081
```

### Example 3: Run the Demo

```bash
# Run the included demo with sample data
python examples/visualization_demo.py

# This will:
# 1. Create sample context entries
# 2. Start the web server
# 3. Open http://localhost:8081 to view
```

## 🔧 Configuration Options

### Custom Port

```bash
# Use a different port
uacs serve --with-ui --ui-port 3000

# Access at: http://localhost:3000
```

### Custom Host

```bash
# Allow remote connections
uacs serve --host 0.0.0.0 --with-ui --ui-port 8081

# Access from network: http://your-ip:8081
```

### MCP Server Only (No UI)

```bash
# Run just the MCP server
uacs serve

# No web UI, just stdio mode
```

## 📱 Browser Requirements

- **Recommended:** Chrome, Firefox, Safari (latest versions)
- **Required:** JavaScript enabled
- **Features:** WebSocket support for real-time updates

## 🐛 Troubleshooting

### Issue: "Connection Refused"

**Solution:** Make sure the server is running
```bash
uacs serve --with-ui
```

### Issue: WebSocket shows "Disconnected"

**Solutions:**
1. Refresh the browser page
2. Check firewall settings
3. Try a different port: `--ui-port 8082`

### Issue: Empty visualization

**Solution:** Add some context first
```bash
uacs context add "Test entry" --agent test
```

### Issue: Port already in use

**Solution:** Use a different port
```bash
uacs serve --with-ui --ui-port 8082
```

## 🎨 Understanding the Visualizations

### Node Colors in Conversation Flow
- **Blue circles** = Context entries
- **Orange circles** = Compressed summaries
- **Lines** = References/relationships

### Quality Scoring
- **High (0.8-1.0)**: Well-structured content with code blocks, substantial text
- **Medium (0.5-0.8)**: Decent content length and structure
- **Low (0-0.5)**: Short entries, error messages, low-quality content

### Compression Metrics
- **Tokens Saved**: How many tokens were eliminated through compression
- **Compression Ratio**: Percentage of token reduction
- **Storage Size**: Physical storage used (MB)

### Topic Clusters
- **Bubble size**: Number of entries with that topic
- **Position**: Automatically arranged by D3.js force simulation

## 🚀 Next Steps

1. **Read full documentation:** [docs/VISUALIZATION.md](VISUALIZATION.md)
2. **Try the examples:** Check `examples/visualization_demo.py`
3. **Customize:** Modify `src/uacs/visualization/static/index.html`
4. **Integrate:** Use the Python API in your projects

## 💡 Pro Tips

1. **Keep it running**: Leave the visualizer open while working to monitor context growth
2. **Use topics**: Add topics to entries for better clustering visualization
3. **Watch compression**: Monitor the Token Dashboard to see real-time savings
4. **Explore relationships**: Drag nodes in Conversation Flow to untangle complex graphs
5. **Quality first**: Check Quality Distribution to identify low-quality entries

## 📚 Learn More

- [Full Visualization Documentation](VISUALIZATION.md)
- [UACS API Reference](../README.md)
- [MCP Server Setup](MCP_SERVER_BINARY.md)
- [CLI Commands](../README.md#cli-usage)

## 🤝 Contributing

Want to add a new visualization mode? See [VISUALIZATION.md - Customization](VISUALIZATION.md#customization)

---

**Enjoy visualizing your context!** 📊✨
