"""Web server for UACS Context Graph Visualization.

Provides a FastAPI HTTP server with WebSocket support for real-time
visualization of context graphs, token usage, and deduplication.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, TYPE_CHECKING

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

if TYPE_CHECKING:
    from uacs.api import UACS

from uacs.embeddings.manager import SearchResult

logger = logging.getLogger(__name__)


class VisualizationServer:
    """Web server for context visualization."""

    def __init__(
        self,
        uacs: "UACS",
        host: str = "localhost",
        port: int = 8081,
    ):
        """Initialize visualization server.

        Args:
            uacs: UACS instance
            host: Server host
            port: Server port
        """
        self.uacs = uacs
        self.context_manager = uacs.shared_context  # Backward compatibility
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
            self.app.mount(
                "/static",
                StaticFiles(directory=str(static_dir)),
                name="static"
            )

    def _setup_routes(self):
        """Setup API routes."""

        @self.app.get("/", response_class=HTMLResponse)
        async def index():
            """Serve main visualization page."""
            html_file = Path(__file__).parent / "static" / "index.html"
            if html_file.exists():
                return html_file.read_text()
            return HTMLResponse(
                content=self._get_default_html(),
                status_code=200
            )

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

        # ====== Semantic API Endpoints (v0.3.0+) ======

        @self.app.post("/api/search")
        async def search(request: Request):
            """Semantic search endpoint.
            
            Request body:
                {
                    "query": str,
                    "types": Optional[List[str]],
                    "limit": int (default 10),
                    "min_confidence": float (default 0.7),
                    "session_id": Optional[str]
                }
            """
            try:
                body = await request.json()
                query = body.get("query", "")
                types = body.get("types", None)
                limit = body.get("limit", 10)
                min_confidence = body.get("min_confidence", 0.7)
                session_id = body.get("session_id", None)
                
                if not query:
                    return JSONResponse(
                        content={"error": "query is required"},
                        status_code=400
                    )
                
                results = self.uacs.search(
                    query=query,
                    types=types,
                    min_confidence=min_confidence,
                    session_id=session_id,
                    limit=limit
                )
                
                return JSONResponse(content={
                    "results": [
                        self._serialize_search_result(r) for r in results
                    ],
                    "count": len(results)
                })
            except Exception as e:
                logger.error("Search error: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/conversations")
        async def list_conversations(
            skip: int = 0,
            limit: int = 50,
            session_id: str = None
        ):
            """List conversations with pagination.
            
            Query params:
                skip: Number of items to skip (default 0)
                limit: Max items to return (default 50)
                session_id: Optional filter by session
            """
            try:
                # Get all unique sessions
                all_messages = (
                    self.uacs.conversation_manager._user_messages +
                    self.uacs.conversation_manager._assistant_messages
                )
                
                # Group by session
                sessions = {}
                for msg in all_messages:
                    sid = msg.session_id
                    if session_id and sid != session_id:
                        continue
                    if sid not in sessions:
                        sessions[sid] = {
                            "session_id": sid,
                            "messages": [],
                            "first_message": None,
                            "last_message": None,
                            "turn_count": 0
                        }
                    
                    sessions[sid]["messages"].append(msg)

                    # Update timestamps
                    first_msg = sessions[sid]["first_message"]
                    if first_msg is None or msg.timestamp < first_msg:
                        sessions[sid]["first_message"] = msg.timestamp
                    last_msg = sessions[sid]["last_message"]
                    if last_msg is None or msg.timestamp > last_msg:
                        sessions[sid]["last_message"] = msg.timestamp

                    # Update turn count
                    if hasattr(msg, 'turn'):
                        sessions[sid]["turn_count"] = max(
                            sessions[sid]["turn_count"],
                            msg.turn
                        )
                
                # Convert to list and sort by last message
                conversations = list(sessions.values())
                conversations.sort(
                    key=lambda x: (
                        x["last_message"]
                        if x["last_message"]
                        else datetime.min
                    ),
                    reverse=True
                )
                
                # Apply pagination
                paginated = conversations[skip:skip + limit]
                
                # Serialize response
                result = []
                for conv in paginated:
                    first_msg = conv["first_message"]
                    last_msg = conv["last_message"]
                    result.append({
                        "session_id": conv["session_id"],
                        "message_count": len(conv["messages"]),
                        "turn_count": conv["turn_count"],
                        "first_message": (
                            first_msg.isoformat() if first_msg else None
                        ),
                        "last_message": (
                            last_msg.isoformat() if last_msg else None
                        )
                    })
                
                return JSONResponse(content={
                    "conversations": result,
                    "total": len(conversations),
                    "skip": skip,
                    "limit": limit
                })
            except Exception as e:
                logger.error("Error listing conversations: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/conversations/{session_id}")
        async def get_conversation(session_id: str):
            """Get full conversation for a session."""
            try:
                conv_mgr = self.uacs.conversation_manager
                messages = conv_mgr.get_session_messages(session_id)

                return JSONResponse(content={
                    "session_id": session_id,
                    "user_messages": [
                        self._serialize_user_message(msg)
                        for msg in messages["user_messages"]
                    ],
                    "assistant_messages": [
                        self._serialize_assistant_message(msg)
                        for msg in messages["assistant_messages"]
                    ],
                    "tool_uses": [
                        self._serialize_tool_use(tool)
                        for tool in messages["tool_uses"]
                    ]
                })
            except Exception as e:
                logger.error("Error getting conversation: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/conversations/{session_id}/timeline")
        async def get_conversation_timeline(session_id: str):
            """Get conversation as a timeline of events."""
            try:
                conv_mgr = self.uacs.conversation_manager
                messages = conv_mgr.get_session_messages(session_id)

                # Merge all events into timeline
                timeline = []
                
                for msg in messages["user_messages"]:
                    timeline.append({
                        "type": "user_message",
                        "turn": msg.turn,
                        "timestamp": msg.timestamp.isoformat(),
                        "content": msg.content,
                        "topics": msg.topics
                    })
                
                for msg in messages["assistant_messages"]:
                    timeline.append({
                        "type": "assistant_message",
                        "turn": msg.turn,
                        "timestamp": msg.timestamp.isoformat(),
                        "content": msg.content,
                        "tokens_in": msg.tokens_in,
                        "tokens_out": msg.tokens_out,
                        "model": msg.model
                    })
                
                for tool in messages["tool_uses"]:
                    timeline.append({
                        "type": "tool_use",
                        "turn": tool.turn,
                        "timestamp": tool.timestamp.isoformat(),
                        "tool_name": tool.tool_name,
                        "tool_input": tool.tool_input,
                        "tool_response": tool.tool_response,
                        "latency_ms": tool.latency_ms,
                        "success": tool.success
                    })
                
                # Sort by turn, then timestamp
                timeline.sort(key=lambda x: (x["turn"], x["timestamp"]))
                
                return JSONResponse(content={
                    "session_id": session_id,
                    "timeline": timeline,
                    "event_count": len(timeline)
                })
            except Exception as e:
                logger.error("Error getting timeline: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/knowledge/decisions")
        async def list_decisions(
            skip: int = 0,
            limit: int = 50,
            session_id: str = None,
            topics: str = None
        ):
            """List decisions with optional filters."""
            try:
                knowledge_mgr = self.uacs.knowledge_manager
                decisions = list(knowledge_mgr.decisions.values())

                # Filter by session_id
                if session_id:
                    decisions = [
                        d for d in decisions
                        if d.session_id == session_id
                    ]

                # Filter by topics
                if topics:
                    topic_list = [t.strip() for t in topics.split(",")]
                    decisions = [
                        d for d in decisions
                        if any(t in d.topics for t in topic_list)
                    ]
                
                # Sort by decided_at (newest first)
                decisions.sort(key=lambda x: x.decided_at, reverse=True)
                
                # Paginate
                paginated = decisions[skip:skip + limit]

                return JSONResponse(content={
                    "decisions": [
                        self._serialize_decision(d) for d in paginated
                    ],
                    "total": len(decisions),
                    "skip": skip,
                    "limit": limit
                })
            except Exception as e:
                logger.error("Error listing decisions: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/knowledge/conventions")
        async def list_conventions(
            skip: int = 0,
            limit: int = 50,
            topics: str = None,
            min_confidence: float = 0.0
        ):
            """List conventions with optional filters."""
            try:
                knowledge_mgr = self.uacs.knowledge_manager
                conventions = list(knowledge_mgr.conventions.values())

                # Filter by confidence
                conventions = [
                    c for c in conventions
                    if c.confidence >= min_confidence
                ]

                # Filter by topics
                if topics:
                    topic_list = [t.strip() for t in topics.split(",")]
                    conventions = [
                        c for c in conventions
                        if any(t in c.topics for t in topic_list)
                    ]

                # Sort by confidence (highest first)
                conventions.sort(key=lambda x: x.confidence, reverse=True)

                # Paginate
                paginated = conventions[skip:skip + limit]

                return JSONResponse(content={
                    "conventions": [
                        self._serialize_convention(c) for c in paginated
                    ],
                    "total": len(conventions),
                    "skip": skip,
                    "limit": limit
                })
            except Exception as e:
                logger.error("Error listing conventions: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/knowledge/learnings")
        async def list_learnings(
            skip: int = 0,
            limit: int = 50,
            category: str = None,
            min_confidence: float = 0.0
        ):
            """List learnings with optional filters."""
            try:
                knowledge_mgr = self.uacs.knowledge_manager
                learnings = list(knowledge_mgr.learnings.values())

                # Filter by confidence
                learnings = [
                    learn for learn in learnings
                    if learn.confidence >= min_confidence
                ]

                # Filter by category
                if category:
                    learnings = [
                        learn for learn in learnings
                        if learn.category == category
                    ]

                # Sort by confidence (highest first)
                learnings.sort(key=lambda x: x.confidence, reverse=True)

                # Paginate
                paginated = learnings[skip:skip + limit]

                return JSONResponse(content={
                    "learnings": [
                        self._serialize_learning(learn)
                        for learn in paginated
                    ],
                    "total": len(learnings),
                    "skip": skip,
                    "limit": limit
                })
            except Exception as e:
                logger.error("Error listing learnings: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/knowledge/artifacts")
        async def list_artifacts(
            skip: int = 0,
            limit: int = 50,
            session_id: str = None,
            topics: str = None,
            artifact_type: str = None
        ):
            """List artifacts with optional filters."""
            try:
                knowledge_mgr = self.uacs.knowledge_manager
                artifacts = list(knowledge_mgr.artifacts.values())

                # Filter by session_id
                if session_id:
                    artifacts = [
                        a for a in artifacts
                        if a.created_in_session == session_id
                    ]

                # Filter by artifact type
                if artifact_type:
                    artifacts = [
                        a for a in artifacts if a.type == artifact_type
                    ]

                # Filter by topics
                if topics:
                    topic_list = [t.strip() for t in topics.split(",")]
                    artifacts = [
                        a for a in artifacts
                        if any(t in a.topics for t in topic_list)
                    ]

                # Paginate
                paginated = artifacts[skip:skip + limit]

                return JSONResponse(content={
                    "artifacts": [
                        self._serialize_artifact(a) for a in paginated
                    ],
                    "total": len(artifacts),
                    "skip": skip,
                    "limit": limit
                })
            except Exception as e:
                logger.error("Error listing artifacts: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/sessions")
        async def list_sessions(
            skip: int = 0,
            limit: int = 50
        ):
            """List sessions with metadata."""
            try:
                # Get all messages
                all_messages = (
                    self.uacs.conversation_manager._user_messages +
                    self.uacs.conversation_manager._assistant_messages
                )
                
                # Group by session
                sessions = {}
                for msg in all_messages:
                    sid = msg.session_id
                    if sid not in sessions:
                        sessions[sid] = {
                            "session_id": sid,
                            "message_count": 0,
                            "first_timestamp": msg.timestamp,
                            "last_timestamp": msg.timestamp,
                            "turn_count": 0,
                            "total_tokens_in": 0,
                            "total_tokens_out": 0
                        }
                    
                    sessions[sid]["message_count"] += 1
                    
                    # Update timestamps
                    if msg.timestamp < sessions[sid]["first_timestamp"]:
                        sessions[sid]["first_timestamp"] = msg.timestamp
                    if msg.timestamp > sessions[sid]["last_timestamp"]:
                        sessions[sid]["last_timestamp"] = msg.timestamp
                    
                    # Update turn count
                    if hasattr(msg, 'turn'):
                        sessions[sid]["turn_count"] = max(
                            sessions[sid]["turn_count"],
                            msg.turn
                        )
                    
                    # Update token counts (from assistant messages)
                    if hasattr(msg, 'tokens_in') and msg.tokens_in:
                        sessions[sid]["total_tokens_in"] += msg.tokens_in
                    if hasattr(msg, 'tokens_out') and msg.tokens_out:
                        sessions[sid]["total_tokens_out"] += (
                            msg.tokens_out
                        )
                
                # Convert to list and sort by last timestamp
                session_list = list(sessions.values())
                session_list.sort(
                    key=lambda x: x["last_timestamp"],
                    reverse=True
                )

                # Paginate
                paginated = session_list[skip:skip + limit]

                # Serialize
                result = []
                for sess in paginated:
                    result.append({
                        "session_id": sess["session_id"],
                        "message_count": sess["message_count"],
                        "turn_count": sess["turn_count"],
                        "first_timestamp": (
                            sess["first_timestamp"].isoformat()
                        ),
                        "last_timestamp": (
                            sess["last_timestamp"].isoformat()
                        ),
                        "total_tokens_in": sess["total_tokens_in"],
                        "total_tokens_out": sess["total_tokens_out"]
                    })
                
                return JSONResponse(content={
                    "sessions": result,
                    "total": len(session_list),
                    "skip": skip,
                    "limit": limit
                })
            except Exception as e:
                logger.error("Error listing sessions: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/sessions/{session_id}")
        async def get_session(session_id: str):
            """Get session details with statistics."""
            try:
                conv_mgr = self.uacs.conversation_manager
                messages = conv_mgr.get_session_messages(session_id)

                # Calculate statistics
                total_tokens_in = sum(
                    msg.tokens_in or 0
                    for msg in messages["assistant_messages"]
                )
                total_tokens_out = sum(
                    msg.tokens_out or 0
                    for msg in messages["assistant_messages"]
                )

                tool_count = len(messages["tool_uses"])
                successful_tools = sum(
                    1 for tool in messages["tool_uses"] if tool.success
                )

                # Get all timestamps
                timestamps = []
                user_msgs = messages["user_messages"]
                asst_msgs = messages["assistant_messages"]
                for msg in user_msgs + asst_msgs:
                    timestamps.append(msg.timestamp)

                msg_count = len(user_msgs) + len(asst_msgs)

                return JSONResponse(content={
                    "session_id": session_id,
                    "message_count": msg_count,
                    "user_messages": len(user_msgs),
                    "assistant_messages": len(asst_msgs),
                    "tool_uses": tool_count,
                    "successful_tools": successful_tools,
                    "total_tokens_in": total_tokens_in,
                    "total_tokens_out": total_tokens_out,
                    "first_timestamp": (
                        min(timestamps).isoformat()
                        if timestamps else None
                    ),
                    "last_timestamp": (
                        max(timestamps).isoformat()
                        if timestamps else None
                    )
                })
            except Exception as e:
                logger.error("Error getting session: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/sessions/{session_id}/events")
        async def get_session_events(session_id: str):
            """Get events timeline for a session (alias for timeline)."""
            # Reuse the timeline endpoint
            return await get_conversation_timeline(session_id)

        @self.app.get("/api/analytics/overview")
        async def get_analytics_overview():
            """Get overview analytics across all data."""
            try:
                conv_mgr = self.uacs.conversation_manager
                knowledge_mgr = self.uacs.knowledge_manager

                conv_stats = conv_mgr.get_stats()
                knowledge_stats = knowledge_mgr.get_stats()

                # Calculate token usage over time (last 30 days)
                # This is a simplified version - could be enhanced
                all_asst_msgs = conv_mgr._assistant_messages
                recent_tokens_in = sum(
                    msg.tokens_in or 0 for msg in all_asst_msgs
                )
                recent_tokens_out = sum(
                    msg.tokens_out or 0 for msg in all_asst_msgs
                )

                return JSONResponse(content={
                    "conversations": {
                        "total_sessions": conv_stats["total_sessions"],
                        "total_user_messages": (
                            conv_stats["total_user_messages"]
                        ),
                        "total_assistant_messages": (
                            conv_stats["total_assistant_messages"]
                        ),
                        "total_tool_uses": conv_stats["total_tool_uses"]
                    },
                    "knowledge": {
                        "conventions": knowledge_stats["conventions"],
                        "decisions": knowledge_stats["decisions"],
                        "learnings": knowledge_stats["learnings"],
                        "artifacts": knowledge_stats["artifacts"],
                        "total_items": knowledge_stats["total_items"]
                    },
                    "tokens": {
                        "total_input": recent_tokens_in,
                        "total_output": recent_tokens_out,
                        "total": recent_tokens_in + recent_tokens_out
                    }
                })
            except Exception as e:
                logger.error("Error getting analytics overview: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/analytics/topics")
        async def get_analytics_topics():
            """Get topic clusters and frequencies."""
            try:
                # Collect topics from all sources
                topic_counts = {}

                # From conversations
                conv_mgr = self.uacs.conversation_manager
                for msg in conv_mgr._user_messages:
                    for topic in msg.topics:
                        topic_counts[topic] = (
                            topic_counts.get(topic, 0) + 1
                        )

                # From knowledge
                knowledge_mgr = self.uacs.knowledge_manager
                for conv in knowledge_mgr.conventions.values():
                    for topic in conv.topics:
                        topic_counts[topic] = (
                            topic_counts.get(topic, 0) + 1
                        )

                for dec in knowledge_mgr.decisions.values():
                    for topic in dec.topics:
                        topic_counts[topic] = (
                            topic_counts.get(topic, 0) + 1
                        )

                for art in knowledge_mgr.artifacts.values():
                    for topic in art.topics:
                        topic_counts[topic] = (
                            topic_counts.get(topic, 0) + 1
                        )
                
                # Sort by frequency
                topics = [
                    {"topic": topic, "count": count}
                    for topic, count in topic_counts.items()
                ]
                topics.sort(key=lambda x: x["count"], reverse=True)
                
                return JSONResponse(content={
                    "topics": topics,
                    "total_unique_topics": len(topics)
                })
            except Exception as e:
                logger.error("Error getting topic analytics: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

        @self.app.get("/api/analytics/tokens")
        async def get_analytics_tokens():
            """Get token usage over time."""
            try:
                # Group messages by date
                from collections import defaultdict

                daily_tokens = defaultdict(lambda: {"in": 0, "out": 0})

                conv_mgr = self.uacs.conversation_manager
                for msg in conv_mgr._assistant_messages:
                    date_key = msg.timestamp.date().isoformat()
                    daily_tokens[date_key]["in"] += msg.tokens_in or 0
                    daily_tokens[date_key]["out"] += msg.tokens_out or 0
                
                # Convert to list and sort
                token_timeline = [
                    {
                        "date": date,
                        "tokens_in": tokens["in"],
                        "tokens_out": tokens["out"],
                        "total": tokens["in"] + tokens["out"]
                    }
                    for date, tokens in daily_tokens.items()
                ]
                token_timeline.sort(key=lambda x: x["date"])
                
                return JSONResponse(content={
                    "timeline": token_timeline,
                    "total_days": len(token_timeline)
                })
            except Exception as e:
                logger.error("Error getting token analytics: %s", e)
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=500
                )

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
        unique_hashes = set(
            entry.hash
            for entry in self.context_manager.entries.values()
        )

        # Count duplicates prevented by dedup index
        total_entries = len(self.context_manager.entries)
        dedup_index_size = len(self.context_manager.dedup_index)
        total_possible = (
            total_entries + dedup_index_size - len(unique_hashes)
        )
        duplicates_prevented = dedup_index_size - len(unique_hashes)

        dedup_rate = (
            f"{(duplicates_prevented / total_possible * 100):.1f}%"
            if total_possible > 0
            else "0%"
        )

        return {
            "unique_entries": len(unique_hashes),
            "total_entries": total_entries,
            "duplicates_prevented": duplicates_prevented,
            "deduplication_rate": dedup_rate,
        }

    def _get_quality_distribution(self) -> dict[str, Any]:
        """Get quality distribution of entries.

        Returns:
            Dictionary with quality distribution data
        """
        qualities = [
            entry.quality
            for entry in self.context_manager.entries.values()
        ]

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

    # ====== Serialization Helpers (v0.3.0+) ======

    def _serialize_search_result(self, result: SearchResult) -> dict:
        """Serialize SearchResult to JSON."""
        result_type = (
            result.type
            if hasattr(result, 'type')
            else result.metadata.get('type')
        )
        text = (
            result.text
            if hasattr(result, 'text')
            else result.content
            if hasattr(result, 'content')
            else ""
        )
        content = (
            result.content
            if hasattr(result, 'content')
            else result.text
            if hasattr(result, 'text')
            else ""
        )
        similarity = (
            result.similarity
            if hasattr(result, 'similarity')
            else result.relevance_score
            if hasattr(result, 'relevance_score')
            else 0
        )
        return {
            "type": result_type,
            "text": text,
            "content": content,
            "similarity": similarity,
            "metadata": result.metadata if result.metadata else {},
        }

    def _serialize_user_message(self, msg) -> dict:
        """Serialize UserMessage to JSON."""
        return {
            "content": msg.content,
            "turn": msg.turn,
            "session_id": msg.session_id,
            "topics": msg.topics,
            "timestamp": msg.timestamp.isoformat(),
        }

    def _serialize_assistant_message(self, msg) -> dict:
        """Serialize AssistantMessage to JSON."""
        return {
            "content": msg.content,
            "turn": msg.turn,
            "session_id": msg.session_id,
            "tokens_in": msg.tokens_in,
            "tokens_out": msg.tokens_out,
            "model": msg.model,
            "timestamp": msg.timestamp.isoformat(),
        }

    def _serialize_tool_use(self, tool) -> dict:
        """Serialize ToolUse to JSON."""
        return {
            "tool_name": tool.tool_name,
            "tool_input": tool.tool_input,
            "tool_response": tool.tool_response,
            "turn": tool.turn,
            "session_id": tool.session_id,
            "latency_ms": tool.latency_ms,
            "success": tool.success,
            "timestamp": tool.timestamp.isoformat(),
        }

    def _serialize_decision(self, decision) -> dict:
        """Serialize Decision to JSON."""
        return {
            "question": decision.question,
            "decision": decision.decision,
            "rationale": decision.rationale,
            "alternatives": decision.alternatives,
            "decided_at": decision.decided_at.isoformat(),
            "decided_by": decision.decided_by,
            "session_id": decision.session_id,
            "topics": decision.topics,
        }

    def _serialize_convention(self, convention) -> dict:
        """Serialize Convention to JSON."""
        last_verified = (
            convention.last_verified.isoformat()
            if convention.last_verified
            else None
        )
        return {
            "content": convention.content,
            "topics": convention.topics,
            "source_session": convention.source_session,
            "confidence": convention.confidence,
            "created_at": convention.created_at.isoformat(),
            "last_verified": last_verified,
        }

    def _serialize_learning(self, learning) -> dict:
        """Serialize Learning to JSON."""
        return {
            "pattern": learning.pattern,
            "confidence": learning.confidence,
            "learned_from": learning.learned_from,
            "category": learning.category,
            "created_at": learning.created_at.isoformat(),
        }

    def _serialize_artifact(self, artifact) -> dict:
        """Serialize Artifact to JSON."""
        return {
            "type": artifact.type,
            "path": artifact.path,
            "description": artifact.description,
            "created_in_session": artifact.created_in_session,
            "topics": artifact.topics,
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
    uacs: "UACS",
    host: str = "localhost",
    port: int = 8081,
) -> VisualizationServer:
    """Start the visualization server.

    Args:
        uacs: UACS instance
        host: Server host
        port: Server port

    Returns:
        VisualizationServer instance
    """
    import uvicorn

    server = VisualizationServer(uacs, host, port)

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
