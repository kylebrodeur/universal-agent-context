"""Adapter for AGENTS.md specification support.

This module parses AGENTS.md files (the open standard for AI agent instructions)
and converts them to A2A/ADK-compatible agent capabilities. The adapter follows
the AGENTS.md specification and integrates with the Agent Development Kit (ADK)
and Agent-to-Agent (A2A) protocol.

Spec: https://agents.md/
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .base import BaseFormatAdapter, FormatAdapterRegistry, ParsedContent


@dataclass
class AgentsMDSection:
    """Represents a parsed section from AGENTS.md.

    Attributes:
        title: Section title/heading text.
        content: Section body content as markdown.
        level: Heading level (1 for #, 2 for ##, etc.).
        subsections: Nested child sections.
    """

    title: str
    content: str
    level: int
    subsections: list["AgentsMDSection"]


@dataclass
class AgentsMDConfig:
    """Parsed AGENTS.md configuration.

    Attributes:
        project_overview: High-level project description and context.
        setup_commands: Commands for project setup/installation.
        dev_environment_tips: Development environment recommendations.
        code_style: Code style guidelines and conventions.
        build_commands: Commands for building the project.
        testing_instructions: How to run tests and validation.
        security_considerations: Security guidelines and best practices.
        pr_instructions: Pull request guidelines and workflow.
        custom_sections: Additional custom sections not in the standard spec.
    """

    project_overview: str
    setup_commands: list[str]
    dev_environment_tips: list[str]
    code_style: list[str]
    build_commands: list[str]
    testing_instructions: list[str]
    security_considerations: list[str]
    pr_instructions: list[str]
    custom_sections: dict[str, str]


@FormatAdapterRegistry.register
class AgentsMDAdapter(BaseFormatAdapter):
    """Adapter for parsing and using AGENTS.md files.

    This adapter implements support for the AGENTS.md specification, which provides
    a standardized way to document project context and guidelines for AI agents.
    It parses AGENTS.md files and converts them to A2A/ADK-compatible capabilities.
    """

    FORMAT_NAME = "agents_md"
    SUPPORTED_FILES = ["AGENTS.md"]

    def __init__(self, file_path: Path | None):
        """Initialize AGENTS.md adapter.

        Args:
            file_path: Path to AGENTS.md file
        """
        # Call parent init which will parse the content
        super().__init__(file_path)

        # Store parsed config for backward compatibility
        self.config: AgentsMDConfig | None = None
        if self.parsed:
            self.config = self.parsed.to_dict().get("config")

        # For backward compatibility
        self.project_root = file_path.parent if file_path else None
        self.agents_md_path = file_path

    def parse(self, content: str) -> ParsedContent:
        """Parse AGENTS.md content (required by base class).

        Args:
            content: Raw AGENTS.md content

        Returns:
            ParsedContent with parsed configuration
        """
        config = self._parse_agents_md_content(content)
        return ParsedContent(config=config)

    def _parse_agents_md_content(self, content: str) -> AgentsMDConfig:
        """Parse AGENTS.md file into structured config.

        Extracts standard sections (overview, setup, code style, etc.) and
        custom sections from the AGENTS.md file into a structured configuration.

        Args:
            content: Raw AGENTS.md content

        Returns:
            Parsed AgentsMDConfig
        """

        # Initialize config with defaults
        config = AgentsMDConfig(
            project_overview="",
            setup_commands=[],
            dev_environment_tips=[],
            code_style=[],
            build_commands=[],
            testing_instructions=[],
            security_considerations=[],
            pr_instructions=[],
            custom_sections={},
        )

        # Parse sections
        sections = self._parse_sections(content)

        for section in sections:
            title_lower = section.title.lower()

            if "overview" in title_lower or "project" in title_lower:
                config.project_overview = section.content.strip()
            elif "setup" in title_lower:
                config.setup_commands = self._extract_commands(section.content)
            elif "dev" in title_lower or "environment" in title_lower:
                config.dev_environment_tips = self._extract_bullets(section.content)
            elif "style" in title_lower or "code" in title_lower:
                config.code_style = self._extract_bullets(section.content)
            elif "build" in title_lower:
                config.build_commands = self._extract_commands(section.content)
            elif "test" in title_lower:
                config.testing_instructions = self._extract_bullets(section.content)
            elif "security" in title_lower:
                config.security_considerations = self._extract_bullets(section.content)
            elif "pr" in title_lower or "pull request" in title_lower:
                config.pr_instructions = self._extract_bullets(section.content)
            else:
                # Custom section
                config.custom_sections[section.title] = section.content.strip()

        return config

    def _parse_sections(self, content: str) -> list[AgentsMDSection]:
        """Parse markdown sections.

        Identifies markdown headers (# ## ###) and groups content into
        hierarchical sections with their heading levels preserved.

        Args:
            content: Markdown content

        Returns:
            List of parsed sections
        """
        sections = []
        lines = content.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            # Check for section header
            if line.startswith("#"):
                # Save previous section
                if current_section:
                    current_section.content = "\n".join(current_content)
                    sections.append(current_section)

                # Parse new section
                level = len(re.match(r"^#+", line).group())
                title = line.lstrip("#").strip()

                current_section = AgentsMDSection(
                    title=title, content="", level=level, subsections=[]
                )
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            current_section.content = "\n".join(current_content)
            sections.append(current_section)

        return sections

    def _extract_commands(self, content: str) -> list[str]:
        """Extract command strings from content.

        Finds commands in inline code (`command`) and code blocks,
        typically used for setup, build, and test commands.

        Args:
            content: Section content

        Returns:
            List of command strings
        """
        commands = []

        # Extract from code blocks
        code_blocks = re.findall(r"`([^`]+)`", content)
        commands.extend(code_blocks)

        # Extract from bullets with code
        bullets = re.findall(r"^\s*[-*]\s+.*?`([^`]+)`", content, re.MULTILINE)
        commands.extend(bullets)

        return commands

    def _extract_bullets(self, content: str) -> list[str]:
        """Extract bullet points from content.

        Parses markdown list items (- or *) from the content,
        commonly used for guidelines and recommendations.

        Args:
            content: Section content

        Returns:
            List of bullet point strings
        """
        bullets = []

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                bullets.append(line[1:].strip())

        return bullets

    def to_system_prompt(self) -> str:
        """Convert AGENTS.md to system prompt for agents.

        Returns:
            Formatted system prompt string
        """
        if not self.config:
            return ""

        prompt_parts = []

        if self.config.project_overview:
            prompt_parts.append(f"# Project Context\n\n{self.config.project_overview}")

        if self.config.setup_commands:
            prompt_parts.append("\n## Setup Commands\n")
            for cmd in self.config.setup_commands:
                prompt_parts.append(f"- `{cmd}`")

        if self.config.code_style:
            prompt_parts.append("\n## Code Style Rules\n")
            for rule in self.config.code_style:
                prompt_parts.append(f"- {rule}")

        if self.config.build_commands:
            prompt_parts.append("\n## Build Commands\n")
            for cmd in self.config.build_commands:
                prompt_parts.append(f"- `{cmd}`")

        if self.config.testing_instructions:
            prompt_parts.append("\n## Testing Instructions\n")
            for instruction in self.config.testing_instructions:
                prompt_parts.append(f"- {instruction}")

        if self.config.pr_instructions:
            prompt_parts.append("\n## PR Guidelines\n")
            for instruction in self.config.pr_instructions:
                prompt_parts.append(f"- {instruction}")

        return "\n".join(prompt_parts)

    def to_adk_capabilities(self) -> dict:
        """Convert AGENTS.md to ADK capabilities format.

        Transforms the parsed AGENTS.md configuration into the capability
        format expected by the Agent Development Kit (ADK) and A2A protocol.

        Returns:
            ADK capabilities dictionary with project context and guidelines.
        """
        if not self.config:
            return {}

        return {
            "project_context": self.config.project_overview,
            "setup": self.config.setup_commands,
            "development": self.config.dev_environment_tips,
            "code_style": self.config.code_style,
            "build": self.config.build_commands,
            "testing": self.config.testing_instructions,
            "security": self.config.security_considerations,
            "pr_guidelines": self.config.pr_instructions,
            "custom": self.config.custom_sections,
        }

    def merge_with_skills(self, skills_prompt: str) -> str:
        """Merge AGENTS.md context with SKILLS.md prompt.

        Args:
            skills_prompt: Existing skills-based prompt

        Returns:
            Combined prompt with both contexts
        """
        agents_prompt = self.to_system_prompt()

        if not agents_prompt:
            return skills_prompt

        return f"""{agents_prompt}

---

{skills_prompt}
"""
