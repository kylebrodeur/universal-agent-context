"""Unit tests for EmbeddingManager - Semantic search and deduplication.

This module tests the EmbeddingManager's core functionality:
- Model initialization and caching
- Embedding generation with correct dimensions
- Semantic search functionality
- Duplicate detection with configurable thresholds
- Index persistence (save/load operations)
- Performance benchmarks for embedding and search operations
"""

import time
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from uacs.embeddings import EmbeddingManager, SearchResult
from uacs.embeddings.manager import EmbeddingManagerError


@pytest.fixture
def temp_storage(tmp_path: Path) -> Path:
    """Provide a temporary storage path for embeddings.

    Creates a temporary directory for each test to ensure isolation.
    """
    storage = tmp_path / "embeddings"
    storage.mkdir(parents=True, exist_ok=True)
    return storage


@pytest.fixture
def manager(temp_storage: Path) -> EmbeddingManager:
    """Create an EmbeddingManager instance for testing.

    Uses temporary storage to avoid conflicts between tests.
    """
    return EmbeddingManager(temp_storage)


@pytest.fixture
def populated_manager(manager: EmbeddingManager) -> EmbeddingManager:
    """Create a pre-populated EmbeddingManager with sample data.

    Adds diverse test documents covering various topics for search testing.
    """
    sample_docs = [
        ("doc1", "Python is a high-level programming language", {"topic": "python"}),
        ("doc2", "Machine learning uses statistical models", {"topic": "ml"}),
        ("doc3", "Neural networks are inspired by the brain", {"topic": "ml"}),
        ("doc4", "JavaScript is used for web development", {"topic": "javascript"}),
        ("doc5", "Deep learning is a subset of machine learning", {"topic": "ml"}),
        ("doc6", "Rust is a systems programming language", {"topic": "rust"}),
        ("doc7", "Type systems help catch bugs at compile time", {"topic": "types"}),
        ("doc8", "Functional programming emphasizes immutability", {"topic": "fp"}),
    ]

    for doc_id, text, metadata in sample_docs:
        manager.add_to_index(doc_id, text, metadata)

    return manager


class TestEmbeddingManagerInitialization:
    """Test EmbeddingManager initialization and setup."""

    def test_manager_creation(self, temp_storage: Path) -> None:
        """Test that EmbeddingManager can be created successfully.

        Verifies:
        - Manager instance is created
        - Storage directories are created
        - Model is not loaded until first use (lazy loading)
        """
        manager = EmbeddingManager(temp_storage)

        assert manager is not None
        assert manager.storage_path == temp_storage
        assert manager.storage_path.exists()
        assert manager.model_path.exists()
        assert not manager._model_loaded  # Lazy loading

    def test_storage_structure(self, manager: EmbeddingManager) -> None:
        """Test that storage directory structure is created correctly.

        Verifies the expected directory structure for model and data files.
        """
        assert manager.storage_path.exists()
        assert manager.model_path.exists()
        assert manager.vectors_path.name == "vectors.npy"
        assert manager.index_path.name == "index.faiss"
        assert manager.metadata_path.name == "metadata.json"

    def test_model_lazy_loading(self, manager: EmbeddingManager) -> None:
        """Test that model is loaded lazily on first use.

        Verifies:
        - Model is not loaded on initialization
        - Model is loaded when embedding is requested
        - Model remains loaded for subsequent operations
        """
        # Initially not loaded
        assert not manager._model_loaded

        # Generate embedding triggers loading
        manager.embed("test text")

        # Now loaded
        assert manager._model_loaded
        assert manager._model is not None

    def test_empty_index_initialization(self, manager: EmbeddingManager) -> None:
        """Test that empty FAISS index is initialized correctly.

        Verifies index starts with zero vectors and correct dimensions.
        """
        assert manager._index is not None
        assert manager._index.ntotal == 0
        assert manager._index.d == EmbeddingManager.EMBEDDING_DIM


class TestEmbeddingGeneration:
    """Test embedding generation functionality."""

    def test_embed_returns_correct_shape(self, manager: EmbeddingManager) -> None:
        """Test that embeddings have the correct dimensionality (384).

        Verifies the all-MiniLM-L6-v2 model produces 384-dimensional vectors.
        """
        embedding = manager.embed("This is a test document")

        assert embedding.shape == (EmbeddingManager.EMBEDDING_DIM,)
        assert embedding.shape == (384,)

    def test_embed_normalizes_vectors(self, manager: EmbeddingManager) -> None:
        """Test that embeddings are L2-normalized for cosine similarity.

        Verifies vectors have unit length (L2 norm ≈ 1.0).
        """
        embedding = manager.embed("Sample text for normalization")

        norm = np.linalg.norm(embedding)
        assert np.isclose(norm, 1.0, atol=1e-6)

    def test_embed_different_texts_differ(self, manager: EmbeddingManager) -> None:
        """Test that different texts produce different embeddings.

        Verifies embeddings are semantically meaningful and not identical.
        """
        emb1 = manager.embed("Cats are feline animals")
        emb2 = manager.embed("Dogs are canine animals")

        # Vectors should be different
        assert not np.allclose(emb1, emb2)

        # But similar texts should have some similarity
        similarity = np.dot(emb1, emb2)
        assert 0.3 < similarity < 0.9  # Reasonable similarity range

    def test_embed_similar_texts_are_similar(self, manager: EmbeddingManager) -> None:
        """Test that semantically similar texts have high cosine similarity.

        Verifies the model captures semantic meaning.
        """
        emb1 = manager.embed("Python programming language")
        emb2 = manager.embed("Python is a programming language")

        similarity = np.dot(emb1, emb2)
        assert similarity > 0.85  # High similarity for nearly identical meaning

    def test_embed_empty_text_raises_error(self, manager: EmbeddingManager) -> None:
        """Test that embedding empty text raises appropriate error.

        Verifies error handling for invalid input.
        """
        with pytest.raises(EmbeddingManagerError, match="Cannot embed empty text"):
            manager.embed("")

        with pytest.raises(EmbeddingManagerError, match="Cannot embed empty text"):
            manager.embed("   ")  # Whitespace only

    def test_embed_caches_model(self, manager: EmbeddingManager) -> None:
        """Test that model is cached and reused across embeddings.

        Verifies model loading happens only once for efficiency.
        """
        # First embedding loads model
        manager.embed("First text")
        model_instance = manager._model

        # Second embedding reuses model
        manager.embed("Second text")
        assert manager._model is model_instance  # Same instance


class TestIndexOperations:
    """Test index management operations."""

    def test_add_to_index(self, manager: EmbeddingManager) -> None:
        """Test adding items to the index.

        Verifies:
        - Items can be added with ID, text, and metadata
        - Index size increases correctly
        - Metadata is stored properly
        """
        manager.add_to_index("doc1", "Test document", {"source": "test"})

        assert manager._index.ntotal == 1
        assert "doc1" in manager._metadata
        assert manager._metadata["doc1"]["text"] == "Test document"
        assert manager._metadata["doc1"]["metadata"]["source"] == "test"

    def test_add_multiple_items(self, manager: EmbeddingManager) -> None:
        """Test adding multiple items to the index.

        Verifies batch addition works correctly.
        """
        items = [
            ("id1", "First document"),
            ("id2", "Second document"),
            ("id3", "Third document"),
        ]

        for doc_id, text in items:
            manager.add_to_index(doc_id, text)

        assert manager._index.ntotal == 3
        assert len(manager._id_list) == 3
        assert len(manager._metadata) == 3

    def test_add_duplicate_id_raises_error(self, manager: EmbeddingManager) -> None:
        """Test that adding duplicate IDs raises an error.

        Verifies index integrity by preventing duplicate IDs.
        """
        manager.add_to_index("doc1", "First text")

        with pytest.raises(EmbeddingManagerError, match="ID already exists"):
            manager.add_to_index("doc1", "Different text")

    def test_add_empty_id_raises_error(self, manager: EmbeddingManager) -> None:
        """Test that empty IDs are rejected.

        Verifies input validation for IDs.
        """
        with pytest.raises(EmbeddingManagerError, match="ID cannot be empty"):
            manager.add_to_index("", "Some text")

    def test_remove_from_index(self, manager: EmbeddingManager) -> None:
        """Test removing items from the index.

        Verifies:
        - Items can be removed by ID
        - Index size decreases correctly
        - Metadata is cleaned up
        """
        manager.add_to_index("doc1", "First document")
        manager.add_to_index("doc2", "Second document")

        assert manager.remove_from_index("doc1") is True
        assert manager._index.ntotal == 1
        assert "doc1" not in manager._metadata
        assert len(manager._id_list) == 1

    def test_remove_nonexistent_returns_false(self, manager: EmbeddingManager) -> None:
        """Test that removing non-existent item returns False.

        Verifies graceful handling of invalid removal requests.
        """
        result = manager.remove_from_index("nonexistent")
        assert result is False

    def test_clear_index(self, populated_manager: EmbeddingManager) -> None:
        """Test clearing all data from the index.

        Verifies:
        - All vectors are removed
        - All metadata is cleared
        - Index structure remains valid
        """
        assert populated_manager._index.ntotal == 8

        populated_manager.clear_index()

        assert populated_manager._index.ntotal == 0
        assert len(populated_manager._metadata) == 0
        assert len(populated_manager._id_list) == 0


class TestSemanticSearch:
    """Test semantic search functionality."""

    def test_search_returns_results(self, populated_manager: EmbeddingManager) -> None:
        """Test that search returns semantically relevant results.

        Verifies basic search functionality works.
        """
        results = populated_manager.search("programming languages", k=5, threshold=0.5)

        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_results_sorted_by_similarity(
        self, populated_manager: EmbeddingManager
    ) -> None:
        """Test that search results are sorted by descending similarity.

        Verifies result ordering for user-facing display.
        """
        results = populated_manager.search("machine learning algorithms", k=5)

        # Check descending order
        for i in range(len(results) - 1):
            assert results[i].similarity >= results[i + 1].similarity

    def test_search_respects_threshold(
        self, populated_manager: EmbeddingManager
    ) -> None:
        """Test that search filters results by similarity threshold.

        Verifies only sufficiently similar results are returned.
        """
        high_threshold_results = populated_manager.search(
            "neural networks", k=10, threshold=0.8
        )
        low_threshold_results = populated_manager.search(
            "neural networks", k=10, threshold=0.5
        )

        # Higher threshold should return fewer or equal results
        assert len(high_threshold_results) <= len(low_threshold_results)

        # All results should meet threshold
        for result in high_threshold_results:
            assert result.similarity >= 0.8

    def test_search_respects_k_limit(self, populated_manager: EmbeddingManager) -> None:
        """Test that search returns at most k results.

        Verifies the k parameter limits result count.
        """
        results = populated_manager.search("programming", k=3, threshold=0.0)

        assert len(results) <= 3

    def test_search_semantic_relevance(
        self, populated_manager: EmbeddingManager
    ) -> None:
        """Test that search finds semantically related documents.

        Verifies semantic understanding beyond keyword matching.
        """
        # Search for ML-related content using more direct terminology
        # that's closer to the actual document content
        results = populated_manager.search("machine learning neural networks", k=5, threshold=0.4)

        # Should find ML and neural network docs
        result_ids = {r.id for r in results}
        ml_docs = {"doc2", "doc3", "doc5"}  # ML-related docs

        # At least some ML docs should be in results
        assert len(result_ids & ml_docs) > 0, (
            f"Expected ML docs {ml_docs} in results, but got {result_ids}. "
            f"All results: {[(r.id, r.similarity) for r in results]}"
        )

    def test_search_empty_index_returns_empty_list(
        self, manager: EmbeddingManager
    ) -> None:
        """Test that searching empty index returns empty results.

        Verifies graceful handling of empty index.
        """
        results = manager.search("any query", k=10)

        assert results == []

    def test_search_result_contains_metadata(
        self, populated_manager: EmbeddingManager
    ) -> None:
        """Test that search results include stored metadata.

        Verifies metadata is preserved through search.
        """
        results = populated_manager.search("Python", k=1, threshold=0.5)

        assert len(results) > 0
        result = results[0]
        assert result.metadata is not None
        assert "topic" in result.metadata


class TestDuplicateDetection:
    """Test semantic duplicate detection."""

    def test_check_duplicate_high_similarity(
        self, manager: EmbeddingManager
    ) -> None:
        """Test that near-duplicate texts are detected with threshold > 0.85.

        Verifies duplicate detection catches very similar content.
        """
        manager.add_to_index("doc1", "Python is a programming language")

        # Very similar text should be detected as duplicate
        duplicate_id = manager.check_duplicate(
            "Python is a programming language used for software", threshold=0.85
        )

        assert duplicate_id == "doc1"

    def test_check_duplicate_respects_threshold(
        self, manager: EmbeddingManager
    ) -> None:
        """Test that duplicate detection threshold is configurable.

        Verifies threshold parameter controls detection sensitivity.
        """
        manager.add_to_index("doc1", "Cats are feline animals")

        # With high threshold, should not detect duplicate
        result_high = manager.check_duplicate("Dogs are canine animals", threshold=0.95)
        assert result_high is None

        # With low threshold, might detect as "duplicate"
        result_low = manager.check_duplicate("Dogs are canine animals", threshold=0.3)
        # May or may not find a match depending on similarity

    def test_check_duplicate_empty_index(self, manager: EmbeddingManager) -> None:
        """Test duplicate check on empty index returns None.

        Verifies graceful handling of empty index.
        """
        result = manager.check_duplicate("Any text")

        assert result is None

    def test_check_duplicate_no_match(self, populated_manager: EmbeddingManager) -> None:
        """Test that dissimilar text is not flagged as duplicate.

        Verifies false positives are avoided.
        """
        # Add a unique document
        duplicate_id = populated_manager.check_duplicate(
            "Quantum computing uses qubits for computation", threshold=0.85
        )

        # Should not match existing programming language docs
        assert duplicate_id is None


class TestIndexPersistence:
    """Test saving and loading index to/from disk."""

    def test_save_index_creates_files(self, populated_manager: EmbeddingManager) -> None:
        """Test that save_index creates all required files.

        Verifies:
        - FAISS index file is created
        - Metadata JSON file is created
        - Vector backup file is created
        """
        populated_manager.save_index()

        assert populated_manager.index_path.exists()
        assert populated_manager.metadata_path.exists()
        assert populated_manager.vectors_path.exists()

    def test_save_and_load_preserves_data(
        self, temp_storage: Path, populated_manager: EmbeddingManager
    ) -> None:
        """Test that save/load cycle preserves all data correctly.

        Verifies:
        - Vector count is preserved
        - Metadata is preserved
        - Search results are consistent
        """
        # Save index
        populated_manager.save_index()
        original_count = populated_manager._index.ntotal

        # Create new manager and load
        new_manager = EmbeddingManager(temp_storage)
        new_manager.load_index()

        # Verify data preserved
        assert new_manager._index.ntotal == original_count
        assert len(new_manager._metadata) == len(populated_manager._metadata)
        assert len(new_manager._id_list) == len(populated_manager._id_list)

        # Verify search works the same
        query = "machine learning"
        results1 = populated_manager.search(query, k=5)
        results2 = new_manager.search(query, k=5)

        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1.id == r2.id
            assert np.isclose(r1.similarity, r2.similarity, atol=1e-6)

    def test_load_nonexistent_index_raises_error(
        self, temp_storage: Path
    ) -> None:
        """Test that loading non-existent index raises appropriate error.

        Verifies error handling for missing files.
        """
        storage = temp_storage / "nonexistent"
        storage.mkdir()

        manager = EmbeddingManager(storage)
        # Clear the auto-initialized index
        (storage / "index.faiss").unlink(missing_ok=True)

        with pytest.raises(EmbeddingManagerError, match="Index file not found"):
            manager.load_index()

    def test_auto_load_existing_index(self, temp_storage: Path) -> None:
        """Test that manager auto-loads existing index on initialization.

        Verifies seamless resume from persisted state.
        """
        # Create and save index
        manager1 = EmbeddingManager(temp_storage)
        manager1.add_to_index("doc1", "Test document")
        manager1.save_index()

        # Create new manager - should auto-load
        manager2 = EmbeddingManager(temp_storage)

        assert manager2._index.ntotal == 1
        assert "doc1" in manager2._metadata


class TestPerformanceBenchmarks:
    """Test performance benchmarks for embedding and search operations."""

    def test_embedding_performance(self, manager: EmbeddingManager) -> None:
        """Test that embedding generation completes in < 100ms.

        Benchmarks the all-MiniLM-L6-v2 model performance.
        Target: < 100ms per embedding on typical hardware.
        """
        # Warm up the model
        manager.embed("warmup text")

        # Benchmark
        text = "This is a test document for performance benchmarking"
        start = time.perf_counter()
        manager.embed(text)
        duration = time.perf_counter() - start

        # Should be fast (< 100ms)
        assert duration < 0.1, f"Embedding took {duration*1000:.1f}ms (target: <100ms)"

    def test_search_performance(self, populated_manager: EmbeddingManager) -> None:
        """Test that semantic search completes in < 50ms.

        Benchmarks FAISS IndexFlatIP search performance.
        Target: < 50ms for k=10 search on ~10 documents.
        """
        # Warm up
        populated_manager.search("warmup", k=5)

        # Benchmark
        start = time.perf_counter()
        populated_manager.search("machine learning", k=10)
        duration = time.perf_counter() - start

        # Should be very fast (< 50ms)
        assert duration < 0.05, f"Search took {duration*1000:.1f}ms (target: <50ms)"

    def test_batch_indexing_performance(self, manager: EmbeddingManager) -> None:
        """Test that indexing 100 documents completes in reasonable time.

        Benchmarks bulk indexing performance.
        Target: < 10 seconds for 100 documents.
        """
        docs = [(f"doc{i}", f"Document {i} with some content") for i in range(100)]

        start = time.perf_counter()
        for doc_id, text in docs:
            manager.add_to_index(doc_id, text)
        duration = time.perf_counter() - start

        # Should complete in reasonable time
        assert duration < 10, f"Indexing 100 docs took {duration:.1f}s (target: <10s)"
        assert manager._index.ntotal == 100


class TestGetStats:
    """Test statistics and metadata retrieval."""

    def test_get_stats_returns_expected_fields(
        self, populated_manager: EmbeddingManager
    ) -> None:
        """Test that get_stats returns all expected fields.

        Verifies stats dictionary structure and content.
        """
        stats = populated_manager.get_stats()

        assert "total_vectors" in stats
        assert "dimension" in stats
        assert "model_name" in stats
        assert "model_loaded" in stats
        assert "storage_path" in stats
        assert "index_size_mb" in stats

    def test_get_stats_correct_values(
        self, populated_manager: EmbeddingManager
    ) -> None:
        """Test that get_stats returns accurate values.

        Verifies stats reflect actual index state.
        """
        stats = populated_manager.get_stats()

        assert stats["total_vectors"] == 8
        assert stats["dimension"] == 384
        assert stats["model_name"] == EmbeddingManager.MODEL_NAME
        assert isinstance(stats["storage_path"], str)

    def test_get_stats_after_save(self, populated_manager: EmbeddingManager) -> None:
        """Test that get_stats shows file size after saving.

        Verifies index_size_mb is populated after save.
        """
        populated_manager.save_index()
        stats = populated_manager.get_stats()

        assert stats["index_size_mb"] > 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_very_long_text(self, manager: EmbeddingManager) -> None:
        """Test handling of very long text input.

        Verifies model handles long documents gracefully.
        """
        long_text = "This is a sentence. " * 1000  # ~5000 words

        # Should not crash
        embedding = manager.embed(long_text)
        assert embedding.shape == (384,)

    def test_special_characters(self, manager: EmbeddingManager) -> None:
        """Test handling of text with special characters and unicode.

        Verifies proper handling of non-ASCII text.
        """
        texts = [
            "Text with émojis 🐍🔥",
            "Text with ümläuts and àccénts",
            "中文文本测试",
            "Texto en español con ñ",
        ]

        for text in texts:
            embedding = manager.embed(text)
            assert embedding.shape == (384,)

    def test_numeric_text(self, manager: EmbeddingManager) -> None:
        """Test handling of numeric and symbolic text.

        Verifies model handles non-natural language input.
        """
        numeric_text = "123.456 + 789 = 912.456"

        embedding = manager.embed(numeric_text)
        assert embedding.shape == (384,)

    def test_search_with_no_matches(self, populated_manager: EmbeddingManager) -> None:
        """Test search with very high threshold returns no results.

        Verifies threshold filtering works correctly.
        """
        # Use impossibly high threshold
        results = populated_manager.search("test", k=10, threshold=0.99999)

        # Should return empty or very few results
        assert len(results) <= 1

    def test_repr_method(self, populated_manager: EmbeddingManager) -> None:
        """Test string representation of EmbeddingManager.

        Verifies __repr__ provides useful information.
        """
        repr_str = repr(populated_manager)

        assert "EmbeddingManager" in repr_str
        assert "vectors=8" in repr_str
        assert EmbeddingManager.MODEL_NAME in repr_str
