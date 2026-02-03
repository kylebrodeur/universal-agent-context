# Task Group 5: Comprehensive Test Suite for v0.3.0

**Status:** Ready for Implementation
**Priority:** High (ensures reliability)
**Estimated Effort:** 6-8 hours
**Dependencies:** Task Groups 1 & 2 Complete ✅

---

## Overview

Create comprehensive test coverage for UACS v0.3.0 semantic API to ensure reliability and prevent regressions.

### Current Test Status

**Existing Tests (✅ Passing):**
- `tests/test_embedding_manager.py` - 43 tests for embeddings (ALL PASSING)
- `tests/test_shared_context.py` - Tests for old SharedContextManager
- `tests/test_visualization_server.py` - 15+ tests for web visualizer

**Missing Tests (⏳ Need to Add):**
- ConversationManager tests (user messages, assistant messages, tool uses)
- KnowledgeManager tests (decisions, conventions, learnings, artifacts)
- Unified UACS API tests (all semantic methods)
- Hook integration tests
- Search functionality tests
- End-to-end workflow tests

---

## Test Suite Structure

```
tests/
├── test_conversation_manager.py    # NEW - Unit tests for conversations
├── test_knowledge_manager.py       # NEW - Unit tests for knowledge
├── test_uacs_unified_api.py        # NEW - Integration tests for UACS class
├── test_semantic_search.py         # NEW - Search functionality tests
├── test_hook_integration.py        # NEW - Hook integration tests
├── test_embedding_manager.py       # ✅ EXISTS - 43 tests passing
├── test_shared_context.py          # ✅ EXISTS
└── test_visualization_server.py    # ✅ EXISTS
```

---

## Task Breakdown

### Phase 1: ConversationManager Tests (2 hours)

**File:** `tests/test_conversation_manager.py`

**Tests to write:**

1. **User Message Tests:**
   ```python
   def test_add_user_message()
   def test_add_user_message_with_topics()
   def test_add_user_message_creates_embedding()
   def test_list_user_messages()
   def test_get_user_message_by_id()
   def test_user_message_validation()  # Test invalid inputs
   ```

2. **Assistant Message Tests:**
   ```python
   def test_add_assistant_message()
   def test_add_assistant_message_with_tokens()
   def test_add_assistant_message_with_model()
   def test_assistant_message_creates_embedding()
   def test_list_assistant_messages()
   def test_get_assistant_message_by_id()
   ```

3. **Tool Use Tests:**
   ```python
   def test_add_tool_use()
   def test_add_tool_use_with_latency()
   def test_add_tool_use_with_success_false()
   def test_tool_use_creates_embedding()
   def test_list_tool_uses()
   def test_get_tool_use_by_id()
   ```

4. **Search Tests:**
   ```python
   def test_search_user_messages()
   def test_search_assistant_messages()
   def test_search_tool_uses()
   def test_search_by_session_id()
   def test_search_with_type_filter()
   def test_search_threshold()
   ```

5. **Statistics Tests:**
   ```python
   def test_get_stats()
   def test_stats_per_session()
   def test_token_stats()
   ```

**Test Pattern Example:**
```python
import pytest
import tempfile
from pathlib import Path
from uacs.conversations.manager import ConversationManager
from uacs.embeddings.manager import EmbeddingManager

@pytest.fixture
def managers():
    """Create temporary managers for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        embeddings_path = tmpdir / "embeddings"
        conversations_path = tmpdir / "conversations"

        embedding_manager = EmbeddingManager(embeddings_path)
        conversation_manager = ConversationManager(
            conversations_path,
            embedding_manager
        )

        yield conversation_manager

def test_add_user_message(managers):
    """Test adding a user message."""
    msg = managers.add_user_message(
        content="Help me implement authentication",
        turn=1,
        session_id="test_001",
        topics=["security", "feature"]
    )

    assert msg.content == "Help me implement authentication"
    assert msg.turn == 1
    assert msg.session_id == "test_001"
    assert "security" in msg.topics
    assert "feature" in msg.topics
    assert msg.id is not None

def test_add_user_message_creates_embedding(managers):
    """Test that adding message creates embedding."""
    initial_count = managers.embedding_manager.get_stats()["total_vectors"]

    msg = managers.add_user_message(
        content="Test message",
        turn=1,
        session_id="test_001"
    )

    final_count = managers.embedding_manager.get_stats()["total_vectors"]
    assert final_count == initial_count + 1
```

### Phase 2: KnowledgeManager Tests (2 hours)

**File:** `tests/test_knowledge_manager.py`

**Tests to write:**

1. **Convention Tests:**
   ```python
   def test_add_convention()
   def test_add_convention_with_topics()
   def test_add_convention_with_source_session()
   def test_add_convention_with_confidence()
   def test_list_conventions()
   def test_get_convention_by_id()
   def test_convention_creates_embedding()
   ```

2. **Decision Tests:**
   ```python
   def test_add_decision()
   def test_add_decision_with_alternatives()
   def test_add_decision_with_decided_by()
   def test_add_decision_with_topics()
   def test_list_decisions()
   def test_get_decision_by_id()
   def test_decision_creates_embedding()
   ```

3. **Learning Tests:**
   ```python
   def test_add_learning()
   def test_add_learning_with_category()
   def test_add_learning_with_confidence()
   def test_list_learnings()
   def test_get_learning_by_id()
   def test_learning_creates_embedding()
   ```

4. **Artifact Tests:**
   ```python
   def test_add_artifact()
   def test_add_artifact_file_type()
   def test_add_artifact_function_type()
   def test_add_artifact_class_type()
   def test_list_artifacts()
   def test_get_artifact_by_id()
   def test_artifact_creates_embedding()
   ```

5. **Search Tests:**
   ```python
   def test_search_conventions()
   def test_search_decisions()
   def test_search_learnings()
   def test_search_artifacts()
   def test_search_by_type_filter()
   def test_search_min_confidence()
   ```

6. **Statistics Tests:**
   ```python
   def test_get_stats()
   def test_stats_by_category()
   def test_stats_by_confidence()
   ```

### Phase 3: Unified UACS API Tests (2 hours)

**File:** `tests/test_uacs_unified_api.py`

**Tests to write:**

1. **Initialization Tests:**
   ```python
   def test_uacs_init()
   def test_uacs_creates_directories()
   def test_uacs_initializes_managers()
   ```

2. **Semantic Method Tests:**
   ```python
   def test_uacs_add_user_message()
   def test_uacs_add_assistant_message()
   def test_uacs_add_tool_use()
   def test_uacs_add_convention()
   def test_uacs_add_decision()
   def test_uacs_add_learning()
   def test_uacs_add_artifact()
   ```

3. **Search Tests:**
   ```python
   def test_uacs_search_all_types()
   def test_uacs_search_filtered_by_type()
   def test_uacs_search_by_session_id()
   def test_uacs_search_sorts_by_relevance()
   def test_uacs_search_returns_correct_limit()
   ```

4. **Statistics Tests:**
   ```python
   def test_uacs_get_stats()
   def test_uacs_get_capabilities()
   def test_uacs_get_token_stats()
   ```

5. **Backward Compatibility Tests:**
   ```python
   def test_add_to_context_deprecated_warning()
   def test_add_to_context_still_works()
   def test_old_and_new_apis_coexist()
   ```

6. **End-to-End Workflow Tests:**
   ```python
   def test_complete_conversation_workflow():
       """Test a complete conversation workflow."""
       uacs = UACS(project_path=tmpdir)

       # User asks question
       user_msg = uacs.add_user_message(
           content="How do I implement auth?",
           turn=1,
           session_id="session_001",
           topics=["security"]
       )

       # Assistant responds
       assistant_msg = uacs.add_assistant_message(
           content="Let's use JWT...",
           turn=1,
           session_id="session_001",
           tokens_in=10,
           tokens_out=50
       )

       # Tool is used
       tool_use = uacs.add_tool_use(
           tool_name="Edit",
           tool_input={"file": "auth.py"},
           tool_response="Success",
           turn=2,
           session_id="session_001"
       )

       # Decision is made
       decision = uacs.add_decision(
           question="Which auth method?",
           decision="JWT tokens",
           rationale="Stateless",
           session_id="session_001"
       )

       # Search should find all of this
       results = uacs.search("authentication", limit=10)
       assert len(results) >= 4  # All 4 items should be found
   ```

### Phase 4: Semantic Search Tests (1 hour)

**File:** `tests/test_semantic_search.py`

**Tests to write:**

1. **Similarity Tests:**
   ```python
   def test_search_finds_similar_content()
   def test_search_similarity_scores()
   def test_search_ranking_by_relevance()
   ```

2. **Type Filtering Tests:**
   ```python
   def test_search_filter_by_user_message()
   def test_search_filter_by_decision()
   def test_search_filter_by_convention()
   def test_search_filter_multiple_types()
   ```

3. **Threshold Tests:**
   ```python
   def test_search_min_confidence_filters()
   def test_search_with_high_threshold()
   def test_search_with_low_threshold()
   ```

4. **Session Filtering Tests:**
   ```python
   def test_search_by_session_id()
   def test_search_across_all_sessions()
   ```

5. **Edge Cases:**
   ```python
   def test_search_empty_query()
   def test_search_no_results()
   def test_search_with_special_characters()
   def test_search_very_long_query()
   ```

### Phase 5: Hook Integration Tests (1-2 hours)

**File:** `tests/test_hook_integration.py`

**Tests to write:**

1. **Hook Execution Tests:**
   ```python
   def test_user_prompt_submit_hook()
   def test_post_tool_use_hook()
   def test_session_end_hook()
   ```

2. **Hook Data Validation:**
   ```python
   def test_hook_input_format()
   def test_hook_output_format()
   def test_hook_error_handling()
   ```

3. **Hook + UACS Integration:**
   ```python
   def test_hook_stores_to_uacs()
   def test_hook_creates_embeddings()
   def test_hook_extractable_by_search()
   ```

**Test Pattern Example:**
```python
import json
import subprocess

def test_user_prompt_submit_hook(tmpdir):
    """Test UserPromptSubmit hook integration."""
    hook_input = {
        "prompt": "Help with authentication",
        "session_id": "test_001",
        "cwd": str(tmpdir),
        "turn": 1
    }

    result = subprocess.run(
        ["python3", ".claude-plugin/hooks/uacs_capture_message.py"],
        input=json.dumps(hook_input),
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["continue"] == True

    # Verify data was stored
    uacs = UACS(project_path=tmpdir)
    stats = uacs.get_stats()
    assert stats["semantic"]["conversations"]["total_user_messages"] == 1
```

---

## Test Coverage Goals

### Target Coverage: 90%+

**By Module:**
- ConversationManager: 90%+
- KnowledgeManager: 90%+
- EmbeddingManager: ✅ Already 95%+ (43 tests passing)
- UACS Unified API: 85%+
- Search functionality: 85%+
- Hooks: 80%+ (harder to test)

### Critical Paths to Cover:

1. **Happy Path:** All semantic methods work correctly
2. **Edge Cases:** Empty inputs, null values, invalid data
3. **Error Handling:** Graceful failures, clear error messages
4. **Integration:** All components work together
5. **Backward Compatibility:** Old API still works

---

## Running Tests

### Run All Tests:
```bash
pytest tests/ -v
```

### Run Specific Test File:
```bash
pytest tests/test_conversation_manager.py -v
```

### Run with Coverage:
```bash
pytest tests/ --cov=src/uacs --cov-report=html
open htmlcov/index.html
```

### Run Specific Test:
```bash
pytest tests/test_conversation_manager.py::test_add_user_message -v
```

---

## Success Criteria

- [ ] All new test files created (5 files)
- [ ] Minimum 50 new tests written
- [ ] All tests passing (100% pass rate)
- [ ] Coverage >= 90% for new code
- [ ] No regressions (existing tests still pass)
- [ ] CI/CD integration (GitHub Actions)

---

## Implementation Prompt

Use this prompt with an agent:

```
# Task: Create Comprehensive Test Suite for UACS v0.3.0

## Context
You need to write comprehensive tests for the new semantic API (conversations, knowledge, embeddings, unified UACS).

## Reference
- Test Plan: .github/TASK_GROUP_5_TEST_SUITE.md (THIS FILE)
- Existing Tests: tests/test_embedding_manager.py (43 tests, good example)
- Code to Test: src/uacs/api.py, src/uacs/conversations/, src/uacs/knowledge/

## Your Task
1. Create 5 new test files as specified in the plan
2. Write minimum 50 tests total
3. Achieve 90%+ coverage for new code
4. Ensure all tests pass

## Test Priority
1. test_uacs_unified_api.py (most critical)
2. test_conversation_manager.py
3. test_knowledge_manager.py
4. test_semantic_search.py
5. test_hook_integration.py

## Guidelines
- Use pytest fixtures for setup/teardown
- Use tempfile for temporary directories
- Follow existing test patterns (see test_embedding_manager.py)
- Test both happy path and edge cases
- Add docstrings to all test functions
```

---

## Files to Reference

- **Example tests:** tests/test_embedding_manager.py (43 passing tests)
- **Code to test:** src/uacs/api.py:91-152 (unified API)
- **ConversationManager:** src/uacs/conversations/manager.py
- **KnowledgeManager:** src/uacs/knowledge/manager.py
- **Models:** src/uacs/conversations/models.py, src/uacs/knowledge/models.py
- **Hooks:** .claude-plugin/hooks/*.py

---

**Status:** ✅ Ready for Implementation
**Next Step:** Start with test_uacs_unified_api.py (highest priority)
