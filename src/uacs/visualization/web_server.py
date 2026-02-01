"""Web server for UACS Context Graph Visualization.

Provides a FastAPI HTTP server with WebSocket support for real-time
visualization of context graphs, token usage, and deduplication.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from uacs.context.shared_context import SharedContextManager

logger = logging.getLogger(__name__)


class VisualizationServer:
    """Web server for context visualization."""

    def __init__(
        self,
        context_manager: SharedContextManager,
        host: str = "localhost",
        port: int = 8081,
    ):
        """Initialize visualization server.

        Args:
            context_manager: SharedContextManager instance
            host: Server host
            port: Server port
        """
        self.context_manager = context_manager
        self.host = host
        self.port = port
        self.app = FastAPI(title="UACS Context Visualizer")

        # Store active WebSocket connections
        self.active_connections: list[WebSocket] = []

        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

        # Setup static files
        static_dir = Path(__file__).parent / "static"
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    def _setup_routes(self):
        """Setup API routes."""

        @self.app.get("/", response_class=HTMLResponse)
        async def index():
            """Serve main visualization page."""
            html_file = Path(__file__).parent / "static" / "index.html"
            if html_file.exists():
                return html_file.read_text()
            return HTMLResponse(content=self._get_default_html(), status_code=200)

        @self.app.get("/api/graph")
        async def get_graph():
            """Get context graph data.

            Returns:
                JSON representation of context graph
            """
            try:
                graph = self.context_manager.get_context_graph()
                return JSONResponse(content=graph)
            except Exception as e:
                logger.error("Error getting graph: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/stats")
        async def get_stats():
            """Get token and compression statistics.

            Returns:
                JSON representation of stats
            """
            try:
                stats = self.context_manager.get_stats()
                return JSONResponse(content=stats)
            except Exception as e:
                logger.error("Error getting stats: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/topics")
        async def get_topics():
            """Get topic clusters from context entries.

            Returns:
                JSON representation of topic clusters
            """
            try:
                topics = self._get_topic_clusters()
                return JSONResponse(content=topics)
            except Exception as e:
                logger.error("Error getting topics: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/deduplication")
        async def get_deduplication():
            """Get deduplication information.

            Returns:
                JSON representation of duplicate content areas
            """
            try:
                dedup_data = self._get_deduplication_data()
                return JSONResponse(content=dedup_data)
            except Exception as e:
                logger.error("Error getting deduplication data: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/quality")
        async def get_quality():
            """Get quality distribution of context entries.

            Returns:
                JSON representation of quality scores
            """
            try:
                quality_data = self._get_quality_distribution()
                return JSONResponse(content=quality_data)
            except Exception as e:
                logger.error("Error getting quality data: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await self._handle_websocket(websocket)

        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return JSONResponse(content={"status": "ok"})

    async def _handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection for real-time updates.

        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)

        try:
            while True:
                # Send updates every 2 seconds
                await asyncio.sleep(2)

                data = {
                    "type": "update",
                    "graph": self.context_manager.get_context_graph(),
                    "stats": self.context_manager.get_stats(),
                    "topics": self._get_topic_clusters(),
                    "quality": self._get_quality_distribution(),
                }

                await websocket.send_json(data)
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            logger.error("WebSocket error: %s", e)
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    def _get_topic_clusters(self) -> dict[str, Any]:
        """Get topic clusters from context entries.

        Returns:
            Dictionary with topic cluster information
        """
        # Count topics across entries
        topic_counts: dict[str, int] = {}
        topic_entries: dict[str, list[str]] = {}

        for entry in self.context_manager.entries.values():
            for topic in entry.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
                if topic not in topic_entries:
                    topic_entries[topic] = []
                topic_entries[topic].append(entry.id)

        # Create clusters
        clusters = []
        for topic, count in topic_counts.items():
            clusters.append({
                "topic": topic,
                "count": count,
                "entries": topic_entries[topic],
            })

        # Sort by count
        clusters.sort(key=lambda x: x["count"], reverse=True)

        return {
            "clusters": clusters,
            "total_topics": len(clusters),
        }

    def _get_deduplication_data(self) -> dict[str, Any]:
        """Get deduplication information.

        Returns:
            Dictionary with deduplication statistics
        """
        # Get all unique hashes
        unique_hashes = set(entry.hash for entry in self.context_manager.entries.values())

        # Count duplicates prevented by dedup index
        total_possible = len(self.context_manager.entries) + len(self.context_manager.dedup_index) - len(unique_hashes)
        duplicates_prevented = len(self.context_manager.dedup_index) - len(unique_hashes)

        return {
            "unique_entries": len(unique_hashes),
            "total_entries": len(self.context_manager.entries),
            "duplicates_prevented": duplicates_prevented,
            "deduplication_rate": f"{(duplicates_prevented / total_possible * 100):.1f}%" if total_possible > 0 else "0%",
        }

    def _get_quality_distribution(self) -> dict[str, Any]:
        """Get quality distribution of entries.

        Returns:
            Dictionary with quality distribution data
        """
        qualities = [entry.quality for entry in self.context_manager.entries.values()]

        if not qualities:
            return {
                "distribution": [],
                "average": 0,
                "high_quality": 0,
                "medium_quality": 0,
                "low_quality": 0,
            }

        # Create distribution buckets
        high_quality = sum(1 for q in qualities if q >= 0.8)
        medium_quality = sum(1 for q in qualities if 0.5 <= q < 0.8)
        low_quality = sum(1 for q in qualities if q < 0.5)

        distribution = [
            {"range": "High (0.8-1.0)", "count": high_quality},
            {"range": "Medium (0.5-0.8)", "count": medium_quality},
            {"range": "Low (0-0.5)", "count": low_quality},
        ]

        return {
            "distribution": distribution,
            "average": sum(qualities) / len(qualities),
            "high_quality": high_quality,
            "medium_quality": medium_quality,
            "low_quality": low_quality,
        }

    def _get_default_html(self) -> str:
        """Get default HTML if static file doesn't exist.

        Returns:
            HTML string
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <title>UACS Context Visualizer</title>
</head>
<body>
    <h1>UACS Context Visualizer</h1>
    <p>Static files not found. Please check the installation.</p>
</body>
</html>
"""

    async def broadcast_update(self, data: dict[str, Any]):
        """Broadcast update to all connected WebSocket clients.

        Args:
            data: Data to broadcast
        """
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error("Error broadcasting to connection: %s", e)
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)


async def start_visualization_server(
    context_manager: SharedContextManager,
    host: str = "localhost",
    port: int = 8081,
) -> VisualizationServer:
    """Start the visualization server.

    Args:
        context_manager: SharedContextManager instance
        host: Server host
        port: Server port

    Returns:
        VisualizationServer instance
    """
    import uvicorn

    server = VisualizationServer(context_manager, host, port)

    # Create server config
    config = uvicorn.Config(
        server.app,
        host=host,
        port=port,
        log_level="info",
    )

    # Start server in background
    uvicorn_server = uvicorn.Server(config)

    logger.info("Starting visualization server on %s:%s", host, port)

    # Run server
    await uvicorn_server.serve()

    return server
