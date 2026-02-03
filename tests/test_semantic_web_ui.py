"""Integration tests for UACS v0.3.0 Web UI Semantic API endpoints.

Tests all new semantic endpoints added to the visualization server,
including search, conversations, knowledge, sessions, and analytics.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from pathlib import Path

from uacs import UACS
from uacs.visualization.web_server import VisualizationServer


@pytest.fixture
def test_project(tmp_path):
    """Create a test project with comprehensive sample data."""
    project_path = tmp_path / "test_project"
    project_path.mkdir()
    
    # Initialize UACS
    uacs = UACS(project_path=project_path)
    
    # Session 1: Authentication-related conversation
    uacs.add_user_message(
        content="I need help implementing authentication in my web app",
        turn=1,
        session_id="session_001",
        topics=["security", "authentication"]
    )
    
    uacs.add_assistant_message(
        content="I can help you with that. Let's discuss JWT tokens vs sessions.",
        turn=1,
        session_id="session_001",
        tokens_in=500,
        tokens_out=150,
        model="claude-3-5-sonnet"
    )
    
    uacs.add_tool_use(
        tool_name="read_file",
        tool_input={"path": "auth.py"},
        tool_response="# Authentication module...",
        turn=1,
        session_id="session_001",
        latency_ms=125.5,
        success=True
    )
    
    uacs.add_user_message(
        content="What's the best approach for API authentication?",
        turn=2,
        session_id="session_001",
        topics=["security", "api", "authentication"]
    )
    
    uacs.add_assistant_message(
        content="JWT tokens are ideal for stateless API authentication.",
        turn=2,
        session_id="session_001",
        tokens_in=600,
        tokens_out=200,
        model="claude-3-5-sonnet"
    )
    
    uacs.add_decision(
        question="How should we handle API authentication?",
        decision="Use JWT tokens with RS256 signing",
        rationale="Stateless, scalable, and industry-standard approach",
        session_id="session_001",
        alternatives=["Session cookies", "OAuth2", "API keys"],
        topics=["security", "authentication", "api"]
    )
    
    uacs.add_convention(
        content="Always use bcrypt with cost factor >= 12 for password hashing",
        topics=["security", "passwords"],
        source_session="session_001"
    )
    
    uacs.add_artifact(
        type="code",
        path="src/auth/jwt_handler.py",
        description="JWT token generation and validation logic",
        created_in_session="session_001",
        topics=["security", "authentication"]
    )
    
    # Session 2: Database-related conversation
    uacs.add_user_message(
        content="How should I structure my database schema?",
        turn=1,
        session_id="session_002",
        topics=["database", "design"]
    )
    
    uacs.add_assistant_message(
        content="Let's analyze your requirements and design the schema.",
        turn=1,
        session_id="session_002",
        tokens_in=400,
        tokens_out=100,
        model="claude-3-5-sonnet"
    )
    
    uacs.add_decision(
        question="Which database should we use?",
        decision="PostgreSQL for primary database",
        rationale="ACID compliance, robust indexing, and JSON support",
        session_id="session_002",
        alternatives=["MySQL", "MongoDB", "SQLite"],
        topics=["database", "infrastructure"]
    )
    
    uacs.add_convention(
        content="Use snake_case for all database column names",
        topics=["database", "naming"],
        source_session="session_002"
    )
    
    uacs.add_learning(
        pattern="Users prefer explicit foreign key constraints",
        confidence=0.85,
        learned_from="session_002",
        category="database_design"
    )
    
    # Session 3: Recent session with different topic
    uacs.add_user_message(
        content="Help me optimize this slow query",
        turn=1,
        session_id="session_003",
        topics=["performance", "database", "optimization"]
    )
    
    uacs.add_assistant_message(
        content="Let me analyze the query and suggest optimizations.",
        turn=1,
        session_id="session_003",
        tokens_in=300,
        tokens_out=80,
        model="claude-3-5-sonnet"
    )
    
    uacs.add_convention(
        content="Add indexes on all foreign key columns by default",
        topics=["database", "performance"],
        source_session="session_003"
    )
    
    return uacs


@pytest.fixture
def client(request, tmp_path):
    """Create FastAPI test client with initialized UACS.
    
    Uses lazy loading - only creates test data when needed.
    """
    # Check if test needs sample data
    needs_data = "no_data" not in request.keywords
    
    if needs_data:
        # Create test project with data
        uacs = request.getfixturevalue("test_project")
    else:
        # Create empty project
        project_path = tmp_path / "empty_project"
        project_path.mkdir()
        uacs = UACS(project_path=project_path)
    
    server = VisualizationServer(uacs=uacs)
    return TestClient(server.app)


# ==================== Search Endpoint Tests ====================

def test_search_endpoint_basic(client):
    """Test basic semantic search functionality."""
    response = client.post("/api/search", json={
        "query": "authentication",
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert isinstance(data["results"], list)
    assert data["count"] >= 0


def test_search_with_types_filter(client):
    """Test search with type filtering."""
    response = client.post("/api/search", json={
        "query": "authentication",
        "types": ["decision"],
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    # All results should be decisions if any returned
    for result in data["results"]:
        if "type" in result:
            assert result["type"] == "decision"


def test_search_with_session_filter(client):
    """Test search with session ID filtering."""
    response = client.post("/api/search", json={
        "query": "authentication",
        "session_id": "session_001",
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_search_with_min_confidence(client):
    """Test search with minimum confidence threshold."""
    response = client.post("/api/search", json={
        "query": "database",
        "min_confidence": 0.8,
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    # All results should meet confidence threshold
    for result in data["results"]:
        if "similarity" in result:
            assert result["similarity"] >= 0.8


def test_search_empty_query(client):
    """Test search endpoint handles empty query."""
    response = client.post("/api/search", json={
        "query": "",
        "limit": 10
    })
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "query is required" in data["error"]


def test_search_no_results(client):
    """Test search returns empty array when no matches found."""
    response = client.post("/api/search", json={
        "query": "nonexistent_xyzabc_topic_12345",
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    # May be empty or have low-confidence results
    assert data["count"] >= 0


def test_search_invalid_json(client):
    """Test search endpoint handles invalid JSON."""
    response = client.post(
        "/api/search",
        data="invalid json {{{",
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 422  # FastAPI validation error


# ==================== Conversation Endpoint Tests ====================

def test_list_conversations(client):
    """Test listing all conversations with pagination."""
    response = client.get("/api/conversations?skip=0&limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["conversations"], list)
    assert data["total"] >= 3  # We created 3 sessions
    
    # Check conversation structure
    if data["conversations"]:
        conv = data["conversations"][0]
        assert "session_id" in conv
        assert "message_count" in conv
        assert "turn_count" in conv
        assert "first_message" in conv
        assert "last_message" in conv


def test_list_conversations_with_session_filter(client):
    """Test conversation listing with session ID filter."""
    response = client.get("/api/conversations?session_id=session_001")
    
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    
    # Should only return session_001
    for conv in data["conversations"]:
        assert conv["session_id"] == "session_001"


def test_list_conversations_pagination(client):
    """Test conversation pagination works correctly."""
    # Get first page
    response1 = client.get("/api/conversations?skip=0&limit=1")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Get second page
    response2 = client.get("/api/conversations?skip=1&limit=1")
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Pages should be different (if we have enough data)
    if data1["total"] >= 2:
        assert data1["conversations"][0]["session_id"] != data2["conversations"][0]["session_id"]


def test_get_conversation_by_id(client):
    """Test getting specific conversation by session ID."""
    response = client.get("/api/conversations/session_001")
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] == "session_001"
    assert "user_messages" in data
    assert "assistant_messages" in data
    assert "tool_uses" in data
    assert isinstance(data["user_messages"], list)
    assert isinstance(data["assistant_messages"], list)
    assert isinstance(data["tool_uses"], list)
    
    # Verify message structure
    if data["user_messages"]:
        msg = data["user_messages"][0]
        assert "content" in msg
        assert "turn" in msg
        assert "session_id" in msg
        assert "topics" in msg
        assert "timestamp" in msg


def test_get_conversation_timeline(client):
    """Test getting conversation timeline view."""
    response = client.get("/api/conversations/session_001/timeline")
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] == "session_001"
    assert "timeline" in data
    assert "event_count" in data
    assert isinstance(data["timeline"], list)
    
    # Verify timeline events are sorted by turn/timestamp
    if len(data["timeline"]) > 1:
        for i in range(len(data["timeline"]) - 1):
            curr = data["timeline"][i]
            next_event = data["timeline"][i + 1]
            assert curr["turn"] <= next_event["turn"]
    
    # Verify event structure
    if data["timeline"]:
        event = data["timeline"][0]
        assert "type" in event
        assert "turn" in event
        assert "timestamp" in event


def test_get_nonexistent_conversation(client):
    """Test getting conversation that doesn't exist."""
    response = client.get("/api/conversations/nonexistent_session_xyz")
    
    # Should return 200 with empty data structures (not 404)
    assert response.status_code == 200
    data = response.json()
    assert "user_messages" in data
    assert len(data["user_messages"]) == 0


# ==================== Knowledge Endpoint Tests ====================

def test_list_decisions(client):
    """Test listing all decisions."""
    response = client.get("/api/knowledge/decisions?skip=0&limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert "decisions" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["decisions"], list)
    assert data["total"] >= 2  # We created 2 decisions
    
    # Verify decision structure
    if data["decisions"]:
        decision = data["decisions"][0]
        assert "question" in decision
        assert "decision" in decision
        assert "rationale" in decision
        assert "alternatives" in decision
        assert "decided_at" in decision
        assert "session_id" in decision
        assert "topics" in decision


def test_list_decisions_with_session_filter(client):
    """Test decisions filtering by session ID."""
    response = client.get("/api/knowledge/decisions?session_id=session_001")
    
    assert response.status_code == 200
    data = response.json()
    assert "decisions" in data
    
    # All returned decisions should be from session_001
    for decision in data["decisions"]:
        assert decision["session_id"] == "session_001"


def test_list_decisions_with_topics_filter(client):
    """Test decisions filtering by topics."""
    response = client.get("/api/knowledge/decisions?topics=security,authentication")
    
    assert response.status_code == 200
    data = response.json()
    assert "decisions" in data
    
    # All returned decisions should have at least one matching topic
    for decision in data["decisions"]:
        topics = decision["topics"]
        assert any(t in ["security", "authentication"] for t in topics)


def test_list_conventions(client):
    """Test listing all conventions."""
    response = client.get("/api/knowledge/conventions?skip=0&limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert "conventions" in data
    assert "total" in data
    assert isinstance(data["conventions"], list)
    assert data["total"] >= 3  # We created 3 conventions
    
    # Verify convention structure
    if data["conventions"]:
        convention = data["conventions"][0]
        assert "content" in convention
        assert "topics" in convention
        assert "source_session" in convention
        assert "confidence" in convention
        assert "created_at" in convention


def test_list_conventions_with_topics_filter(client):
    """Test conventions filtering by topics."""
    response = client.get("/api/knowledge/conventions?topics=database")
    
    assert response.status_code == 200
    data = response.json()
    assert "conventions" in data
    
    # All returned conventions should have "database" topic
    for convention in data["conventions"]:
        assert "database" in convention["topics"]


def test_list_conventions_with_min_confidence(client):
    """Test conventions filtering by minimum confidence."""
    response = client.get("/api/knowledge/conventions?min_confidence=0.8")
    
    assert response.status_code == 200
    data = response.json()
    assert "conventions" in data
    
    # All returned conventions should meet confidence threshold
    for convention in data["conventions"]:
        assert convention["confidence"] >= 0.8


def test_list_learnings(client):
    """Test listing all learnings."""
    response = client.get("/api/knowledge/learnings?skip=0&limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert "learnings" in data
    assert "total" in data
    assert isinstance(data["learnings"], list)
    assert data["total"] >= 1  # We created 1 learning
    
    # Verify learning structure
    if data["learnings"]:
        learning = data["learnings"][0]
        assert "pattern" in learning
        assert "confidence" in learning
        assert "learned_from" in learning
        assert "category" in learning
        assert "created_at" in learning


def test_list_learnings_with_category_filter(client):
    """Test learnings filtering by category."""
    response = client.get("/api/knowledge/learnings?category=database_design")
    
    assert response.status_code == 200
    data = response.json()
    assert "learnings" in data
    
    # All returned learnings should be from specified category
    for learning in data["learnings"]:
        assert learning["category"] == "database_design"


def test_list_learnings_with_min_confidence(client):
    """Test learnings filtering by minimum confidence."""
    response = client.get("/api/knowledge/learnings?min_confidence=0.8")
    
    assert response.status_code == 200
    data = response.json()
    assert "learnings" in data
    
    # All returned learnings should meet confidence threshold
    for learning in data["learnings"]:
        assert learning["confidence"] >= 0.8


def test_list_artifacts(client):
    """Test listing all artifacts."""
    response = client.get("/api/knowledge/artifacts?skip=0&limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert "artifacts" in data
    assert "total" in data
    assert isinstance(data["artifacts"], list)
    assert data["total"] >= 1  # We created 1 artifact
    
    # Verify artifact structure
    if data["artifacts"]:
        artifact = data["artifacts"][0]
        assert "type" in artifact
        assert "path" in artifact
        assert "description" in artifact
        assert "created_in_session" in artifact
        assert "topics" in artifact


def test_list_artifacts_with_session_filter(client):
    """Test artifacts filtering by session ID."""
    response = client.get("/api/knowledge/artifacts?session_id=session_001")
    
    assert response.status_code == 200
    data = response.json()
    assert "artifacts" in data
    
    # All returned artifacts should be from session_001
    for artifact in data["artifacts"]:
        assert artifact["created_in_session"] == "session_001"


def test_list_artifacts_with_type_filter(client):
    """Test artifacts filtering by artifact type."""
    response = client.get("/api/knowledge/artifacts?artifact_type=code")
    
    assert response.status_code == 200
    data = response.json()
    assert "artifacts" in data
    
    # All returned artifacts should be of type "code"
    for artifact in data["artifacts"]:
        assert artifact["type"] == "code"


def test_list_artifacts_with_topics_filter(client):
    """Test artifacts filtering by topics."""
    response = client.get("/api/knowledge/artifacts?topics=security,authentication")
    
    assert response.status_code == 200
    data = response.json()
    assert "artifacts" in data
    
    # All returned artifacts should have at least one matching topic
    for artifact in data["artifacts"]:
        topics = artifact["topics"]
        assert any(t in ["security", "authentication"] for t in topics)


# ==================== Session Endpoint Tests ====================

def test_list_sessions(client):
    """Test listing all sessions with metadata."""
    response = client.get("/api/sessions?skip=0&limit=50")
    
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert isinstance(data["sessions"], list)
    assert data["total"] >= 3  # We created 3 sessions
    
    # Verify session structure
    if data["sessions"]:
        session = data["sessions"][0]
        assert "session_id" in session
        assert "message_count" in session
        assert "turn_count" in session
        assert "first_timestamp" in session
        assert "last_timestamp" in session
        assert "total_tokens_in" in session
        assert "total_tokens_out" in session


def test_list_sessions_pagination(client):
    """Test session pagination works correctly."""
    # Get first page
    response1 = client.get("/api/sessions?skip=0&limit=2")
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Get second page
    response2 = client.get("/api/sessions?skip=2&limit=2")
    assert response2.status_code == 200
    data2 = response2.json()
    
    assert data1["skip"] == 0
    assert data2["skip"] == 2


def test_get_session_by_id(client):
    """Test getting specific session details."""
    response = client.get("/api/sessions/session_001")
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] == "session_001"
    assert "message_count" in data
    assert "user_messages" in data
    assert "assistant_messages" in data
    assert "tool_uses" in data
    assert "successful_tools" in data
    assert "total_tokens_in" in data
    assert "total_tokens_out" in data
    assert "first_timestamp" in data
    assert "last_timestamp" in data
    
    # Verify token counts are correct
    assert data["total_tokens_in"] > 0
    assert data["total_tokens_out"] > 0


def test_get_session_events(client):
    """Test getting session events timeline."""
    response = client.get("/api/sessions/session_001/events")
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "timeline" in data
    assert "event_count" in data
    assert isinstance(data["timeline"], list)
    
    # Events should include various types
    event_types = {event["type"] for event in data["timeline"]}
    assert len(event_types) > 0


def test_get_nonexistent_session(client):
    """Test getting session that doesn't exist."""
    response = client.get("/api/sessions/nonexistent_session_xyz")
    
    # Should return 200 with zero counts (not 404)
    assert response.status_code == 200
    data = response.json()
    assert data["message_count"] == 0


# ==================== Analytics Endpoint Tests ====================

def test_analytics_overview(client):
    """Test analytics overview endpoint."""
    response = client.get("/api/analytics/overview")
    
    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "knowledge" in data
    assert "tokens" in data
    
    # Verify conversation stats
    conv_stats = data["conversations"]
    assert "total_sessions" in conv_stats
    assert "total_user_messages" in conv_stats
    assert "total_assistant_messages" in conv_stats
    assert "total_tool_uses" in conv_stats
    assert conv_stats["total_sessions"] >= 3
    
    # Verify knowledge stats
    knowledge_stats = data["knowledge"]
    assert "conventions" in knowledge_stats
    assert "decisions" in knowledge_stats
    assert "learnings" in knowledge_stats
    assert "artifacts" in knowledge_stats
    assert "total_items" in knowledge_stats
    
    # Verify token stats
    token_stats = data["tokens"]
    assert "total_input" in token_stats
    assert "total_output" in token_stats
    assert "total" in token_stats
    assert token_stats["total"] > 0


def test_analytics_topics(client):
    """Test analytics topic clusters endpoint."""
    response = client.get("/api/analytics/topics")
    
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    assert "total_unique_topics" in data
    assert isinstance(data["topics"], list)
    assert data["total_unique_topics"] > 0
    
    # Verify topic structure
    if data["topics"]:
        topic = data["topics"][0]
        assert "topic" in topic
        assert "count" in topic
        assert topic["count"] > 0
    
    # Verify topics are sorted by count (descending)
    if len(data["topics"]) > 1:
        counts = [t["count"] for t in data["topics"]]
        assert counts == sorted(counts, reverse=True)


def test_analytics_tokens(client):
    """Test analytics token usage over time endpoint."""
    response = client.get("/api/analytics/tokens")
    
    assert response.status_code == 200
    data = response.json()
    assert "timeline" in data
    assert "total_days" in data
    assert isinstance(data["timeline"], list)
    
    # Verify timeline structure
    if data["timeline"]:
        day = data["timeline"][0]
        assert "date" in day
        assert "tokens_in" in day
        assert "tokens_out" in day
        assert "total" in day
        assert day["total"] == day["tokens_in"] + day["tokens_out"]
    
    # Verify timeline is sorted by date
    if len(data["timeline"]) > 1:
        dates = [t["date"] for t in data["timeline"]]
        assert dates == sorted(dates)


# ==================== Error Handling Tests ====================

@pytest.mark.no_data
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_search_missing_query(client):
    """Test search without query parameter."""
    response = client.post("/api/search", json={
        "limit": 10
    })
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_invalid_pagination_parameters(client):
    """Test endpoints handle invalid pagination gracefully."""
    # Negative skip should still work (treated as 0)
    response = client.get("/api/conversations?skip=-5&limit=10")
    assert response.status_code == 200
    
    # Very large limit should still work
    response = client.get("/api/sessions?skip=0&limit=10000")
    assert response.status_code == 200


def test_conversation_endpoint_with_malformed_session_id(client):
    """Test conversation endpoint with special characters in session ID."""
    # Should handle special characters gracefully
    response = client.get("/api/conversations/session_with_special_chars!@#")
    assert response.status_code == 200


def test_multiple_filter_combinations(client):
    """Test combining multiple filters works correctly."""
    response = client.get(
        "/api/knowledge/decisions"
        "?session_id=session_001"
        "&topics=security"
        "&skip=0"
        "&limit=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "decisions" in data


def test_empty_database_responses(client, tmp_path):
    """Test endpoints return appropriate empty responses with no data."""
    # Create fresh UACS with no data
    empty_project = tmp_path / "empty_project"
    empty_project.mkdir()
    uacs_empty = UACS(project_path=empty_project)
    
    server = VisualizationServer(uacs=uacs_empty)
    empty_client = TestClient(server.app)
    
    # Test various endpoints
    response = empty_client.get("/api/conversations")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    
    response = empty_client.get("/api/sessions")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    
    response = empty_client.get("/api/knowledge/decisions")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    
    response = empty_client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["conversations"]["total_sessions"] == 0


# ==================== Integration Tests ====================

def test_full_workflow_integration(client):
    """Test complete workflow: search -> get conversation -> get session."""
    # 1. Search for authentication-related content
    search_response = client.post("/api/search", json={
        "query": "authentication",
        "limit": 5
    })
    assert search_response.status_code == 200
    
    # 2. List conversations
    conv_response = client.get("/api/conversations?limit=10")
    assert conv_response.status_code == 200
    conversations = conv_response.json()["conversations"]
    
    if conversations:
        session_id = conversations[0]["session_id"]
        
        # 3. Get full conversation
        full_conv_response = client.get(f"/api/conversations/{session_id}")
        assert full_conv_response.status_code == 200
        
        # 4. Get session details
        session_response = client.get(f"/api/sessions/{session_id}")
        assert session_response.status_code == 200
        
        # 5. Get session timeline
        timeline_response = client.get(f"/api/sessions/{session_id}/events")
        assert timeline_response.status_code == 200


def test_analytics_consistency(client):
    """Test that analytics data is consistent across endpoints."""
    # Get overview
    overview = client.get("/api/analytics/overview").json()
    
    # Get individual counts
    conversations = client.get("/api/conversations").json()
    sessions = client.get("/api/sessions").json()
    decisions = client.get("/api/knowledge/decisions").json()
    conventions = client.get("/api/knowledge/conventions").json()
    
    # Verify consistency
    assert overview["conversations"]["total_sessions"] == sessions["total"]
    assert overview["knowledge"]["decisions"] == decisions["total"]
    assert overview["knowledge"]["conventions"] == conventions["total"]


def test_topic_consistency_across_endpoints(client):
    """Test that topics are consistent across different endpoints."""
    # Get topics from analytics
    analytics_topics = client.get("/api/analytics/topics").json()
    topic_names = {t["topic"] for t in analytics_topics["topics"]}
    
    # Get topics from decisions
    decisions = client.get("/api/knowledge/decisions").json()
    decision_topics = set()
    for decision in decisions["decisions"]:
        decision_topics.update(decision["topics"])
    
    # Analytics should include decision topics
    assert decision_topics.issubset(topic_names)


def test_timestamp_ordering(client):
    """Test that all timestamp-based ordering works correctly."""
    # Test conversations (should be ordered by last_message)
    conversations = client.get("/api/conversations").json()["conversations"]
    if len(conversations) > 1:
        for i in range(len(conversations) - 1):
            curr_time = conversations[i]["last_message"]
            next_time = conversations[i + 1]["last_message"]
            assert curr_time >= next_time  # Descending order
    
    # Test sessions (should be ordered by last_timestamp)
    sessions = client.get("/api/sessions").json()["sessions"]
    if len(sessions) > 1:
        for i in range(len(sessions) - 1):
            curr_time = sessions[i]["last_timestamp"]
            next_time = sessions[i + 1]["last_timestamp"]
            assert curr_time >= next_time  # Descending order


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
