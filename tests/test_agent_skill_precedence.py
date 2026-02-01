"""Tests for .agent/ and .claude/ directory precedence in AgentSkillAdapter."""

import pytest
from pathlib import Path
from uacs.adapters.agent_skill_adapter import AgentSkillAdapter


def test_agent_directory_takes_precedence_over_claude(tmp_path):
    """Test that .agent/skills/ skills take precedence over .claude/skills/ with same name."""
    # Create same skill name in both .agent/ and .claude/
    agent_dir = tmp_path / ".agent" / "skills" / "deployment"
    agent_dir.mkdir(parents=True)
    (agent_dir / "SKILL.md").write_text("""---
name: deployment
description: Agent directory version
---
# Deployment (Agent)

This is from .agent/ directory.
""")

    claude_dir = tmp_path / ".claude" / "skills" / "deployment"
    claude_dir.mkdir(parents=True)
    (claude_dir / "SKILL.md").write_text("""---
name: deployment
description: Claude directory version
---
# Deployment (Claude)

This is from .claude/ directory.
""")

    # Discover skills
    skills = AgentSkillAdapter.discover_skills(tmp_path)

    # Should only have one skill (not duplicated)
    assert len(skills) == 1

    # Should be the .agent/ version
    skill = skills[0]
    assert skill.parsed.description == "Agent directory version"
    assert "from .agent/ directory" in skill.parsed.instructions
    assert str(skill.source_directory).endswith(".agent/skills")


def test_all_four_directories_discovered(tmp_path, monkeypatch):
    """Test that skills are discovered from all four directories."""
    # Mock home directory
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    # Create skills in all four locations
    # 1. Project .agent/
    project_agent = tmp_path / ".agent" / "skills" / "skill1"
    project_agent.mkdir(parents=True)
    (project_agent / "SKILL.md").write_text("""---
name: skill1
description: From project .agent/
---
# Skill 1
Instructions from project .agent/
""")

    # 2. Home .agent/
    home_agent = fake_home / ".agent" / "skills" / "skill2"
    home_agent.mkdir(parents=True)
    (home_agent / "SKILL.md").write_text("""---
name: skill2
description: From home .agent/
---
# Skill 2
Instructions from home .agent/
""")

    # 3. Project .claude/
    project_claude = tmp_path / ".claude" / "skills" / "skill3"
    project_claude.mkdir(parents=True)
    (project_claude / "SKILL.md").write_text("""---
name: skill3
description: From project .claude/
---
# Skill 3
Instructions from project .claude/
""")

    # 4. Home .claude/
    home_claude = fake_home / ".claude" / "skills" / "skill4"
    home_claude.mkdir(parents=True)
    (home_claude / "SKILL.md").write_text("""---
name: skill4
description: From home .claude/
---
# Skill 4
Instructions from home .claude/
""")

    # Discover skills
    skills = AgentSkillAdapter.discover_skills(tmp_path)

    # Should find all 4 skills
    assert len(skills) == 4

    names = {s.parsed.name for s in skills}
    assert names == {"skill1", "skill2", "skill3", "skill4"}


def test_skill_source_metadata_tracked(tmp_path):
    """Test that skill objects track their source directory."""
    # Create skill in .agent/
    agent_dir = tmp_path / ".agent" / "skills" / "test"
    agent_dir.mkdir(parents=True)
    (agent_dir / "SKILL.md").write_text("""---
name: test
description: Test skill
---
# Test
Instructions
""")

    skills = AgentSkillAdapter.discover_skills(tmp_path)

    assert len(skills) == 1
    skill = skills[0]

    # Should have source_directory attribute
    assert hasattr(skill, 'source_directory')
    assert str(skill.source_directory).endswith(".agent/skills")


def test_precedence_order_complex(tmp_path, monkeypatch):
    """Test complex precedence scenario with skills in multiple locations."""
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    # Create "common" skill in all locations
    # Project .agent/ (should win)
    (tmp_path / ".agent" / "skills" / "common").mkdir(parents=True)
    (tmp_path / ".agent" / "skills" / "common" / "SKILL.md").write_text("""---
name: common
description: Priority 1 - Project agent
---
# Common
From project .agent/
""")

    # Home .agent/
    (fake_home / ".agent" / "skills" / "common").mkdir(parents=True)
    (fake_home / ".agent" / "skills" / "common" / "SKILL.md").write_text("""---
name: common
description: Priority 2 - Home agent
---
# Common
From home .agent/
""")

    # Project .claude/
    (tmp_path / ".claude" / "skills" / "common").mkdir(parents=True)
    (tmp_path / ".claude" / "skills" / "common" / "SKILL.md").write_text("""---
name: common
description: Priority 3 - Project claude
---
# Common
From project .claude/
""")

    # Home .claude/
    (fake_home / ".claude" / "skills" / "common").mkdir(parents=True)
    (fake_home / ".claude" / "skills" / "common" / "SKILL.md").write_text("""---
name: common
description: Priority 4 - Home claude
---
# Common
From home .claude/
""")

    skills = AgentSkillAdapter.discover_skills(tmp_path)

    # Should only have one skill
    assert len(skills) == 1

    # Should be from project .agent/ (highest priority)
    skill = skills[0]
    assert skill.parsed.description == "Priority 1 - Project agent"
    assert "From project .agent/" in skill.parsed.instructions


def test_backward_compatibility_claude_only(tmp_path):
    """Test that .claude/ directory still works for external repos."""
    # Only create .claude/ directory (no .agent/)
    claude_dir = tmp_path / ".claude" / "skills" / "external"
    claude_dir.mkdir(parents=True)
    (claude_dir / "SKILL.md").write_text("""---
name: external
description: From external repo
---
# External Skill
Imported from GitHub repo
""")

    skills = AgentSkillAdapter.discover_skills(tmp_path)

    assert len(skills) == 1
    skill = skills[0]
    assert skill.parsed.name == "external"
    assert skill.parsed.description == "From external repo"
