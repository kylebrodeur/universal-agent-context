#!/usr/bin/env python3
"""
UACS UserPromptSubmit Hook - Local LLM Tagging

Uses a local embedded LLM (via transformers) to tag user prompts with topics/categories.
This provides better topic extraction than simple heuristics at zero API cost.

Hook Type: UserPromptSubmit (async)
Fires: On every user prompt
Matcher: None (fires for all prompts)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Global model cache (load once, reuse)
_model_cache = None
_tokenizer_cache = None


def tag_prompt_with_local_llm(hook_input: dict) -> dict:
    """Use embedded transformers model to tag user prompts with topics."""
    try:
        # Get hook inputs
        prompt = hook_input.get("prompt", "")
        session_id = hook_input.get("session_id", "unknown")
        project_dir = hook_input.get("cwd", ".")

        if not prompt or len(prompt.strip()) < 10:
            # Too short to meaningfully categorize
            return {"continue": True, "message": "UACS: Prompt too short to tag"}

        # Try LLM-based extraction, fallback to heuristics
        try:
            topics = extract_topics_with_transformers(prompt)
        except Exception as llm_error:
            # LLM failed (missing deps, model issues, etc.) - use heuristics
            topics = extract_topics_heuristic(prompt)

        if not topics:
            # Fallback to heuristics if LLM returns nothing
            topics = extract_topics_heuristic(prompt)

        # Store topics for this session (for later use by PostToolUse)
        store_session_topics(project_dir, session_id, topics)

        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "message": f"UACS: Tagged with {len(topics)} topics: {', '.join(topics[:3])}",
            }
        }

    except Exception as e:
        # Non-blocking - don't interrupt user's prompt
        return {
            "continue": True,
            "error": str(e),
            "message": f"UACS: Tagging failed (non-critical): {type(e).__name__}",
        }


def extract_topics_with_transformers(prompt: str) -> list[str]:
    """Use embedded transformers model to extract topics from prompt.

    Uses TinyLlama-1.1B-Chat (1.1B params, ~2GB) for fast, embedded inference.
    Model is cached after first load for performance.

    Args:
        prompt: User's prompt text

    Returns:
        List of topic strings (e.g., ["security", "authentication", "bug-fix"])
    """
    global _model_cache, _tokenizer_cache

    try:
        # Lazy import (only if transformers is installed)
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
    except ImportError:
        # transformers not installed - fall back to heuristics
        return []

    # Load model once and cache
    if _model_cache is None or _tokenizer_cache is None:
        try:
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            _tokenizer_cache = AutoTokenizer.from_pretrained(model_name)
            _model_cache = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True,
            )
            _model_cache.eval()  # Inference mode
        except Exception as e:
            # Model loading failed - fall back to heuristics
            return []

    # Truncate very long prompts to save inference time
    if len(prompt) > 500:
        prompt_for_llm = prompt[:500] + "..."
    else:
        prompt_for_llm = prompt

    # Construct prompt for topic extraction
    system_prompt = """Categorize this programming task into 2-4 relevant topics.

Choose from these categories:
- testing, security, performance, bug-fix, feature, documentation
- deployment, database, api, frontend, backend, architecture
- refactoring, code-review, dependencies, configuration, tooling

Output ONLY comma-separated topics (e.g., "security, authentication, bug-fix").
Be concise and specific."""

    full_prompt = f"""<|system|>
{system_prompt}</s>
<|user|>
Task: {prompt_for_llm}

Topics:</s>
<|assistant|>
"""

    try:
        # Tokenize
        inputs = _tokenizer_cache(full_prompt, return_tensors="pt", truncation=True, max_length=512)

        if torch.cuda.is_available():
            inputs = {k: v.to(_model_cache.device) for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            outputs = _model_cache.generate(
                **inputs,
                max_new_tokens=30,  # Short output (just topics)
                temperature=0.3,  # Lower temp for consistent categorization
                do_sample=True,
                pad_token_id=_tokenizer_cache.eos_token_id,
            )

        # Decode
        response_text = _tokenizer_cache.decode(outputs[0], skip_special_tokens=True)

        # Extract just the topics (after "Topics:")
        if "Topics:" in response_text:
            topics_text = response_text.split("Topics:")[-1].strip()
        else:
            topics_text = response_text.strip()

        # Parse comma-separated topics
        topics = [t.strip().lower() for t in topics_text.split(",")]

        # Clean up topics (remove empty, duplicates, junk)
        topics = [t for t in topics if t and len(t) > 2 and len(t) < 30]
        topics = list(dict.fromkeys(topics))  # Remove duplicates, preserve order

        # Limit to 4 topics
        return topics[:4]

    except Exception as e:
        # Inference failed - fall back to heuristics
        return []


def extract_topics_heuristic(prompt: str) -> list[str]:
    """Fallback topic extraction using keyword matching."""
    topics = set()
    prompt_lower = prompt.lower()

    # Topic keywords
    topic_keywords = {
        "testing": ["test", "pytest", "unittest", "jest", "spec", "coverage"],
        "security": ["security", "auth", "password", "encryption", "vulnerability", "sql injection", "xss"],
        "performance": ["performance", "optimize", "slow", "cache", "benchmark", "speed"],
        "bug-fix": ["bug", "error", "exception", "traceback", "fix", "crash"],
        "feature": ["feature", "implement", "add", "create new", "functionality"],
        "documentation": ["document", "readme", "docs", "comment", "explain"],
        "deployment": ["deploy", "docker", "kubernetes", "production", "ci/cd"],
        "database": ["database", "sql", "query", "migration", "schema"],
        "api": ["api", "endpoint", "rest", "graphql", "request", "response"],
        "frontend": ["react", "vue", "angular", "component", "ui", "interface"],
        "backend": ["server", "backend", "service", "microservice"],
        "refactoring": ["refactor", "clean", "reorganize", "restructure"],
        "code-review": ["review", "feedback", "quality", "lint"],
    }

    for topic, keywords in topic_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            topics.add(topic)

    # Default if no topics found
    if not topics:
        topics.add("general")

    return list(topics)[:4]  # Limit to 4 topics


def store_session_topics(project_dir: str, session_id: str, topics: list[str]):
    """Store topics for this session in state directory.

    This allows PostToolUse hook to access topics without re-computing.
    """
    try:
        state_dir = Path(project_dir) / ".state" / "sessions"
        state_dir.mkdir(parents=True, exist_ok=True)

        topics_file = state_dir / f"{session_id}_topics.json"

        # Load existing topics if any
        existing_topics = []
        if topics_file.exists():
            with open(topics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_topics = data.get("topics", [])

        # Merge with new topics (preserve order, remove duplicates)
        all_topics = existing_topics + topics
        all_topics = list(dict.fromkeys(all_topics))  # Remove duplicates

        # Save
        with open(topics_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "session_id": session_id,
                    "topics": all_topics,
                    "last_updated": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

    except Exception:
        # Non-critical if storage fails
        pass


def main():
    """Main entry point for UserPromptSubmit hook."""
    try:
        input_data = json.load(sys.stdin)
        result = tag_prompt_with_local_llm(input_data)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        error_result = {
            "continue": True,
            "error": str(e),
            "message": "UACS: Tagging hook failed (non-blocking)",
        }
        print(json.dumps(error_result))
        sys.exit(0)


if __name__ == "__main__":
    main()
