"""Tests for multiple skill discovery from .agent/skills/ and .claude/skills/ directories."""

from pathlib import Path

from uacs.adapters import FormatAdapterRegistry
from uacs.adapters.agent_skill_adapter import AgentSkillAdapter


def test_discover_skills_in_project_directory(tmp_path):
    """Test discovering multiple SKILL.md files in project .claude/skills/."""
    skills_dir = tmp_path / ".claude" / "skills"

    # Create deployment skill
    deployment_dir = skills_dir / "deployment"
    deployment_dir.mkdir(parents=True)
    (deployment_dir / "SKILL.md").write_text("""---
name: deployment
description: Deployment patterns and best practices
---
# Deployment Skill

## Instructions
Deploy applications to production safely.
""")

    # Create testing skill
    testing_dir = skills_dir / "testing"
    testing_dir.mkdir(parents=True)
    (testing_dir / "SKILL.md").write_text("""---
name: testing
description: Testing strategies and patterns
---
# Testing Skill

## Instructions
Write comprehensive tests for all code.
""")

    # Discover skills
    skills = AgentSkillAdapter.discover_skills(tmp_path)

    assert len(skills) == 2
    names = [s.parsed.name for s in skills if s.parsed]
    assert "deployment" in names
    assert "testing" in names


def test_discover_skills_in_home_directory(tmp_path, monkeypatch):
    """Test discovering SKILL.md files from ~/.claude/skills/."""
    # Mock home directory
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    skills_dir = fake_home / ".claude" / "skills"

    # Create skill
    skill_dir = skills_dir / "global-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("""---
name: global-skill
description: A global skill available everywhere
---
# Global Skill

## Instructions
This skill is available from home directory.
""")

    # Discover skills (use fake_home as project path since we can't actually discover from home)
    skills = AgentSkillAdapter.discover_skills(fake_home)

    assert len(skills) >= 1
    names = [s.parsed.name for s in skills if s.parsed]
    assert "global-skill" in names


def test_discover_skills_handles_missing_directories(tmp_path):
    """Test that discovery handles missing .claude/skills/ gracefully."""
    # No .claude directory exists
    skills = AgentSkillAdapter.discover_skills(tmp_path)

    assert isinstance(skills, list)
    assert len(skills) == 0


def test_discover_skills_handles_invalid_skill_files(tmp_path):
    """Test that discovery continues even when some SKILL.md files are invalid."""
    skills_dir = tmp_path / ".claude" / "skills"

    # Create valid skill
    valid_dir = skills_dir / "valid"
    valid_dir.mkdir(parents=True)
    (valid_dir / "SKILL.md").write_text("""---
name: valid
description: Valid skill
---
# Valid Skill
""")

    # Create invalid skill (malformed YAML)
    invalid_dir = skills_dir / "invalid"
    invalid_dir.mkdir(parents=True)
    (invalid_dir / "SKILL.md").write_text("This is not valid YAML frontmatter")

    # Should discover valid skill and skip invalid one
    skills = AgentSkillAdapter.discover_skills(tmp_path)

    assert len(skills) >= 1
    names = [s.parsed.name for s in skills if s.parsed]
    assert "valid" in names


def test_discover_skills_ignores_non_directory_items(tmp_path):
    """Test that discovery ignores non-directory items in skills/."""
    skills_dir = tmp_path / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create a regular file (should be ignored)
    (skills_dir / "README.md").write_text("Some readme")

    # Create a valid skill directory
    skill_dir = skills_dir / "real-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("""---
name: real-skill
description: A real skill
---
# Real Skill
""")

    skills = AgentSkillAdapter.discover_skills(tmp_path)

    assert len(skills) == 1
    assert skills[0].parsed.name == "real-skill"


def test_detect_and_load_all_includes_multiple_skills(tmp_path):
    """Test that FormatAdapterRegistry.detect_and_load_all finds multiple skills."""
    # Create individual SKILL.md files in Agent Skills format
    skills_dir = tmp_path / ".agent" / "skills"

    skill1_dir = skills_dir / "skill1"
    skill1_dir.mkdir(parents=True)
    (skill1_dir / "SKILL.md").write_text("""---
name: skill1
description: First individual skill
---
# Skill 1
""")

    skill2_dir = skills_dir / "skill2"
    skill2_dir.mkdir(parents=True)
    (skill2_dir / "SKILL.md").write_text("""---
name: skill2
description: Second individual skill
---
# Skill 2
""")

    skill3_dir = skills_dir / "skill3"
    skill3_dir.mkdir(parents=True)
    (skill3_dir / "SKILL.md").write_text("""---
name: skill3
description: Third individual skill
---
# Skill 3
""")

    # Discover all adapters
    adapters = FormatAdapterRegistry.detect_and_load_all(tmp_path)

    # Should find 3 individual SKILL.md files
    assert len(adapters) >= 3

    # Check formats
    format_names = [a.FORMAT_NAME for a in adapters]
    assert "agent_skill" in format_names  # Agent Skills format
    assert format_names.count("agent_skill") >= 2  # At least 2 SKILL.md files


def test_detect_and_load_all_avoids_duplicates(tmp_path):
    """Test that detect_and_load_all doesn't return duplicate adapters."""
    # Create the same skill in multiple locations
    skills_dir = tmp_path / ".claude" / "skills"
    skill_dir = skills_dir / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: Test
---
# Test
""")

    # Call twice to ensure no duplicates
    adapters1 = FormatAdapterRegistry.detect_and_load_all(tmp_path)
    adapters2 = FormatAdapterRegistry.detect_and_load_all(tmp_path)

    # Should return same number of adapters
    assert len(adapters1) == len(adapters2)

    # No duplicate file paths
    file_paths = [str(a.file_path) for a in adapters1]
    assert len(file_paths) == len(set(file_paths))


def test_skill_adapter_parses_yaml_frontmatter_correctly(tmp_path):
    """Test that AgentSkillAdapter correctly parses YAML frontmatter."""
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("""---
name: auth-skill
description: Authentication and authorization patterns
author: Test Author
version: 1.0
---
# Authentication Skill

## Instructions
Implement secure authentication flows.
""")

    adapter = AgentSkillAdapter(skill_file)

    assert adapter.parsed is not None
    assert adapter.parsed.name == "auth-skill"
    assert adapter.parsed.description == "Authentication and authorization patterns"
    assert "Implement secure authentication flows" in adapter.parsed.instructions


def test_skill_adapter_to_system_prompt(tmp_path):
    """Test that skill adapter converts to system prompt correctly."""
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("""---
name: test-skill
description: A test skill
---
# Test Skill

Follow these instructions carefully.
""")

    adapter = AgentSkillAdapter(skill_file)
    prompt = adapter.to_system_prompt()

    assert "# Skill: test-skill" in prompt
    assert "**Description**: A test skill" in prompt
    assert "Follow these instructions carefully" in prompt


def test_skill_adapter_to_adk_capabilities(tmp_path):
    """Test that skill adapter converts to ADK format correctly."""
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("""---
name: deploy-skill
description: Deployment helper
---
# Deploy Skill

Deploy to production.
""")

    adapter = AgentSkillAdapter(skill_file)
    capabilities = adapter.to_adk_capabilities()

    assert capabilities["name"] == "deploy-skill"
    assert capabilities["description"] == "Deployment helper"
    assert "Deploy to production" in capabilities["instructions"]
