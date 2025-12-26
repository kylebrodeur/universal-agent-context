"""SurrealDB-backed memory store for UACS.

This module implements the persistent graph + vector memory system using SurrealDB.
It handles:
- Observations (Nodes)
- Entities (Nodes)
- Relationships (Edges: MENTIONS, FOLLOWS, etc.)
- Vector Search
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional

try:
    from surrealdb import Surreal
    SURREAL_AVAILABLE = True
except ImportError:
    SURREAL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class Observation:
    """Atomic unit of memory."""
    content: str
    type: str  # 'user_input', 'tool_output', 'thought', 'error', 'document'
    agent: str
    embedding: Optional[List[float]] = None
    quality_score: float = 1.0
    branch_id: Optional[str] = None
    thought_number: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Entity:
    """Thing mentioned in observations."""
    name: str
    type: str  # 'file', 'function', 'concept', 'url'
    path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class SurrealMemoryStore:
    """SurrealDB implementation of the memory store."""

    def __init__(self, db_url: str = "memory://", namespace: str = "uacs", database: str = "memory"):
        """Initialize SurrealDB store.
        
        Args:
            db_url: Connection URL (e.g., 'ws://localhost:8000/rpc', 'file://memory.db', 'memory://')
            namespace: SurrealDB namespace
            database: SurrealDB database
        """
        if not SURREAL_AVAILABLE:
            raise ImportError("surrealdb package is not installed. Install with 'pip install surrealdb'")
            
        self.db_url = db_url
        self.namespace = namespace
        self.database = database
        self.db = Surreal(db_url)
        self._connected = False

    async def connect(self):
        """Connect to the database and initialize schema."""
        if self._connected:
            return

        await self.db.connect()
        await self.db.use(self.namespace, self.database)
        await self._init_schema()
        self._connected = True

    async def close(self):
        """Close the database connection."""
        await self.db.close()
        self._connected = False

    async def _init_schema(self):
        """Initialize database schema (tables, indexes)."""
        # Define Observation Table
        await self.db.query("DEFINE TABLE observation SCHEMALESS")
        await self.db.query("DEFINE FIELD timestamp ON observation TYPE datetime")
        await self.db.query("DEFINE INDEX content_search ON observation COLUMNS content SEARCH ANALYZER ascii BM25 HIGHLIGHTS")
        
        # Define Entity Table
        await self.db.query("DEFINE TABLE entity SCHEMALESS")
        await self.db.query("DEFINE INDEX entity_name ON entity COLUMNS name UNIQUE")

        # Define Vector Index (if we had dimensions, we'd set it here)
        # For now, we assume 768 dimensions for standard models
        # await self.db.query("DEFINE INDEX observation_embedding ON observation FIELDS embedding MTREE DIMENSION 768 DIST COSINE")

    async def add_observation(self, observation: Observation) -> str:
        """Add a new observation node."""
        if not self._connected:
            await self.connect()

        data = asdict(observation)
        # Remove None values to let DB handle defaults or optionality
        data = {k: v for k, v in data.items() if v is not None}
        
        # Create record
        result = await self.db.create("observation", data)
        return result[0]["id"]

    async def add_entity(self, entity: Entity) -> str:
        """Add or get an entity node."""
        if not self._connected:
            await self.connect()

        data = asdict(entity)
        data = {k: v for k, v in data.items() if v is not None}

        # Upsert based on name (using a query since create might fail on unique constraint)
        # Using a transaction-like approach or just a merge
        # For simplicity in this phase, we try to select first
        existing = await self.db.query(f"SELECT * FROM entity WHERE name = '{entity.name}'")
        if existing and existing[0]['result']:
            return existing[0]['result'][0]['id']
        
        result = await self.db.create("entity", data)
        return result[0]["id"]

    async def add_mentions(self, observation_id: str, entity_id: str):
        """Create MENTIONS edge: observation -> entity."""
        if not self._connected:
            await self.connect()
            
        await self.db.query(f"RELATE {observation_id}->MENTIONS->{entity_id}")

    async def add_follows(self, from_obs_id: str, to_obs_id: str, type: str = "next", reason: str = None):
        """Create FOLLOWS edge: from_obs -> to_obs.
        
        Note: In our design, 'FOLLOWS' usually points backwards in time (New -> Old) 
        or forwards (Old -> New)? 
        The design doc says: `observation:124 -> FOLLOWS -> observation:123` (New follows Old).
        So `from_obs_id` is the NEW one, `to_obs_id` is the OLD one.
        """
        if not self._connected:
            await self.connect()
            
        content = {"type": type}
        if reason:
            content["reason"] = reason
            
        await self.db.query(f"RELATE {from_obs_id}->FOLLOWS->{to_obs_id} CONTENT {json.dumps(content)}")

    async def search(self, query_embedding: List[float], limit: int = 5) -> List[dict]:
        """Search observations by vector similarity."""
        if not self._connected:
            await self.connect()

        # This requires the vector index to be defined and working
        # For Phase 1, we might just return recent observations if no embedding provided
        if not query_embedding:
            result = await self.db.query(f"SELECT * FROM observation ORDER BY timestamp DESC LIMIT {limit}")
            return result[0]['result']

        # Vector search query
        # Note: Syntax depends on SurrealDB version and index definition
        q = f"""
        SELECT *, vector::similarity::cosine(embedding, $query_embedding) AS score
        FROM observation
        WHERE embedding <|0.7|> $query_embedding
        ORDER BY score DESC LIMIT {limit};
        """
        result = await self.db.query(q, {"query_embedding": query_embedding})
        return result[0]['result']

    async def get_recent_observations(self, limit: int = 10) -> List[dict]:
        """Get most recent observations."""
        if not self._connected:
            await self.connect()
            
        result = await self.db.query(f"SELECT * FROM observation ORDER BY timestamp DESC LIMIT {limit}")
        return result[0]['result']
