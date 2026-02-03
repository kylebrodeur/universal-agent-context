"""Knowledge manager for semantic knowledge management in UACS.

This module provides the KnowledgeManager class which handles:
- Storing and retrieving conventions, decisions, learnings, and artifacts
- Semantic deduplication using embeddings
- Confidence scoring and decay over time
- Natural language search across all knowledge types
- Persistent JSON storage
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from uacs.embeddings import EmbeddingManager
from uacs.knowledge.models import (
    Artifact,
    Convention,
    Decision,
    Learning,
    SearchResult,
)

logger = logging.getLogger(__name__)


class KnowledgeManagerError(Exception):
    """Base exception for knowledge manager errors."""

    pass


class KnowledgeManager:
    """Manages structured knowledge with semantic search and deduplication.

    The KnowledgeManager provides a high-level API for storing and retrieving
    project knowledge including conventions, decisions, learnings, and artifacts.
    It uses semantic embeddings for intelligent deduplication and natural language
    search.

    Storage structure:
        ```
        storage_path/
        ├── knowledge/
        │   ├── conventions.json
        │   ├── decisions.json
        │   ├── learnings.json
        │   └── artifacts.json
        └── embeddings/
            ├── index.faiss
            └── metadata.json
        ```

    Example:
        ```python
        from pathlib import Path
        from uacs.knowledge import KnowledgeManager

        # Initialize manager
        manager = KnowledgeManager(Path(".state"))

        # Add convention (with automatic deduplication)
        convention = manager.add_convention(
            content="Use Pydantic for all data models",
            topics=["validation", "data-models"],
            source_session="session_123"
        )

        # Add decision
        decision = manager.add_decision(
            question="How should we handle API auth?",
            decision="Use JWT with refresh tokens",
            rationale="Provides good security and is stateless",
            decided_by="claude-opus-4-5",
            session_id="session_123"
        )

        # Search across all knowledge
        results = manager.search("authentication", limit=10)
        for result in results:
            print(f"{result.type}: {result.content} ({result.relevance_score:.2f})")

        # Decay confidence over time
        manager.decay_confidence(max_age_days=90)
        ```
    """

    # Deduplication threshold for semantic similarity
    DEFAULT_DEDUP_THRESHOLD = 0.85

    # Confidence decay parameters
    CONFIDENCE_DECAY_RATE = 0.01  # Decay per day

    def __init__(
        self,
        storage_path: Path,
        embedding_manager: Optional[EmbeddingManager] = None,
    ):
        """Initialize the knowledge manager.

        Args:
            storage_path: Base directory for storage (typically .state/)
            embedding_manager: Optional EmbeddingManager instance. If not provided,
                             a new one will be created in storage_path/embeddings/

        Raises:
            KnowledgeManagerError: If initialization fails
        """
        self.storage_path = Path(storage_path)
        self.knowledge_path = self.storage_path / "knowledge"

        # Create directories
        self.knowledge_path.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.conventions_file = self.knowledge_path / "conventions.json"
        self.decisions_file = self.knowledge_path / "decisions.json"
        self.learnings_file = self.knowledge_path / "learnings.json"
        self.artifacts_file = self.knowledge_path / "artifacts.json"

        # Initialize or use provided embedding manager
        if embedding_manager is None:
            embeddings_path = self.storage_path / "embeddings"
            self.embeddings = EmbeddingManager(embeddings_path)
        else:
            self.embeddings = embedding_manager

        # In-memory caches (loaded from JSON files)
        self.conventions: dict[str, Convention] = {}
        self.decisions: dict[str, Decision] = {}
        self.learnings: dict[str, Learning] = {}
        self.artifacts: dict[str, Artifact] = {}

        # Load existing knowledge
        self._load_knowledge()

        logger.info(
            f"KnowledgeManager initialized with {len(self.conventions)} conventions, "
            f"{len(self.decisions)} decisions, {len(self.learnings)} learnings, "
            f"{len(self.artifacts)} artifacts"
        )

    def _load_knowledge(self) -> None:
        """Load all knowledge from JSON files.

        Raises:
            KnowledgeManagerError: If loading fails
        """
        try:
            # Load conventions
            if self.conventions_file.exists():
                with open(self.conventions_file, "r", encoding="utf-8") as f:
                    conventions_data = json.load(f)
                    self.conventions = {
                        cid: self._convention_from_json(data)
                        for cid, data in conventions_data.items()
                    }

            # Load decisions
            if self.decisions_file.exists():
                with open(self.decisions_file, "r", encoding="utf-8") as f:
                    decisions_data = json.load(f)
                    self.decisions = {
                        did: self._decision_from_json(data)
                        for did, data in decisions_data.items()
                    }

            # Load learnings
            if self.learnings_file.exists():
                with open(self.learnings_file, "r", encoding="utf-8") as f:
                    learnings_data = json.load(f)
                    self.learnings = {
                        lid: self._learning_from_json(data)
                        for lid, data in learnings_data.items()
                    }

            # Load artifacts
            if self.artifacts_file.exists():
                with open(self.artifacts_file, "r", encoding="utf-8") as f:
                    artifacts_data = json.load(f)
                    self.artifacts = {
                        aid: self._artifact_from_json(data)
                        for aid, data in artifacts_data.items()
                    }

        except Exception as e:
            raise KnowledgeManagerError(f"Failed to load knowledge: {e}") from e

    def _save_knowledge(self) -> None:
        """Save all knowledge to JSON files.

        Raises:
            KnowledgeManagerError: If saving fails
        """
        try:
            # Save conventions
            conventions_data = {
                cid: self._convention_to_json(conv)
                for cid, conv in self.conventions.items()
            }
            with open(self.conventions_file, "w", encoding="utf-8") as f:
                json.dump(conventions_data, f, indent=2, ensure_ascii=False)

            # Save decisions
            decisions_data = {
                did: self._decision_to_json(dec) for did, dec in self.decisions.items()
            }
            with open(self.decisions_file, "w", encoding="utf-8") as f:
                json.dump(decisions_data, f, indent=2, ensure_ascii=False)

            # Save learnings
            learnings_data = {
                lid: self._learning_to_json(learn)
                for lid, learn in self.learnings.items()
            }
            with open(self.learnings_file, "w", encoding="utf-8") as f:
                json.dump(learnings_data, f, indent=2, ensure_ascii=False)

            # Save artifacts
            artifacts_data = {
                aid: self._artifact_to_json(art) for aid, art in self.artifacts.items()
            }
            with open(self.artifacts_file, "w", encoding="utf-8") as f:
                json.dump(artifacts_data, f, indent=2, ensure_ascii=False)

            # Save embedding index
            self.embeddings.save_index()

        except Exception as e:
            raise KnowledgeManagerError(f"Failed to save knowledge: {e}") from e

    # Serialization helpers
    def _convention_to_json(self, convention: Convention) -> dict[str, Any]:
        """Convert Convention to JSON-serializable dict."""
        return {
            "content": convention.content,
            "topics": convention.topics,
            "source_session": convention.source_session,
            "confidence": convention.confidence,
            "created_at": convention.created_at.isoformat(),
            "last_verified": (
                convention.last_verified.isoformat()
                if convention.last_verified
                else None
            ),
        }

    def _convention_from_json(self, data: dict[str, Any]) -> Convention:
        """Create Convention from JSON dict."""
        return Convention(
            content=data["content"],
            topics=data.get("topics", []),
            source_session=data.get("source_session"),
            confidence=data.get("confidence", 1.0),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_verified=(
                datetime.fromisoformat(data["last_verified"])
                if data.get("last_verified")
                else None
            ),
        )

    def _decision_to_json(self, decision: Decision) -> dict[str, Any]:
        """Convert Decision to JSON-serializable dict."""
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

    def _decision_from_json(self, data: dict[str, Any]) -> Decision:
        """Create Decision from JSON dict."""
        return Decision(
            question=data["question"],
            decision=data["decision"],
            rationale=data["rationale"],
            alternatives=data.get("alternatives", []),
            decided_at=datetime.fromisoformat(data["decided_at"]),
            decided_by=data["decided_by"],
            session_id=data["session_id"],
            topics=data.get("topics", []),
        )

    def _learning_to_json(self, learning: Learning) -> dict[str, Any]:
        """Convert Learning to JSON-serializable dict."""
        return {
            "pattern": learning.pattern,
            "confidence": learning.confidence,
            "learned_from": learning.learned_from,
            "category": learning.category,
            "created_at": learning.created_at.isoformat(),
        }

    def _learning_from_json(self, data: dict[str, Any]) -> Learning:
        """Create Learning from JSON dict."""
        return Learning(
            pattern=data["pattern"],
            confidence=data["confidence"],
            learned_from=data["learned_from"],
            category=data["category"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def _artifact_to_json(self, artifact: Artifact) -> dict[str, Any]:
        """Convert Artifact to JSON-serializable dict."""
        return {
            "type": artifact.type,
            "path": artifact.path,
            "description": artifact.description,
            "created_in_session": artifact.created_in_session,
            "topics": artifact.topics,
        }

    def _artifact_from_json(self, data: dict[str, Any]) -> Artifact:
        """Create Artifact from JSON dict."""
        return Artifact(
            type=data["type"],
            path=data["path"],
            description=data["description"],
            created_in_session=data["created_in_session"],
            topics=data.get("topics", []),
        )

    # Public API - Add Knowledge
    def add_convention(
        self,
        content: str,
        topics: Optional[list[str]] = None,
        source_session: Optional[str] = None,
        confidence: float = 1.0,
    ) -> Convention:
        """Add a project convention with semantic deduplication.

        Before adding, checks for semantically similar conventions. If a duplicate
        is found (similarity >= 0.85), the existing convention's confidence is
        increased instead of creating a new one.

        Args:
            content: Description of the convention
            topics: Optional list of topic tags
            source_session: Optional session ID where convention was established
            confidence: Initial confidence score (0.0-1.0, default 1.0)

        Returns:
            Convention object (either newly created or existing with updated confidence)

        Raises:
            KnowledgeManagerError: If adding fails
        """
        if not content or not content.strip():
            raise KnowledgeManagerError("Convention content cannot be empty")

        try:
            # Check for semantic duplicates
            duplicate_id = self.embeddings.check_duplicate(
                content, threshold=self.DEFAULT_DEDUP_THRESHOLD
            )

            if duplicate_id:
                # Extract convention ID from embedding metadata ID
                # Format: "convention:<uuid>"
                if duplicate_id.startswith("convention:"):
                    conv_id = duplicate_id.replace("convention:", "")
                    if conv_id in self.conventions:
                        existing = self.conventions[conv_id]
                        # Increase confidence (capped at 1.0)
                        existing.confidence = min(1.0, existing.confidence + 0.1)
                        existing.last_verified = datetime.utcnow()
                        self._save_knowledge()
                        logger.info(
                            f"Found duplicate convention, increased confidence to "
                            f"{existing.confidence:.2f}"
                        )
                        return existing

            # Create new convention
            conv_id = str(uuid.uuid4())
            convention = Convention(
                content=content,
                topics=topics or [],
                source_session=source_session,
                confidence=confidence,
                created_at=datetime.utcnow(),
                last_verified=None,
            )

            # Add to storage
            self.conventions[conv_id] = convention

            # Add to embedding index
            embedding_id = f"convention:{conv_id}"
            self.embeddings.add_to_index(
                id=embedding_id,
                text=content,
                metadata={
                    "type": "convention",
                    "convention_id": conv_id,
                    "topics": topics or [],
                },
            )

            # Save to disk
            self._save_knowledge()

            logger.info(f"Added new convention: {conv_id}")
            return convention

        except Exception as e:
            raise KnowledgeManagerError(f"Failed to add convention: {e}") from e

    def add_decision(
        self,
        question: str,
        decision: str,
        rationale: str,
        decided_by: str,
        session_id: str,
        alternatives: Optional[list[str]] = None,
        topics: Optional[list[str]] = None,
    ) -> Decision:
        """Add an architectural decision.

        Decisions are not deduplicated as each decision is unique to its context.

        Args:
            question: The question or problem being addressed
            decision: The decision that was made
            rationale: Why this decision was made
            decided_by: Model or agent identifier
            session_id: Session where decision was made
            alternatives: Optional list of alternatives considered
            topics: Optional list of topic tags

        Returns:
            Decision object

        Raises:
            KnowledgeManagerError: If adding fails
        """
        if not all([question, decision, rationale, decided_by, session_id]):
            raise KnowledgeManagerError(
                "All decision fields (question, decision, rationale, "
                "decided_by, session_id) are required"
            )

        try:
            # Create decision
            dec_id = str(uuid.uuid4())
            decision_obj = Decision(
                question=question,
                decision=decision,
                rationale=rationale,
                alternatives=alternatives or [],
                decided_at=datetime.utcnow(),
                decided_by=decided_by,
                session_id=session_id,
                topics=topics or [],
            )

            # Add to storage
            self.decisions[dec_id] = decision_obj

            # Add to embedding index (concatenate all text for better search)
            decision_text = f"{question} {decision} {rationale}"
            embedding_id = f"decision:{dec_id}"
            self.embeddings.add_to_index(
                id=embedding_id,
                text=decision_text,
                metadata={
                    "type": "decision",
                    "decision_id": dec_id,
                    "topics": topics or [],
                },
            )

            # Save to disk
            self._save_knowledge()

            logger.info(f"Added new decision: {dec_id}")
            return decision_obj

        except Exception as e:
            raise KnowledgeManagerError(f"Failed to add decision: {e}") from e

    def add_learning(
        self,
        pattern: str,
        confidence: float,
        learned_from: list[str],
        category: str,
        topics: Optional[list[str]] = None,
    ) -> Learning:
        """Add a cross-session learning with semantic deduplication.

        Before adding, checks for semantically similar learnings. If a duplicate
        is found, the existing learning is updated with increased confidence and
        merged session references.

        Args:
            pattern: Description of the learned pattern
            confidence: Confidence score (0.0-1.0)
            learned_from: List of session IDs where pattern was observed
            category: Category of learning (e.g., 'performance', 'usability')
            topics: Optional list of topic tags

        Returns:
            Learning object (either newly created or existing with updated data)

        Raises:
            KnowledgeManagerError: If adding fails
        """
        if not pattern or not pattern.strip():
            raise KnowledgeManagerError("Learning pattern cannot be empty")

        if not learned_from:
            raise KnowledgeManagerError(
                "Learning must be derived from at least one session"
            )

        if not 0.0 <= confidence <= 1.0:
            raise KnowledgeManagerError("Confidence must be between 0.0 and 1.0")

        try:
            # Check for semantic duplicates
            duplicate_id = self.embeddings.check_duplicate(
                pattern, threshold=self.DEFAULT_DEDUP_THRESHOLD
            )

            if duplicate_id:
                # Extract learning ID
                if duplicate_id.startswith("learning:"):
                    learn_id = duplicate_id.replace("learning:", "")
                    if learn_id in self.learnings:
                        existing = self.learnings[learn_id]
                        # Merge sessions and increase confidence
                        existing.learned_from = list(
                            set(existing.learned_from + learned_from)
                        )
                        existing.confidence = min(
                            1.0, existing.confidence + (confidence * 0.5)
                        )
                        self._save_knowledge()
                        logger.info(
                            f"Found duplicate learning, merged sessions and increased "
                            f"confidence to {existing.confidence:.2f}"
                        )
                        return existing

            # Create new learning
            learn_id = str(uuid.uuid4())
            learning = Learning(
                pattern=pattern,
                confidence=confidence,
                learned_from=learned_from,
                category=category,
                created_at=datetime.utcnow(),
            )

            # Add to storage
            self.learnings[learn_id] = learning

            # Add to embedding index
            embedding_id = f"learning:{learn_id}"
            self.embeddings.add_to_index(
                id=embedding_id,
                text=pattern,
                metadata={
                    "type": "learning",
                    "learning_id": learn_id,
                    "category": category,
                    "topics": topics or [],
                },
            )

            # Save to disk
            self._save_knowledge()

            logger.info(f"Added new learning: {learn_id}")
            return learning

        except Exception as e:
            raise KnowledgeManagerError(f"Failed to add learning: {e}") from e

    def add_artifact(
        self,
        type: str,
        path: str,
        description: str,
        created_in_session: str,
        topics: Optional[list[str]] = None,
    ) -> Artifact:
        """Add a code artifact reference.

        Artifacts are not deduplicated as they represent unique file references.

        Args:
            type: Type of artifact (file, function, class, etc.)
            path: Path or identifier for the artifact
            description: Human-readable description
            created_in_session: Session ID where artifact was created
            topics: Optional list of topic tags

        Returns:
            Artifact object

        Raises:
            KnowledgeManagerError: If adding fails
        """
        if not all([type, path, description, created_in_session]):
            raise KnowledgeManagerError(
                "All artifact fields (type, path, description, "
                "created_in_session) are required"
            )

        try:
            # Create artifact
            art_id = str(uuid.uuid4())
            artifact = Artifact(
                type=type,
                path=path,
                description=description,
                created_in_session=created_in_session,
                topics=topics or [],
            )

            # Add to storage
            self.artifacts[art_id] = artifact

            # Add to embedding index (path + description for better search)
            artifact_text = f"{path} {description}"
            embedding_id = f"artifact:{art_id}"
            self.embeddings.add_to_index(
                id=embedding_id,
                text=artifact_text,
                metadata={
                    "type": "artifact",
                    "artifact_id": art_id,
                    "artifact_type": type,
                    "topics": topics or [],
                },
            )

            # Save to disk
            self._save_knowledge()

            logger.info(f"Added new artifact: {art_id}")
            return artifact

        except Exception as e:
            raise KnowledgeManagerError(f"Failed to add artifact: {e}") from e

    # Public API - Search
    def search(
        self,
        query: str,
        types: Optional[list[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Semantic search across all knowledge types.

        Args:
            query: Natural language search query
            types: Optional filter for result types
                  (convention, decision, learning, artifact)
            min_confidence: Minimum confidence threshold for conventions/learnings
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects, sorted by relevance

        Raises:
            KnowledgeManagerError: If search fails
        """
        try:
            # Search embeddings
            embedding_results = self.embeddings.search(
                query, k=limit * 2, threshold=0.6
            )  # Get more results for filtering

            # Convert to SearchResult objects
            search_results = []
            for result in embedding_results:
                result_type = result.metadata.get("type") if result.metadata else None

                # Filter by type if specified
                if types and result_type not in types:
                    continue

                # Build SearchResult based on type
                if result_type == "convention":
                    conv_id = (
                        result.metadata.get("convention_id")
                        if result.metadata
                        else None
                    )
                    if conv_id and conv_id in self.conventions:
                        conv = self.conventions[conv_id]
                        # Filter by confidence
                        if conv.confidence < min_confidence:
                            continue
                        search_results.append(
                            SearchResult(
                                type="convention",
                                content=conv.content,
                                relevance_score=result.similarity,
                                source_session=conv.source_session,
                                metadata={
                                    "topics": conv.topics,
                                    "confidence": conv.confidence,
                                },
                            )
                        )

                elif result_type == "decision":
                    dec_id = (
                        result.metadata.get("decision_id") if result.metadata else None
                    )
                    if dec_id and dec_id in self.decisions:
                        dec = self.decisions[dec_id]
                        search_results.append(
                            SearchResult(
                                type="decision",
                                content=f"{dec.question} → {dec.decision}",
                                relevance_score=result.similarity,
                                source_session=dec.session_id,
                                metadata={
                                    "topics": dec.topics,
                                    "rationale": dec.rationale,
                                    "decided_by": dec.decided_by,
                                },
                            )
                        )

                elif result_type == "learning":
                    learn_id = (
                        result.metadata.get("learning_id") if result.metadata else None
                    )
                    if learn_id and learn_id in self.learnings:
                        learn = self.learnings[learn_id]
                        # Filter by confidence
                        if learn.confidence < min_confidence:
                            continue
                        search_results.append(
                            SearchResult(
                                type="learning",
                                content=learn.pattern,
                                relevance_score=result.similarity,
                                source_session=(
                                    learn.learned_from[0]
                                    if learn.learned_from
                                    else None
                                ),
                                metadata={
                                    "confidence": learn.confidence,
                                    "category": learn.category,
                                    "session_count": len(learn.learned_from),
                                },
                            )
                        )

                elif result_type == "artifact":
                    art_id = (
                        result.metadata.get("artifact_id") if result.metadata else None
                    )
                    if art_id and art_id in self.artifacts:
                        art = self.artifacts[art_id]
                        search_results.append(
                            SearchResult(
                                type="artifact",
                                content=f"{art.path}: {art.description}",
                                relevance_score=result.similarity,
                                source_session=art.created_in_session,
                                metadata={
                                    "topics": art.topics,
                                    "artifact_type": art.type,
                                    "path": art.path,
                                },
                            )
                        )

            # Sort by relevance and limit
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            return search_results[:limit]

        except Exception as e:
            raise KnowledgeManagerError(f"Search failed: {e}") from e

    # Public API - Maintenance
    def decay_confidence(self, max_age_days: int = 90) -> int:
        """Decay confidence scores for old conventions and learnings.

        Confidence decays linearly based on age:
        - confidence = max(0.0, confidence - (age_days * decay_rate))

        Args:
            max_age_days: Age threshold for decay (default 90 days)

        Returns:
            Number of items that had their confidence decayed

        Raises:
            KnowledgeManagerError: If decay operation fails
        """
        try:
            now = datetime.utcnow()
            decayed_count = 0

            # Decay conventions
            for conv in self.conventions.values():
                age_days = (now - conv.created_at).days
                if age_days > 0:
                    decay_amount = age_days * self.CONFIDENCE_DECAY_RATE
                    old_confidence = conv.confidence
                    conv.confidence = max(0.0, conv.confidence - decay_amount)
                    if conv.confidence != old_confidence:
                        decayed_count += 1

            # Decay learnings
            for learn in self.learnings.values():
                age_days = (now - learn.created_at).days
                if age_days > 0:
                    decay_amount = age_days * self.CONFIDENCE_DECAY_RATE
                    old_confidence = learn.confidence
                    learn.confidence = max(0.0, learn.confidence - decay_amount)
                    if learn.confidence != old_confidence:
                        decayed_count += 1

            # Save changes
            if decayed_count > 0:
                self._save_knowledge()
                logger.info(f"Decayed confidence for {decayed_count} items")

            return decayed_count

        except Exception as e:
            raise KnowledgeManagerError(f"Confidence decay failed: {e}") from e

    def deduplicate(self) -> int:
        """Find and merge duplicate entries across all knowledge types.

        This is a maintenance operation that finds semantically similar items
        and merges them, keeping the one with higher confidence.

        Returns:
            Number of duplicates merged

        Raises:
            KnowledgeManagerError: If deduplication fails
        """
        try:
            merged_count = 0

            # Deduplicate conventions
            convention_ids = list(self.conventions.keys())
            for conv_id in convention_ids:
                if conv_id not in self.conventions:
                    continue  # Already merged

                conv = self.conventions[conv_id]
                similar = self.embeddings.search(
                    conv.content, k=5, threshold=self.DEFAULT_DEDUP_THRESHOLD
                )

                # Find other conventions with high similarity
                for result in similar:
                    if not result.id.startswith("convention:"):
                        continue
                    other_id = result.id.replace("convention:", "")
                    if other_id == conv_id or other_id not in self.conventions:
                        continue

                    # Merge: keep the one with higher confidence
                    other_conv = self.conventions[other_id]
                    if other_conv.confidence > conv.confidence:
                        # Keep other, remove current
                        del self.conventions[conv_id]
                        self.embeddings.remove_from_index(f"convention:{conv_id}")
                    else:
                        # Keep current, remove other
                        conv.confidence = min(
                            1.0, conv.confidence + (other_conv.confidence * 0.5)
                        )
                        del self.conventions[other_id]
                        self.embeddings.remove_from_index(f"convention:{other_id}")

                    merged_count += 1
                    break  # Only merge once per iteration

            # Similar process for learnings
            learning_ids = list(self.learnings.keys())
            for learn_id in learning_ids:
                if learn_id not in self.learnings:
                    continue

                learn = self.learnings[learn_id]
                similar = self.embeddings.search(
                    learn.pattern, k=5, threshold=self.DEFAULT_DEDUP_THRESHOLD
                )

                for result in similar:
                    if not result.id.startswith("learning:"):
                        continue
                    other_id = result.id.replace("learning:", "")
                    if other_id == learn_id or other_id not in self.learnings:
                        continue

                    # Merge: keep the one with higher confidence and merge sessions
                    other_learn = self.learnings[other_id]
                    if other_learn.confidence > learn.confidence:
                        del self.learnings[learn_id]
                        self.embeddings.remove_from_index(f"learning:{learn_id}")
                    else:
                        learn.learned_from = list(
                            set(learn.learned_from + other_learn.learned_from)
                        )
                        learn.confidence = min(
                            1.0, learn.confidence + (other_learn.confidence * 0.5)
                        )
                        del self.learnings[other_id]
                        self.embeddings.remove_from_index(f"learning:{other_id}")

                    merged_count += 1
                    break

            # Save changes
            if merged_count > 0:
                self._save_knowledge()
                logger.info(f"Merged {merged_count} duplicate items")

            return merged_count

        except Exception as e:
            raise KnowledgeManagerError(f"Deduplication failed: {e}") from e

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the knowledge store.

        Returns:
            Dictionary with knowledge statistics
        """
        return {
            "conventions": len(self.conventions),
            "decisions": len(self.decisions),
            "learnings": len(self.learnings),
            "artifacts": len(self.artifacts),
            "total_items": (
                len(self.conventions)
                + len(self.decisions)
                + len(self.learnings)
                + len(self.artifacts)
            ),
            "embedding_stats": self.embeddings.get_stats(),
            "storage_path": str(self.knowledge_path),
        }

    def __repr__(self) -> str:
        """String representation of knowledge manager."""
        return (
            f"KnowledgeManager(conventions={len(self.conventions)}, "
            f"decisions={len(self.decisions)}, learnings={len(self.learnings)}, "
            f"artifacts={len(self.artifacts)})"
        )
