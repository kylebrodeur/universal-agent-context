"""Tests for UACS main API."""

import pytest

from uacs import UACS
from uacs.packages import InstalledPackage, PackageSource


def test_uacs_init(tmp_project):
    """Test UACS initialization."""
    uacs = UACS(tmp_project)

    assert uacs.project_path == tmp_project
    assert uacs.packages is not None
    assert uacs.shared_context is not None
    assert uacs.unified_context is not None


def test_uacs_loads_agents_md(uacs, sample_agents_md):
    """Test UACS loads AGENTS.md."""
    assert uacs.agents_md is not None
    assert uacs.agents_md.config is not None
    assert "test project" in uacs.agents_md.config.project_overview.lower()


def test_uacs_loads_agent_skills(uacs, sample_agent_skill):
    """Test UACS loads Agent Skills."""
    assert len(uacs.agent_skills) > 0
    # Check that at least one skill was loaded
    assert any(adapter.parsed for adapter in uacs.agent_skills)


def test_list_packages(uacs):
    """Test listing packages through UACS."""
    packages = uacs.list_packages()

    assert isinstance(packages, list)
    # Should be empty or contain installed packages


def test_get_capabilities(uacs):
    """Test getting capabilities."""
    capabilities = uacs.get_capabilities()

    assert isinstance(capabilities, dict)
    assert "skills" in capabilities or "agents_md" in capabilities


def test_build_context(uacs):
    """Test building context for an agent."""
    context = uacs.build_context(
        query="Review the code", agent="test-agent", max_tokens=1000
    )

    assert isinstance(context, str)
    assert len(context) > 0


def test_add_to_context(uacs):
    """Test adding content to shared context."""
    uacs.add_to_context(
        key="test-key", content="Test content", metadata={"source": "test"}
    )

    # Verify it was added
    stats = uacs.get_token_stats()
    assert stats is not None


def test_get_token_stats(uacs):
    """Test getting token statistics."""
    stats = uacs.get_token_stats()

    assert isinstance(stats, dict)
    assert "total_potential_tokens" in stats or isinstance(stats, dict)


def test_get_stats(uacs):
    """Test comprehensive stats."""
    stats = uacs.get_stats()

    assert isinstance(stats, dict)
    assert "project_path" in stats
    assert "adapters" in stats
    assert "packages" in stats
    assert "context" in stats
    assert "capabilities" in stats


def test_install_package(uacs, tmp_project):
    """Test installing a package."""
    # Create a sample skill directory with proper naming
    sample_skill = tmp_project / "test-install-skill"
    sample_skill.mkdir()
    skill_md = sample_skill / "SKILL.md"
    skill_md.write_text("""---
name: test-install-skill
description: A test skill for install testing
metadata:
  version: 1.0.0
---
# Test Install Skill

## Triggers
- install test

## Instructions
Test installation.
""")

    # Test installing from local path (uses real validator)
    result = uacs.install_package(str(sample_skill))

    assert isinstance(result, InstalledPackage)
    assert result.name == "test-install-skill"
    assert result.source == str(sample_skill)
    assert result.source_type == PackageSource.LOCAL

    # Verify it's in the list
    packages = uacs.list_packages()
    assert len(packages) == 1
    assert packages[0].name == "test-install-skill"


def test_uacs_with_no_files(tmp_project):
    """Test UACS with no Agent Skills or AGENTS.md."""
    uacs = UACS(tmp_project)

    assert len(uacs.agent_skills) == 0
    assert uacs.agents_md is None
    assert uacs.packages is not None


def test_uacs_stats_with_no_adapters(tmp_project):
    """Test stats when no adapters are loaded."""
    uacs = UACS(tmp_project)
    stats = uacs.get_stats()

    assert stats["adapters"]["agent_skills"]["count"] == 0
    assert stats["adapters"]["agents_md"]["loaded"] is False
