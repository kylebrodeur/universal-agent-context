# SurrealDB Memory System Design

## Overview

This document outlines the architecture for upgrading the Universal Agent Context System (UACS) from simple JSON-based storage to a dynamic, multi-model memory system using **SurrealDB**.

This transition enables:
1.  **Graph Relationships:** Native modeling of how observations relate to files, concepts, and other observations.
2.  **Vector Search:** Semantic recall of past events ("What did we do about the auth bug?").
3.  **Reasoning Graphs:** Supporting non-linear thinking (branching, revisions) inspired by the `sequential-thinking` MCP.
4.  **Structured Observations:** Moving from raw text logs to typed events.
5.  **Embedded Deployment:** Running locally within the CLI without external server dependencies.

## Architecture

### Storage Engine
We will use **SurrealDB** in **Embedded Mode** (or local file mode via `surreal start file://...` managed by the CLI). This ensures zero-config setup for users.

### Data Model

The memory system will consist of **Nodes** (Vertices) and **Relationships** (Edges).

#### Nodes (Tables)

1.  **`observation`**
    *   The atomic unit of memory.
    *   **Fields:**
        *   `content`: string (The text content)
        *   `type`: string (e.g., 'user_input', 'tool_output', 'thought', 'error')
        *   `agent`: string (e.g., 'gemini', 'claude')
        *   `timestamp`: datetime
        *   `embedding`: vector<float> (768-dim embedding of content)
        *   `branch_id`: string (optional, for grouping reasoning branches)
        *   `thought_number`: int (optional, for sequential ordering within a branch)
    *   **Indexes:**
        *   `HNSW` index on `embedding` for semantic search.
        *   Full-text index on `content`.

2.  **`entity`**
    *   Things mentioned in observations.
    *   **Fields:**
        *   `name`: string
        *   `type`: string (e.g., 'file', 'function', 'concept', 'url')
        *   `path`: string (optional, for files)

3.  **`session`**
    *   A container for a sequence of observations.
    *   **Fields:**
        *   `goal`: string
        *   `start_time`: datetime
        *   `status`: string
        *   `plan_status`: string (e.g., 'in_progress', 'blocked', 'completed')

#### Edges (Relationships)

1.  **`MENTIONS`** (`observation -> entity`)
    *   Captures what an observation is about.
    *   Example: `observation:123 -> MENTIONS -> entity:file_main_py`

2.  **`FOLLOWS`** (`observation -> observation`)
    *   Maintains the chain of thought, supporting non-linear reasoning.
    *   **Fields:**
        *   `type`: string
            *   `'next'`: Standard linear flow.
            *   `'branch'`: Alternative path (forking).
            *   `'revision'`: Correction of a previous thought.
        *   `reason`: string (optional, why the branch/revision occurred)
    *   Example: `observation:124 -> FOLLOWS { type: 'revision' } -> observation:123`

3.  **`BELONGS_TO`** (`observation -> session`)
    *   Groups observations into sessions.

4.  **`SIMILAR_TO`** (`observation -> observation`)
    *   (Optional) Explicit links between semantically similar nodes, or computed dynamically via vector search.

## Core Capabilities

### 1. Semantic Search (Recall)
Agents can query memory using natural language.
*   **Query:** "How did we fix the login bug?"
*   **SurrealQL:**
    ```sql
    SELECT *, vector::similarity::cosine(embedding, $query_embedding) AS score
    FROM observation
    WHERE embedding <|0.7|> $query_embedding
    ORDER BY score DESC LIMIT 5;
    ```

### 2. Graph Traversal (Context Expansion)
Agents can explore related context.
*   **Query:** "Show me everything related to `src/auth.py`."
*   **SurrealQL:**
    ```sql
    SELECT <-MENTIONS<-observation.* FROM entity WHERE name = 'src/auth.py';
    ```

### 3. Reasoning Graph Navigation
Agents can navigate complex thought processes, including backtracks and revisions.
*   **Query:** "Show me the alternative approach we considered."
*   **SurrealQL:**
    ```sql
    SELECT * FROM observation
    WHERE ->FOLLOWS[WHERE type = 'branch'].out
    ```

## Comparison with MCPs

| Feature | 'memory' MCP | 'sequential-thinking' MCP | **UACS SurrealDB Design** |
| :--- | :--- | :--- | :--- |
| **Structure** | Entity-Centric | Sequence-Centric | **Hybrid (Graph)** |
| **Storage** | In-Memory / SQLite | In-Memory | **SurrealDB (Disk/Embedded)** |
| **Reasoning** | None | Branching / Revision | **Native Graph Edges** |
| **Search** | Keyword | None | **Vector + Graph + Keyword** |

**Adoption Strategy:**
*   We adopt the **Branching/Revision** logic from `sequential-thinking` by adding typed `FOLLOWS` edges.
*   We improve on `memory` MCP by making **Observations** first-class nodes, allowing them to link to multiple entities without duplication.

## Implementation Plan

### Phase 1: The `SurrealMemoryStore`
Create a new class in `uacs.memory` that implements the storage interface but talks to SurrealDB.

```python
class SurrealMemoryStore:
    def __init__(self, db_path: str):
        self.db = Surreal(f"file://{db_path}")

    async def add_observation(self, content: str, agent: str, embedding: list[float]):
        # INSERT INTO observation ...
        pass

    async def search(self, query_embedding: list[float], limit: int = 5):
        # Vector search query
        pass
```

### Phase 2: Embedding Integration
Integrate a lightweight embedding model (e.g., `all-MiniLM-L6-v2` via `sentence-transformers` or `fastembed`) into UACS to generate vectors for observations.

### Phase 3: Graph Extraction
Implement a simple heuristic or LLM-based extractor to identify entities (files, functions) in observations and create `MENTIONS` edges automatically.

### Phase 4: Agent Tools
Expose new tools to the agents:
*   `recall_memory(query: str)`
*   `explore_connections(entity_name: str)`
*   `navigate_reasoning(start_observation_id: str)`dexed) |
| **Querying** | Python filtering | SurrealQL (Rich query language) |
