"""Test fixtures for UACS tests."""

import pytest

from uacs import UACS


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    return tmp_path


@pytest.fixture
def sample_agents_md(tmp_project):
    """Create a sample AGENTS.md file."""
    agents_md = tmp_project / "AGENTS.md"
    agents_md.write_text("""# Test Project

## Project Overview
This is a test project for multi-agent CLI.

## Setup Commands
- `uv sync`
- `uv run pytest`

## Code Style
- Use Python 3.11+
- Follow PEP 8
- Use type hints

## Testing Instructions
- Run all tests: `pytest tests/`
- With coverage: `pytest --cov=src`
""")
    return agents_md


@pytest.fixture
def sample_agent_skill(tmp_project):
    """Create a sample Agent Skill (SKILL.md)."""
    skill_dir = tmp_project / ".agent" / "skills" / "test-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("""---
name: test-skill
description: A test skill
---
# Test Skill

## Triggers
- test trigger
- run test

## Instructions
Run the test skill.
""")
    return skill_file


@pytest.fixture
def uacs(tmp_project, sample_agents_md, sample_agent_skill):
    """Create UACS instance with sample files."""
    return UACS(tmp_project)
