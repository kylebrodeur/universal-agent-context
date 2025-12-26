"""Adapter for Agent Skills SKILL.md format (individual skill files).

Supports both .agent/ (recommended) and .claude/ (for importing external repos) directories.
See https://agentskills.io for the vendor-neutral format specification.
"""

import re
from pathlib import Path
from typing import Any

from .base import BaseFormatAdapter, FormatAdapterRegistry, ParsedContent


@FormatAdapterRegistry.register
class AgentSkillAdapter(BaseFormatAdapter):
    """Agent Skills SKILL.md format adapter.

    Supports the vendor-neutral Agent Skills format with YAML frontmatter:
    ```
    ---
    name: skill-name
    description: Brief description
    ---
    # skill-name

    ## Instructions
    ...
    ```

    See https://agentskills.io for full specification.
    """

    FORMAT_NAME = "agent_skill"
    SUPPORTED_FILES = ["SKILL.md"]

    source_directory: str | None = None

    def parse(self, content: str) -> ParsedContent:
        """Parse Claude Code SKILL.md format.

        Args:
            content: Raw SKILL.md content

        Returns:
            ParsedContent with skill metadata and instructions
        """
        # Parse YAML frontmatter
        metadata = {}
        instructions = content

        # Check for YAML frontmatter (--- ... ---)
        yaml_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(yaml_pattern, content, re.DOTALL)

        if match:
            yaml_content = match.group(1)
            instructions = match.group(2)

            # Parse simple YAML (key: value pairs)
            for line in yaml_content.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

        return ParsedContent(
            name=metadata.get("name", "unnamed-skill"),
            description=metadata.get("description", ""),
            instructions=instructions.strip(),
            metadata=metadata,
            triggers=self._extract_triggers(instructions),
        )

    def _extract_triggers(self, content: str) -> list[str]:
        """Extract triggers from markdown content."""
        triggers = []

        # Look for ## Triggers section
        trigger_section = re.search(
            r"##\s+Triggers\s*\n(.*?)(?:\n##|$)", content, re.DOTALL | re.IGNORECASE
        )
        if trigger_section:
            section_content = trigger_section.group(1)
            # Extract list items
            for line in section_content.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    triggers.append(line[2:].strip())

        return triggers

    def to_system_prompt(self) -> str:
        """Convert to system prompt.

        Returns:
            Formatted system prompt
        """
        if not self.parsed:
            return ""

        prompt_parts = [
            f"# Skill: {self.parsed.name}",
            "",
            f"**Description**: {self.parsed.description}",
            "",
            "## Instructions",
            self.parsed.instructions,
        ]

        return "\n".join(prompt_parts)

    def to_adk_capabilities(self) -> dict[str, Any]:
        """Convert to ADK capability format.

        Returns:
            ADK capability dictionary
        """
        if not self.parsed:
            return {}

        return {
            "name": self.parsed.name,
            "description": self.parsed.description,
            "instructions": self.parsed.instructions,
            "metadata": self.parsed.metadata,
        }

    @classmethod
    def discover_skills(cls, project_path: Path) -> list["AgentSkillAdapter"]:
        """Discover all SKILL.md files in project and personal directories.

        Searches multiple directories with precedence:
        1. project_path/.agent/skills/*/SKILL.md (highest priority)
        2. ~/.agent/skills/*/SKILL.md
        3. project_path/.claude/skills/*/SKILL.md
        4. ~/.claude/skills/*/SKILL.md (lowest priority)

        When duplicate skill names exist, .agent/ versions take precedence.
        The .claude/ directory is supported for importing external skill repos.

        Returns:
            List of skill adapters, deduplicated by skill name
        """
        skills_by_name = {}  # Use dict to handle deduplication

        # Search in precedence order (higher priority first)
        search_paths = [
            project_path / ".agent" / "skills",
            Path.home() / ".agent" / "skills",
            project_path / ".claude" / "skills",
            Path.home() / ".claude" / "skills",
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            # Find all SKILL.md files in subdirectories
            for skill_dir in search_path.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    try:
                        adapter = cls(skill_file)
                        skill_name = (
                            adapter.parsed.name if adapter.parsed else skill_dir.name
                        )

                        # Only add if not already found (precedence: earlier paths win)
                        if skill_name not in skills_by_name:
                            # Track source directory for metadata
                            adapter.source_directory = str(search_path)
                            skills_by_name[skill_name] = adapter
                    except Exception as e:
                        # Log warning but continue discovering other skills
                        print(f"Warning: Failed to load {skill_file}: {e}")

        return list(skills_by_name.values())

    def find_skill_by_trigger(self, query: str) -> bool:
        """Check if this skill matches a query trigger.

        Args:
            query: Query string to match against triggers

        Returns:
            True if any trigger matches the query
        """
        if not self.parsed or not hasattr(self.parsed, "triggers"):
            return False

        query_lower = query.lower()
        for trigger in self.parsed.triggers:
            if trigger.lower() in query_lower or query_lower in trigger.lower():
                return True

        return False


__all__ = ["AgentSkillAdapter"]
