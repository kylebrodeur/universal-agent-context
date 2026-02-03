"""Embedding manager for semantic search and deduplication in UACS.

This module provides the EmbeddingManager class which handles:
- Text embedding using sentence-transformers
- FAISS-based similarity search
- Semantic deduplication detection
- Persistent storage of embeddings and metadata
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from semantic search.

    Attributes:
        id: Identifier of the matched item
        text: Original text of the matched item
        similarity: Cosine similarity score (0-1)
        metadata: Optional metadata associated with the item
    """

    id: str
    text: str
    similarity: float
    metadata: dict[str, Any] | None = None

    def __repr__(self) -> str:
        """String representation of search result."""
        return f"SearchResult(id={self.id!r}, similarity={self.similarity:.3f})"


class EmbeddingManagerError(Exception):
    """Base exception for embedding manager errors."""

    pass


class EmbeddingManager:
    """Manages text embeddings for semantic search and deduplication.

    Uses sentence-transformers for embedding generation and FAISS for
    efficient similarity search. Supports persistent storage of embeddings
    and metadata.

    The manager automatically downloads the embedding model on first use
    and maintains a FAISS index for fast similarity search.

    Example:
        ```python
        from pathlib import Path
        from uacs.embeddings import EmbeddingManager

        # Initialize manager
        manager = EmbeddingManager(Path(".state/embeddings"))

        # Add texts to index
        manager.add_to_index("doc1", "This is a document about cats")
        manager.add_to_index("doc2", "This is a document about dogs")

        # Search for similar texts
        results = manager.search("feline animals", k=5, threshold=0.7)
        for result in results:
            print(f"{result.id}: {result.similarity:.3f}")

        # Check for duplicates
        duplicate_id = manager.check_duplicate("This is about cats")
        if duplicate_id:
            print(f"Duplicate found: {duplicate_id}")

        # Save index to disk
        manager.save_index()
        ```

    Storage structure:
        ```
        storage_path/
        ├── model/              # Auto-downloaded transformer model
        ├── vectors.npy         # Numpy array of embeddings
        ├── index.faiss         # FAISS index file
        └── metadata.json       # ID to text/metadata mapping
        ```
    """

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384

    def __init__(self, storage_path: Path):
        """Initialize the embedding manager.

        Args:
            storage_path: Directory for storing embeddings and model
                         (typically .state/embeddings/)

        Raises:
            EmbeddingManagerError: If initialization fails
        """
        self.storage_path = Path(storage_path)
        self.model_path = self.storage_path / "model"
        self.vectors_path = self.storage_path / "vectors.npy"
        self.index_path = self.storage_path / "index.faiss"
        self.metadata_path = self.storage_path / "metadata.json"

        # Create storage directories
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.model_path.mkdir(parents=True, exist_ok=True)

        # Initialize model (lazy-loaded on first use)
        self._model: Any = None
        self._model_loaded = False

        # Initialize FAISS index
        self._index: Any = None
        self._metadata: dict[str, dict[str, Any]] = {}
        self._id_list: list[str] = []  # Maintain order of IDs in index

        # Try to load existing index
        if self.index_path.exists():
            try:
                self.load_index()
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}")
                self._initialize_empty_index()
        else:
            self._initialize_empty_index()

    def _initialize_empty_index(self) -> None:
        """Initialize an empty FAISS index."""
        try:
            import faiss
        except ImportError as e:
            raise EmbeddingManagerError(
                "faiss-cpu is required for embedding search. "
                "Install it with: pip install faiss-cpu"
            ) from e

        # Use IndexFlatIP for cosine similarity (after L2 normalization)
        self._index = faiss.IndexFlatIP(self.EMBEDDING_DIM)
        self._metadata = {}
        self._id_list = []

    def _load_model(self) -> None:
        """Load the sentence transformer model.

        Downloads the model on first use and caches it in model_path.

        Raises:
            EmbeddingManagerError: If model loading fails
        """
        if self._model_loaded:
            return

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise EmbeddingManagerError(
                "sentence-transformers is required for embeddings. "
                "Install it with: pip install sentence-transformers"
            ) from e

        try:
            logger.info(f"Loading embedding model: {self.MODEL_NAME}")
            # Load model from cache or download
            self._model = SentenceTransformer(
                self.MODEL_NAME, cache_folder=str(self.model_path)
            )
            self._model_loaded = True
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            raise EmbeddingManagerError(f"Failed to load embedding model: {e}") from e

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding vector for text.

        Args:
            text: Input text to embed

        Returns:
            Normalized embedding vector (384 dimensions)

        Raises:
            EmbeddingManagerError: If embedding generation fails
        """
        if not text or not text.strip():
            raise EmbeddingManagerError("Cannot embed empty text")

        # Load model if not already loaded
        if not self._model_loaded:
            self._load_model()

        try:
            # Generate embedding
            embedding = self._model.encode(text, convert_to_numpy=True)

            # Ensure it's a 1D array
            if embedding.ndim > 1:
                embedding = embedding.flatten()

            # L2 normalize for cosine similarity
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            return embedding

        except Exception as e:
            raise EmbeddingManagerError(f"Failed to generate embedding: {e}") from e

    def add_to_index(self, id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a text and its embedding to the index.

        Args:
            id: Unique identifier for the text
            text: Text to embed and index
            metadata: Optional metadata to store with the text

        Raises:
            EmbeddingManagerError: If indexing fails
        """
        if not id:
            raise EmbeddingManagerError("ID cannot be empty")

        if id in self._metadata:
            raise EmbeddingManagerError(f"ID already exists in index: {id}")

        # Generate embedding
        embedding = self.embed(text)

        # Add to FAISS index
        try:
            import faiss
        except ImportError as e:
            raise EmbeddingManagerError(
                "faiss-cpu is required. Install with: pip install faiss-cpu"
            ) from e

        # FAISS expects 2D array (n_samples, n_features)
        embedding_2d = embedding.reshape(1, -1).astype(np.float32)
        self._index.add(embedding_2d)

        # Store metadata
        self._id_list.append(id)
        self._metadata[id] = {
            "text": text,
            "metadata": metadata or {},
        }

        logger.debug(f"Added to index: {id}")

    def search(
        self, query: str, k: int = 10, threshold: float = 0.7
    ) -> list[SearchResult]:
        """Search for similar texts in the index.

        Args:
            query: Query text to search for
            k: Maximum number of results to return
            threshold: Minimum similarity threshold (0-1, default 0.7)

        Returns:
            List of SearchResult objects, sorted by similarity (highest first)

        Raises:
            EmbeddingManagerError: If search fails
        """
        if self._index.ntotal == 0:
            return []  # Empty index

        # Generate query embedding
        query_embedding = self.embed(query)

        # Search FAISS index
        try:
            # FAISS expects 2D array
            query_2d = query_embedding.reshape(1, -1).astype(np.float32)

            # Search for k results
            similarities, indices = self._index.search(query_2d, min(k, self._index.ntotal))

            # Process results
            results = []
            for sim, idx in zip(similarities[0], indices[0]):
                # Skip invalid indices
                if idx < 0 or idx >= len(self._id_list):
                    continue

                # Filter by threshold
                if sim < threshold:
                    continue

                # Get metadata
                id = self._id_list[idx]
                item_data = self._metadata.get(id, {})

                results.append(
                    SearchResult(
                        id=id,
                        text=item_data.get("text", ""),
                        similarity=float(sim),
                        metadata=item_data.get("metadata"),
                    )
                )

            return results

        except Exception as e:
            raise EmbeddingManagerError(f"Search failed: {e}") from e

    def check_duplicate(
        self, text: str, threshold: float = 0.85
    ) -> Optional[str]:
        """Check if text is a duplicate of an existing indexed item.

        Args:
            text: Text to check for duplication
            threshold: Similarity threshold for duplicate detection (default 0.85)

        Returns:
            ID of duplicate item if found, None otherwise

        Raises:
            EmbeddingManagerError: If duplicate check fails
        """
        if self._index.ntotal == 0:
            return None  # Empty index, no duplicates

        # Search for most similar item
        results = self.search(text, k=1, threshold=threshold)

        if results:
            return results[0].id

        return None

    def save_index(self) -> None:
        """Save the FAISS index and metadata to disk.

        Saves three files:
        - index.faiss: FAISS index
        - vectors.npy: Embedding vectors (for backup)
        - metadata.json: ID to text/metadata mapping

        Raises:
            EmbeddingManagerError: If saving fails
        """
        try:
            import faiss
        except ImportError as e:
            raise EmbeddingManagerError(
                "faiss-cpu is required. Install with: pip install faiss-cpu"
            ) from e

        try:
            # Save FAISS index
            faiss.write_index(self._index, str(self.index_path))

            # Save metadata
            metadata_dict = {
                "id_list": self._id_list,
                "metadata": self._metadata,
            }
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata_dict, f, indent=2, ensure_ascii=False)

            # Save vectors as numpy array (for backup/inspection)
            if self._index.ntotal > 0:
                vectors = faiss.rev_swig_ptr(
                    self._index.get_xb(), self._index.ntotal * self.EMBEDDING_DIM
                )
                vectors = np.array(vectors).reshape(self._index.ntotal, self.EMBEDDING_DIM)
                np.save(self.vectors_path, vectors)

            logger.info(
                f"Saved index with {self._index.ntotal} vectors to {self.index_path}"
            )

        except Exception as e:
            raise EmbeddingManagerError(f"Failed to save index: {e}") from e

    def load_index(self) -> None:
        """Load the FAISS index and metadata from disk.

        Raises:
            EmbeddingManagerError: If loading fails
        """
        try:
            import faiss
        except ImportError as e:
            raise EmbeddingManagerError(
                "faiss-cpu is required. Install with: pip install faiss-cpu"
            ) from e

        try:
            # Load FAISS index
            if not self.index_path.exists():
                raise EmbeddingManagerError(f"Index file not found: {self.index_path}")

            self._index = faiss.read_index(str(self.index_path))

            # Load metadata
            if not self.metadata_path.exists():
                raise EmbeddingManagerError(
                    f"Metadata file not found: {self.metadata_path}"
                )

            with open(self.metadata_path, "r", encoding="utf-8") as f:
                metadata_dict = json.load(f)

            self._id_list = metadata_dict.get("id_list", [])
            self._metadata = metadata_dict.get("metadata", {})

            logger.info(
                f"Loaded index with {self._index.ntotal} vectors from {self.index_path}"
            )

            # Validate consistency
            if len(self._id_list) != self._index.ntotal:
                logger.warning(
                    f"Index size mismatch: {len(self._id_list)} IDs vs "
                    f"{self._index.ntotal} vectors"
                )

        except Exception as e:
            raise EmbeddingManagerError(f"Failed to load index: {e}") from e

    def clear_index(self) -> None:
        """Clear all data from the index.

        This removes all embeddings and metadata but keeps the index structure.
        """
        self._initialize_empty_index()
        logger.info("Index cleared")

    def remove_from_index(self, id: str) -> bool:
        """Remove an item from the index.

        Note: FAISS IndexFlatIP doesn't support direct removal, so this
        method rebuilds the entire index without the specified item.

        Args:
            id: ID of item to remove

        Returns:
            True if item was removed, False if not found

        Raises:
            EmbeddingManagerError: If removal fails
        """
        if id not in self._metadata:
            return False

        try:
            # Find index position
            idx = self._id_list.index(id)

            # Save metadata and IDs for remaining items BEFORE rebuilding
            remaining_metadata = {k: v for k, v in self._metadata.items() if k != id}
            remaining_ids = [rid for rid in self._id_list if rid != id]

            # Get all vectors except the one to remove
            import faiss

            if self._index.ntotal > 0:
                all_vectors = faiss.rev_swig_ptr(
                    self._index.get_xb(), self._index.ntotal * self.EMBEDDING_DIM
                )
                all_vectors = np.array(all_vectors).reshape(
                    self._index.ntotal, self.EMBEDDING_DIM
                )

                # Remove the vector at idx
                remaining_vectors = np.delete(all_vectors, idx, axis=0)

                # Rebuild index (this clears metadata/id_list)
                self._initialize_empty_index()

                # Restore remaining data
                self._metadata = remaining_metadata
                self._id_list = remaining_ids

                if len(remaining_vectors) > 0:
                    self._index.add(remaining_vectors.astype(np.float32))

            logger.debug(f"Removed from index: {id}")
            return True

        except Exception as e:
            raise EmbeddingManagerError(f"Failed to remove from index: {e}") from e

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the index.

        Returns:
            Dictionary with index statistics
        """
        return {
            "total_vectors": self._index.ntotal if self._index else 0,
            "dimension": self.EMBEDDING_DIM,
            "model_name": self.MODEL_NAME,
            "model_loaded": self._model_loaded,
            "storage_path": str(self.storage_path),
            "index_size_mb": (
                self.index_path.stat().st_size / (1024 * 1024)
                if self.index_path.exists()
                else 0
            ),
        }

    def __repr__(self) -> str:
        """String representation of embedding manager."""
        return (
            f"EmbeddingManager(model={self.MODEL_NAME}, "
            f"vectors={self._index.ntotal if self._index else 0}, "
            f"path={self.storage_path})"
        )
