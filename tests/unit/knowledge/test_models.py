"""Unit tests for Knowledge Layer Pydantic models.

This module tests the Pydantic models used in UACS v0.3.0 Semantic Knowledge Layer:
- Convention: Project conventions and patterns
- Decision: Architectural decisions
- Learning: Cross-session learnings
- Artifact: Code artifacts
- SearchResult: Semantic search results

Tests cover:
- Model validation
- Required vs optional fields
- Confidence score constraints (0.0-1.0)
- JSON serialization/deserialization
- Datetime handling
- Field validators
"""

from datetime import datetime, timezone
from typing import Any, Dict

import pytest
from pydantic import ValidationError

from uacs.knowledge.models import (
    Artifact,
    Convention,
    Decision,
    Learning,
    SearchResult,
)


@pytest.fixture
def sample_convention_data() -> Dict[str, Any]:
    """Provide sample data for Convention model testing.

    Returns minimal valid data that can be extended in individual tests.
    """
    return {
        "content": "Use type hints for all function signatures",
        "topics": ["typing", "code-quality"],
        "source_session": "session_2024_01_15",
        "confidence": 0.95,
    }


@pytest.fixture
def sample_decision_data() -> Dict[str, Any]:
    """Provide sample data for Decision model testing.

    Returns minimal valid data that can be extended in individual tests.
    """
    return {
        "question": "Which database should we use for the project?",
        "decision": "Use PostgreSQL for relational data",
        "rationale": "Better support for complex queries and ACID compliance",
        "alternatives": ["MongoDB", "MySQL", "SQLite"],
        "decided_by": "claude-opus-4-5-20251101",
        "session_id": "session_2024_01_15",
        "topics": ["database", "architecture"],
    }


@pytest.fixture
def sample_learning_data() -> Dict[str, Any]:
    """Provide sample data for Learning model testing.

    Returns minimal valid data that can be extended in individual tests.
    """
    return {
        "pattern": "Fast iteration cycles improve code quality",
        "confidence": 0.88,
        "learned_from": ["session_2024_01_10", "session_2024_01_12"],
        "category": "development-process",
    }


@pytest.fixture
def sample_artifact_data() -> Dict[str, Any]:
    """Provide sample data for Artifact model testing.

    Returns minimal valid data that can be extended in individual tests.
    """
    return {
        "type": "class",
        "path": "src/uacs/knowledge/models.py::Convention",
        "description": "Pydantic model for project conventions",
        "created_in_session": "session_2024_01_15",
        "topics": ["knowledge", "data-models"],
    }


@pytest.fixture
def sample_search_result_data() -> Dict[str, Any]:
    """Provide sample data for SearchResult model testing.

    Returns minimal valid data that can be extended in individual tests.
    """
    return {
        "type": "convention",
        "content": "Use Pydantic models for data validation",
        "relevance_score": 0.92,
        "source_session": "session_2024_01_15",
        "metadata": {"topics": ["validation"], "confidence": 0.95},
    }


class TestConventionModel:
    """Test the Convention Pydantic model."""

    def test_convention_creation_minimal(self) -> None:
        """Test creating Convention with only required field (content).

        Verifies:
        - Model accepts minimal valid data
        - Optional fields get default values
        - created_at is auto-populated
        """
        convention = Convention(content="Use descriptive variable names")

        assert convention.content == "Use descriptive variable names"
        assert convention.topics == []
        assert convention.source_session is None
        assert convention.confidence == 1.0
        assert isinstance(convention.created_at, datetime)
        assert convention.last_verified is None

    def test_convention_creation_full(self, sample_convention_data: Dict[str, Any]) -> None:
        """Test creating Convention with all fields populated.

        Verifies all fields can be set and are stored correctly.
        """
        now = datetime.now(timezone.utc)
        sample_convention_data["created_at"] = now
        sample_convention_data["last_verified"] = now

        convention = Convention(**sample_convention_data)

        assert convention.content == sample_convention_data["content"]
        assert convention.topics == sample_convention_data["topics"]
        assert convention.source_session == sample_convention_data["source_session"]
        assert convention.confidence == sample_convention_data["confidence"]
        assert convention.created_at == now
        assert convention.last_verified == now

    def test_convention_empty_content_raises_error(self) -> None:
        """Test that empty content string raises validation error.

        Verifies min_length=1 constraint is enforced.
        """
        with pytest.raises(ValidationError) as exc_info:
            Convention(content="")

        errors = exc_info.value.errors()
        assert any(
            e["loc"] == ("content",) and e["type"] == "string_too_short"
            for e in errors
        )

    def test_convention_confidence_bounds(self) -> None:
        """Test that confidence score is constrained to [0.0, 1.0].

        Verifies ge=0.0 and le=1.0 constraints are enforced.
        """
        # Valid bounds
        Convention(content="Test", confidence=0.0)
        Convention(content="Test", confidence=1.0)
        Convention(content="Test", confidence=0.5)

        # Below lower bound
        with pytest.raises(ValidationError) as exc_info:
            Convention(content="Test", confidence=-0.1)
        assert any(
            e["loc"] == ("confidence",) and "greater_than_equal" in e["type"]
            for e in exc_info.value.errors()
        )

        # Above upper bound
        with pytest.raises(ValidationError) as exc_info:
            Convention(content="Test", confidence=1.1)
        assert any(
            e["loc"] == ("confidence",) and "less_than_equal" in e["type"]
            for e in exc_info.value.errors()
        )

    def test_convention_json_serialization(self, sample_convention_data: Dict[str, Any]) -> None:
        """Test JSON serialization and deserialization.

        Verifies:
        - model_dump() produces JSON-serializable dict
        - model_dump_json() produces JSON string
        - Round-trip serialization preserves data
        """
        convention = Convention(**sample_convention_data)

        # Serialize to dict
        data_dict = convention.model_dump()
        assert isinstance(data_dict, dict)
        assert data_dict["content"] == sample_convention_data["content"]

        # Serialize to JSON string
        json_str = convention.model_dump_json()
        assert isinstance(json_str, str)
        assert sample_convention_data["content"] in json_str

        # Round-trip
        convention2 = Convention.model_validate_json(json_str)
        assert convention2.content == convention.content
        assert convention2.confidence == convention.confidence

    def test_convention_datetime_handling(self) -> None:
        """Test datetime field handling and serialization.

        Verifies:
        - created_at uses datetime.utcnow as default factory
        - Datetimes can be passed explicitly
        - Datetimes are serialized correctly to ISO format
        """
        convention = Convention(content="Test convention")

        # Auto-generated datetime
        assert isinstance(convention.created_at, datetime)

        # Explicit datetime
        custom_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        convention2 = Convention(content="Test", created_at=custom_time)
        assert convention2.created_at == custom_time

        # JSON serialization includes ISO format
        json_dict = convention2.model_dump(mode="json")
        assert isinstance(json_dict["created_at"], str)


class TestDecisionModel:
    """Test the Decision Pydantic model."""

    def test_decision_creation_minimal(self) -> None:
        """Test creating Decision with only required fields.

        Verifies:
        - All required fields must be provided
        - Optional fields get default values
        - decided_at is auto-populated
        """
        decision = Decision(
            question="What framework to use?",
            decision="Use FastAPI",
            rationale="Modern and well-documented",
            decided_by="claude-opus-4-5-20251101",
            session_id="session_123",
        )

        assert decision.question == "What framework to use?"
        assert decision.decision == "Use FastAPI"
        assert decision.rationale == "Modern and well-documented"
        assert decision.alternatives == []
        assert decision.topics == []
        assert isinstance(decision.decided_at, datetime)

    def test_decision_creation_full(self, sample_decision_data: Dict[str, Any]) -> None:
        """Test creating Decision with all fields populated.

        Verifies all fields can be set and are stored correctly.
        """
        decision = Decision(**sample_decision_data)

        assert decision.question == sample_decision_data["question"]
        assert decision.decision == sample_decision_data["decision"]
        assert decision.rationale == sample_decision_data["rationale"]
        assert decision.alternatives == sample_decision_data["alternatives"]
        assert decision.decided_by == sample_decision_data["decided_by"]
        assert decision.session_id == sample_decision_data["session_id"]
        assert decision.topics == sample_decision_data["topics"]

    def test_decision_required_fields_validation(self) -> None:
        """Test that all required fields must be non-empty strings.

        Verifies min_length=1 constraint on all required string fields.
        """
        # Missing required field
        with pytest.raises(ValidationError) as exc_info:
            Decision(
                question="Test?",
                decision="Test decision",
                rationale="Test rationale",
                decided_by="claude",
                # session_id is missing
            )
        assert any(e["type"] == "missing" for e in exc_info.value.errors())

        # Empty string for required field
        with pytest.raises(ValidationError) as exc_info:
            Decision(
                question="",
                decision="Test",
                rationale="Test",
                decided_by="claude",
                session_id="123",
            )
        assert any(
            e["loc"] == ("question",) and e["type"] == "string_too_short"
            for e in exc_info.value.errors()
        )

    def test_decision_json_serialization(self, sample_decision_data: Dict[str, Any]) -> None:
        """Test JSON serialization and deserialization.

        Verifies round-trip serialization preserves all data.
        """
        decision = Decision(**sample_decision_data)

        # Serialize and deserialize
        json_str = decision.model_dump_json()
        decision2 = Decision.model_validate_json(json_str)

        assert decision2.question == decision.question
        assert decision2.decision == decision.decision
        assert decision2.alternatives == decision.alternatives
        assert decision2.topics == decision.topics


class TestLearningModel:
    """Test the Learning Pydantic model."""

    def test_learning_creation_minimal(self) -> None:
        """Test creating Learning with minimal required fields.

        Verifies:
        - All required fields must be provided
        - created_at is auto-populated
        """
        learning = Learning(
            pattern="Tests improve code quality",
            confidence=0.9,
            learned_from=["session_1"],
            category="testing",
        )

        assert learning.pattern == "Tests improve code quality"
        assert learning.confidence == 0.9
        assert learning.learned_from == ["session_1"]
        assert learning.category == "testing"
        assert isinstance(learning.created_at, datetime)

    def test_learning_creation_full(self, sample_learning_data: Dict[str, Any]) -> None:
        """Test creating Learning with all fields populated.

        Verifies all fields can be set and are stored correctly.
        """
        now = datetime.now(timezone.utc)
        sample_learning_data["created_at"] = now

        learning = Learning(**sample_learning_data)

        assert learning.pattern == sample_learning_data["pattern"]
        assert learning.confidence == sample_learning_data["confidence"]
        assert learning.learned_from == sample_learning_data["learned_from"]
        assert learning.category == sample_learning_data["category"]
        assert learning.created_at == now

    def test_learning_confidence_bounds(self) -> None:
        """Test that confidence score is constrained to [0.0, 1.0].

        Verifies ge=0.0 and le=1.0 constraints are enforced.
        """
        # Valid bounds
        Learning(
            pattern="Test",
            confidence=0.0,
            learned_from=["s1"],
            category="test",
        )
        Learning(
            pattern="Test",
            confidence=1.0,
            learned_from=["s1"],
            category="test",
        )

        # Below lower bound
        with pytest.raises(ValidationError) as exc_info:
            Learning(
                pattern="Test",
                confidence=-0.1,
                learned_from=["s1"],
                category="test",
            )
        assert any(
            e["loc"] == ("confidence",) and "greater_than_equal" in e["type"]
            for e in exc_info.value.errors()
        )

        # Above upper bound
        with pytest.raises(ValidationError) as exc_info:
            Learning(
                pattern="Test",
                confidence=1.5,
                learned_from=["s1"],
                category="test",
            )
        assert any(
            e["loc"] == ("confidence",) and "less_than_equal" in e["type"]
            for e in exc_info.value.errors()
        )

    def test_learning_learned_from_not_empty(self) -> None:
        """Test that learned_from must contain at least one session.

        Verifies the field_validator ensures non-empty list.
        """
        with pytest.raises(ValidationError) as exc_info:
            Learning(
                pattern="Test pattern",
                confidence=0.8,
                learned_from=[],
                category="test",
            )

        errors = exc_info.value.errors()
        assert any(
            e["loc"] == ("learned_from",) and "at least one session" in str(e["ctx"])
            for e in errors
        )

    def test_learning_json_serialization(self, sample_learning_data: Dict[str, Any]) -> None:
        """Test JSON serialization and deserialization.

        Verifies round-trip serialization preserves all data.
        """
        learning = Learning(**sample_learning_data)

        json_str = learning.model_dump_json()
        learning2 = Learning.model_validate_json(json_str)

        assert learning2.pattern == learning.pattern
        assert learning2.confidence == learning.confidence
        assert learning2.learned_from == learning.learned_from
        assert learning2.category == learning.category


class TestArtifactModel:
    """Test the Artifact Pydantic model."""

    def test_artifact_creation_minimal(self) -> None:
        """Test creating Artifact with only required fields.

        Verifies:
        - All required fields must be provided
        - Optional fields get default values
        """
        artifact = Artifact(
            type="function",
            path="src/utils.py::helper_function",
            description="Helper function for data processing",
            created_in_session="session_123",
        )

        assert artifact.type == "function"
        assert artifact.path == "src/utils.py::helper_function"
        assert artifact.description == "Helper function for data processing"
        assert artifact.created_in_session == "session_123"
        assert artifact.topics == []

    def test_artifact_creation_full(self, sample_artifact_data: Dict[str, Any]) -> None:
        """Test creating Artifact with all fields populated.

        Verifies all fields can be set and are stored correctly.
        """
        artifact = Artifact(**sample_artifact_data)

        assert artifact.type == sample_artifact_data["type"]
        assert artifact.path == sample_artifact_data["path"]
        assert artifact.description == sample_artifact_data["description"]
        assert artifact.created_in_session == sample_artifact_data["created_in_session"]
        assert artifact.topics == sample_artifact_data["topics"]

    def test_artifact_required_fields_validation(self) -> None:
        """Test that all required fields must be non-empty strings.

        Verifies min_length=1 constraint on all required string fields.
        """
        # Missing required field
        with pytest.raises(ValidationError) as exc_info:
            Artifact(
                type="class",
                path="src/models.py::MyClass",
                description="A class",
                # created_in_session is missing
            )
        assert any(e["type"] == "missing" for e in exc_info.value.errors())

        # Empty string for required field
        with pytest.raises(ValidationError) as exc_info:
            Artifact(
                type="",
                path="src/test.py",
                description="Test",
                created_in_session="s1",
            )
        assert any(
            e["loc"] == ("type",) and e["type"] == "string_too_short"
            for e in exc_info.value.errors()
        )

    def test_artifact_json_serialization(self, sample_artifact_data: Dict[str, Any]) -> None:
        """Test JSON serialization and deserialization.

        Verifies round-trip serialization preserves all data.
        """
        artifact = Artifact(**sample_artifact_data)

        json_str = artifact.model_dump_json()
        artifact2 = Artifact.model_validate_json(json_str)

        assert artifact2.type == artifact.type
        assert artifact2.path == artifact.path
        assert artifact2.description == artifact.description
        assert artifact2.topics == artifact.topics


class TestSearchResultModel:
    """Test the SearchResult Pydantic model."""

    def test_search_result_creation_minimal(self) -> None:
        """Test creating SearchResult with only required fields.

        Verifies:
        - Required fields must be provided
        - Optional fields get default values
        """
        result = SearchResult(
            type="convention",
            content="Use type hints everywhere",
            relevance_score=0.85,
        )

        assert result.type == "convention"
        assert result.content == "Use type hints everywhere"
        assert result.relevance_score == 0.85
        assert result.source_session is None
        assert result.metadata == {}

    def test_search_result_creation_full(
        self, sample_search_result_data: Dict[str, Any]
    ) -> None:
        """Test creating SearchResult with all fields populated.

        Verifies all fields can be set and are stored correctly.
        """
        result = SearchResult(**sample_search_result_data)

        assert result.type == sample_search_result_data["type"]
        assert result.content == sample_search_result_data["content"]
        assert result.relevance_score == sample_search_result_data["relevance_score"]
        assert result.source_session == sample_search_result_data["source_session"]
        assert result.metadata == sample_search_result_data["metadata"]

    def test_search_result_type_validation(self) -> None:
        """Test that type field only accepts valid result types.

        Verifies the field_validator enforces allowed types.
        """
        valid_types = ["convention", "decision", "learning", "conversation", "artifact"]

        # Valid types should work
        for valid_type in valid_types:
            result = SearchResult(
                type=valid_type,
                content="Test content",
                relevance_score=0.8,
            )
            assert result.type == valid_type

        # Invalid type should raise error
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(
                type="invalid_type",
                content="Test content",
                relevance_score=0.8,
            )

        errors = exc_info.value.errors()
        assert any(
            e["loc"] == ("type",) and "Invalid result type" in str(e["ctx"])
            for e in errors
        )

    def test_search_result_relevance_score_bounds(self) -> None:
        """Test that relevance_score is constrained to [0.0, 1.0].

        Verifies ge=0.0 and le=1.0 constraints are enforced.
        """
        # Valid bounds
        SearchResult(type="convention", content="Test", relevance_score=0.0)
        SearchResult(type="convention", content="Test", relevance_score=1.0)
        SearchResult(type="convention", content="Test", relevance_score=0.5)

        # Below lower bound
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(type="convention", content="Test", relevance_score=-0.1)
        assert any(
            e["loc"] == ("relevance_score",) and "greater_than_equal" in e["type"]
            for e in exc_info.value.errors()
        )

        # Above upper bound
        with pytest.raises(ValidationError) as exc_info:
            SearchResult(type="convention", content="Test", relevance_score=1.2)
        assert any(
            e["loc"] == ("relevance_score",) and "less_than_equal" in e["type"]
            for e in exc_info.value.errors()
        )

    def test_search_result_metadata_any_structure(self) -> None:
        """Test that metadata field accepts arbitrary dict structures.

        Verifies Dict[str, Any] allows flexible metadata storage.
        """
        # Various metadata structures
        result1 = SearchResult(
            type="convention",
            content="Test",
            relevance_score=0.8,
            metadata={"topics": ["test"], "count": 5, "nested": {"key": "value"}},
        )
        assert result1.metadata["nested"]["key"] == "value"

        # Empty metadata
        result2 = SearchResult(
            type="decision",
            content="Test",
            relevance_score=0.7,
            metadata={},
        )
        assert result2.metadata == {}

        # Rich metadata
        result3 = SearchResult(
            type="learning",
            content="Test",
            relevance_score=0.9,
            metadata={
                "confidence": 0.95,
                "sessions": ["s1", "s2"],
                "verified": True,
                "metrics": {"accuracy": 0.88, "precision": 0.92},
            },
        )
        assert result3.metadata["metrics"]["accuracy"] == 0.88

    def test_search_result_json_serialization(
        self, sample_search_result_data: Dict[str, Any]
    ) -> None:
        """Test JSON serialization and deserialization.

        Verifies round-trip serialization preserves all data including metadata.
        """
        result = SearchResult(**sample_search_result_data)

        json_str = result.model_dump_json()
        result2 = SearchResult.model_validate_json(json_str)

        assert result2.type == result.type
        assert result2.content == result.content
        assert result2.relevance_score == result.relevance_score
        assert result2.metadata == result.metadata


class TestModelInteroperability:
    """Test interactions between different knowledge models."""

    def test_models_can_be_serialized_together(
        self,
        sample_convention_data: Dict[str, Any],
        sample_decision_data: Dict[str, Any],
        sample_learning_data: Dict[str, Any],
    ) -> None:
        """Test that different models can be serialized in the same structure.

        Verifies models can coexist in lists/dicts for knowledge storage.
        """
        convention = Convention(**sample_convention_data)
        decision = Decision(**sample_decision_data)
        learning = Learning(**sample_learning_data)

        # Create a composite structure
        knowledge_base = {
            "conventions": [convention.model_dump()],
            "decisions": [decision.model_dump()],
            "learnings": [learning.model_dump()],
        }

        assert len(knowledge_base["conventions"]) == 1
        assert len(knowledge_base["decisions"]) == 1
        assert len(knowledge_base["learnings"]) == 1

    def test_search_result_can_reference_all_types(self) -> None:
        """Test that SearchResult can represent results from all knowledge types.

        Verifies SearchResult is a universal container for search results.
        """
        types_to_test = ["convention", "decision", "learning", "conversation", "artifact"]

        results = [
            SearchResult(
                type=result_type,
                content=f"Content for {result_type}",
                relevance_score=0.8,
            )
            for result_type in types_to_test
        ]

        assert len(results) == 5
        assert all(isinstance(r, SearchResult) for r in results)
        assert [r.type for r in results] == types_to_test
