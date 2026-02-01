"""Tests for format adapters."""

from pathlib import Path

from uacs.adapters import (
    AgentSkillAdapter,
    AgentsMDAdapter,
    CursorRulesAdapter,
    FormatAdapterRegistry,
)


def test_format_adapter_registry_list():
    """Test listing registered formats."""
    formats = FormatAdapterRegistry.list_formats()

    assert "agents_md" in formats
    assert "cursorrules" in formats
    assert "agent_skill" in formats


def test_agents_md_adapter_loads_file(sample_agents_md):
    """Test AgentsMDAdapter loads AGENTS.md."""
    adapter = AgentsMDAdapter(sample_agents_md)

    assert adapter.exists()
    assert adapter.config is not None


def test_agents_md_adapter_parses_sections(sample_agents_md):
    """Test AgentsMDAdapter parses sections."""
    adapter = AgentsMDAdapter(sample_agents_md)

    assert "test project" in adapter.config.project_overview.lower()
    assert len(adapter.config.setup_commands) > 0
    assert len(adapter.config.code_style) > 0


def test_agents_md_adapter_to_system_prompt(sample_agents_md):
    """Test converting AGENTS.md to system prompt."""
    adapter = AgentsMDAdapter(sample_agents_md)
    prompt = adapter.to_system_prompt()

    assert "Project Context" in prompt or "Test Project" in prompt
    assert len(prompt) > 0


def test_cursor_rules_adapter(tmp_project):
    """Test CursorRulesAdapter."""
    cursorrules = tmp_project / ".cursorrules"
    cursorrules.write_text("Always use type hints\nFollow PEP 8")

    adapter = CursorRulesAdapter(cursorrules)

    assert adapter.exists()
    assert adapter.parsed.rules != ""

    prompt = adapter.to_system_prompt()
    assert "PROJECT RULES" in prompt


def test_agent_skill_adapter(sample_agent_skill):
    """Test AgentSkillAdapter with YAML frontmatter."""
    adapter = AgentSkillAdapter(sample_agent_skill)

    assert adapter.exists()
    assert adapter.parsed.name == "test-skill"
    assert adapter.parsed.description == "A test skill"
    assert "Instructions" in adapter.parsed.instructions


def test_format_adapter_registry_detect(tmp_project, sample_agents_md):
    """Test auto-detecting format."""
    adapter = FormatAdapterRegistry.detect_and_load(tmp_project)

    assert adapter is not None
    assert adapter.FORMAT_NAME in ["agents_md", "agent_skill"]


def test_format_adapter_registry_detect_all(
    tmp_project, sample_agents_md, sample_agent_skill
):
    """Test detecting all adapters."""
    adapters = FormatAdapterRegistry.detect_and_load_all(tmp_project)

    assert len(adapters) >= 2  # Should find both AGENTS.md and SKILL.md
    format_names = [a.FORMAT_NAME for a in adapters]
    assert "agents_md" in format_names
    assert "agent_skill" in format_names


def test_agents_md_adapter_to_adk_capabilities(sample_agents_md):
    """Test converting AGENTS.md to ADK capabilities."""
    adapter = AgentsMDAdapter(sample_agents_md)
    capabilities = adapter.to_adk_capabilities()

    assert isinstance(capabilities, dict)
    assert "project_context" in capabilities
    assert "code_style" in capabilities


def test_adapter_supports_file():
    """Test checking if adapter supports a file."""
    assert AgentsMDAdapter.supports_file(Path("AGENTS.md"))
    assert CursorRulesAdapter.supports_file(Path(".cursorrules"))
