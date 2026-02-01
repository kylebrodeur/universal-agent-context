"""Tests for visualization web server."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from uacs.context.shared_context import SharedContextManager
from uacs.visualization.web_server import VisualizationServer


@pytest.fixture
def context_manager(tmp_path: Path) -> SharedContextManager:
    """Create a test context manager.

    Args:
        tmp_path: Temporary directory path

    Returns:
        SharedContextManager instance
    """
    return SharedContextManager(storage_path=tmp_path / "context")


@pytest.fixture
def viz_server(context_manager: SharedContextManager) -> VisualizationServer:
    """Create a test visualization server.

    Args:
        context_manager: Test context manager

    Returns:
        VisualizationServer instance
    """
    return VisualizationServer(context_manager, host="localhost", port=8081)


@pytest.fixture
def client(viz_server: VisualizationServer) -> TestClient:
    """Create a test client.

    Args:
        viz_server: Visualization server

    Returns:
        TestClient instance
    """
    return TestClient(viz_server.app)


def test_health_endpoint(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_endpoint(client: TestClient):
    """Test index page endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_graph_empty(client: TestClient):
    """Test get graph endpoint with empty context."""
    response = client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "stats" in data
    assert len(data["nodes"]) == 0


def test_get_graph_with_data(
    client: TestClient, context_manager: SharedContextManager
):
    """Test get graph endpoint with context data."""
    # Add some test entries
    context_manager.add_entry("Test content 1", agent="test-agent")
    context_manager.add_entry("Test content 2", agent="test-agent", topics=["test"])

    response = client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 2
    assert data["nodes"][0]["type"] == "entry"
    assert data["nodes"][0]["agent"] == "test-agent"


def test_get_stats_empty(client: TestClient):
    """Test get stats endpoint with empty context."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["entry_count"] == 0
    assert data["summary_count"] == 0
    assert data["total_tokens"] == 0


def test_get_stats_with_data(
    client: TestClient, context_manager: SharedContextManager
):
    """Test get stats endpoint with context data."""
    context_manager.add_entry("Test content", agent="test-agent")

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["entry_count"] == 1
    assert data["total_tokens"] > 0
    assert "compression_ratio" in data
    assert "storage_size_mb" in data


def test_get_topics_empty(client: TestClient):
    """Test get topics endpoint with empty context."""
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert "clusters" in data
    assert "total_topics" in data
    assert len(data["clusters"]) == 0


def test_get_topics_with_data(
    client: TestClient, context_manager: SharedContextManager
):
    """Test get topics endpoint with context data."""
    context_manager.add_entry("Test content 1", agent="test-agent", topics=["test", "demo"])
    context_manager.add_entry("Test content 2", agent="test-agent", topics=["test"])

    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert len(data["clusters"]) == 2
    assert data["total_topics"] == 2

    # Check topic counts
    test_cluster = next(c for c in data["clusters"] if c["topic"] == "test")
    assert test_cluster["count"] == 2

    demo_cluster = next(c for c in data["clusters"] if c["topic"] == "demo")
    assert demo_cluster["count"] == 1


def test_get_deduplication_empty(client: TestClient):
    """Test get deduplication endpoint with empty context."""
    response = client.get("/api/deduplication")
    assert response.status_code == 200
    data = response.json()
    assert "unique_entries" in data
    assert "total_entries" in data
    assert "duplicates_prevented" in data
    assert "deduplication_rate" in data


def test_get_deduplication_with_data(
    client: TestClient, context_manager: SharedContextManager
):
    """Test get deduplication endpoint with context data."""
    # Add entries (second one is duplicate)
    context_manager.add_entry("Test content", agent="test-agent")
    context_manager.add_entry("Test content", agent="test-agent")  # Duplicate
    context_manager.add_entry("Different content", agent="test-agent")

    response = client.get("/api/deduplication")
    assert response.status_code == 200
    data = response.json()
    assert data["unique_entries"] == 2
    assert data["total_entries"] == 2  # Duplicate was not added


def test_get_quality_empty(client: TestClient):
    """Test get quality endpoint with empty context."""
    response = client.get("/api/quality")
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert "average" in data
    assert data["average"] == 0


def test_get_quality_with_data(
    client: TestClient, context_manager: SharedContextManager
):
    """Test get quality endpoint with context data."""
    # Add entries with different quality levels
    context_manager.add_entry("High quality content with code block ```python\nprint('test')\n```", agent="test-agent")
    context_manager.add_entry("Short", agent="test-agent")  # Low quality

    response = client.get("/api/quality")
    assert response.status_code == 200
    data = response.json()
    assert len(data["distribution"]) == 3
    assert data["average"] > 0
    assert data["high_quality"] >= 0
    assert data["medium_quality"] >= 0
    assert data["low_quality"] >= 0


def test_topic_clusters_sorting(
    client: TestClient, context_manager: SharedContextManager
):
    """Test that topic clusters are sorted by count."""
    # Add entries with different topic frequencies
    context_manager.add_entry("Content 1", agent="test-agent", topics=["popular"])
    context_manager.add_entry("Content 2", agent="test-agent", topics=["popular"])
    context_manager.add_entry("Content 3", agent="test-agent", topics=["popular"])
    context_manager.add_entry("Content 4", agent="test-agent", topics=["rare"])

    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()

    # First cluster should be the most popular
    assert data["clusters"][0]["topic"] == "popular"
    assert data["clusters"][0]["count"] == 3
    assert data["clusters"][1]["topic"] == "rare"
    assert data["clusters"][1]["count"] == 1


def test_graph_with_references(
    client: TestClient, context_manager: SharedContextManager
):
    """Test graph endpoint with entry references."""
    entry1_id = context_manager.add_entry("First entry", agent="test-agent")
    entry2_id = context_manager.add_entry(
        "Second entry", agent="test-agent", references=[entry1_id]
    )

    response = client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()

    # Should have 2 nodes and 1 edge
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["edges"][0]["source"] == entry2_id
    assert data["edges"][0]["target"] == entry1_id
    assert data["edges"][0]["type"] == "reference"


def test_graph_with_summaries(
    client: TestClient, context_manager: SharedContextManager
):
    """Test graph endpoint with summaries."""
    entry1_id = context_manager.add_entry("Entry 1", agent="test-agent")
    entry2_id = context_manager.add_entry("Entry 2", agent="test-agent")

    # Create a summary
    summary_id = context_manager.create_summary(
        [entry1_id, entry2_id], "Summary of entries"
    )

    response = client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()

    # Should have 1 summary node and 2 edges
    summary_nodes = [n for n in data["nodes"] if n["type"] == "summary"]
    assert len(summary_nodes) == 1
    assert summary_nodes[0]["id"] == summary_id

    # Should have edges from summary to entries
    summary_edges = [e for e in data["edges"] if e["type"] == "summarizes"]
    assert len(summary_edges) == 2
