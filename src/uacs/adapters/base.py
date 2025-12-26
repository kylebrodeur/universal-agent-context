"""Base adapter class for format translation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Skill:
    """Skill information."""

    name: str
    instructions: str
    triggers: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
    examples: list[str] = field(default_factory=list)


class ParsedContent:
    """Parsed content from format."""

    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    metadata: dict[str, Any] | None = None
    rules: str | None = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        # Set attributes from kwargs for type safety
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.__dict__

    def __repr__(self) -> str:
        return f"ParsedContent({self.__dict__})"


class BaseFormatAdapter(ABC):
    """Base class for all format adapters."""

    FORMAT_NAME: str = "base"
    SUPPORTED_FILES: list[str] = []

    def __init__(self, file_path: Path | None):
        self.file_path = file_path
        self.content = file_path.read_text() if file_path and file_path.exists() else ""
        self.parsed = self.parse(self.content) if self.content else None

    @abstractmethod
    def parse(self, content: str) -> ParsedContent:
        """Parse format-specific content.

        Args:
            content: Raw file content

        Returns:
            Parsed content object
        """
        pass

    @abstractmethod
    def to_system_prompt(self) -> str:
        """Convert to system prompt format.

        Returns:
            Formatted system prompt string
        """
        pass

    def to_adk_capabilities(self) -> dict[str, Any]:
        """Convert to ADK agent card format (optional).

        Returns:
            ADK capabilities dictionary
        """
        return {}

    def exists(self) -> bool:
        """Check if file exists.

        Returns:
            True if file exists
        """
        return self.file_path and self.file_path.exists()

    def get_stats(self) -> dict[str, Any]:
        """Get adapter statistics.

        Returns:
            Dictionary with adapter stats
        """
        return {
            "format": self.FORMAT_NAME,
            "file": str(self.file_path),
            "exists": self.exists(),
            "size": len(self.content),
            "parsed": self.parsed.to_dict() if self.parsed else None,
        }

    def find_skill_by_trigger(self, query: str) -> Skill | None:
        """Find skill that matches query trigger.

        Default implementation: no matching.
        Subclasses can override for trigger-based matching.

        Args:
            query: User query to match against triggers

        Returns:
            Matching skill or None
        """
        return None

    @classmethod
    def supports_file(cls, file_path: Path) -> bool:
        """Check if this adapter supports the file.

        Args:
            file_path: Path to check

        Returns:
            True if adapter supports this file
        """
        return file_path.name in cls.SUPPORTED_FILES


class FormatAdapterRegistry:
    """Registry for format adapters."""

    _adapters: dict[str, type["BaseFormatAdapter"]] = {}

    @classmethod
    def register(
        cls, adapter_class: type["BaseFormatAdapter"]
    ) -> type["BaseFormatAdapter"]:
        """Register adapter class.

        Args:
            adapter_class: Adapter class to register

        Returns:
            The adapter class (for decorator usage)
        """
        cls._adapters[adapter_class.FORMAT_NAME] = adapter_class
        return adapter_class

    @classmethod
    def detect_and_load(
        cls, project_path: Path, search_parents: bool = True
    ) -> BaseFormatAdapter | None:
        """Auto-detect format and return adapter.

        Searches for supported files in:
        1. Project directory (project-specific config)
        2. Parent directories up to root (following AGENTS.md spec)
        3. User home directory (personal/global config)

        Args:
            project_path: Path to project directory
            search_parents: Whether to search parent directories

        Returns:
            Adapter instance or None if no format detected
        """
        search_paths = [project_path]

        # Add parent directories
        if search_parents:
            current = project_path
            while current != current.parent:
                current = current.parent
                search_paths.append(current)

        # Add user home directory for personal skills
        home_config_paths = [
            Path.home() / ".claude",  # Claude Code personal skills
            Path.home() / ".config" / "multi-agent-cli",  # Our tool's config
        ]
        search_paths.extend(home_config_paths)

        # Search all paths for supported files
        for adapter_class in cls._adapters.values():
            for filename in adapter_class.SUPPORTED_FILES:
                for search_path in search_paths:
                    file_path = search_path / filename
                    if file_path.exists():
                        return adapter_class(file_path)

        return None

    @classmethod
    def detect_and_load_all(cls, project_path: Path) -> list[BaseFormatAdapter]:
        """Detect and load all available format adapters.

        Finds all supported files in project and personal directories.
        Also discovers multiple SKILL.md files from .claude/skills/*

        Args:
            project_path: Path to project directory

        Returns:
            List of adapter instances
        """
        adapters = []
        found_files = set()

        search_paths = [
            project_path,
            Path.home() / ".claude",
            Path.home() / ".config" / "multi-agent-cli",
        ]

        for adapter_class in cls._adapters.values():
            for filename in adapter_class.SUPPORTED_FILES:
                for search_path in search_paths:
                    file_path = search_path / filename
                    if file_path.exists() and str(file_path) not in found_files:
                        adapters.append(adapter_class(file_path))
                        found_files.add(str(file_path))

        # Special case: Discover multiple SKILL.md files from .agent/skills/* and .claude/skills/*
        from .agent_skill_adapter import AgentSkillAdapter

        agent_skills = AgentSkillAdapter.discover_skills(project_path)
        for skill in agent_skills:
            if str(skill.file_path) not in found_files:
                adapters.append(skill)
                found_files.add(str(skill.file_path))

        return adapters

    @classmethod
    def list_formats(cls) -> list[str]:
        """List registered formats.

        Returns:
            List of format names
        """
        return list(cls._adapters.keys())

    @classmethod
    def get_adapter(cls, format_name: str) -> type | None:
        """Get adapter class by format name.

        Args:
            format_name: Name of the format

        Returns:
            Adapter class or None if not found
        """
        return cls._adapters.get(format_name)


__all__ = ["BaseFormatAdapter", "FormatAdapterRegistry", "ParsedContent", "Skill"]
