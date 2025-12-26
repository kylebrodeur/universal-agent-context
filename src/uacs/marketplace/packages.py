"""Package dataclasses for marketplace items."""

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Package:
    """Base package class for marketplace items."""

    name: str
    description: str
    source: str  # 'smithery', 'github', etc.
    package_type: Literal["skill", "mcp"]
    url: str
    version: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Get package ID (name)."""
        return self.name

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "type": self.package_type,
            "url": self.url,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass
class SkillPackage(Package):
    """Skill package from GitHub or other source."""

    triggers: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    instructions: str = ""

    def __post_init__(self):
        """Ensure package_type is set correctly."""
        self.package_type = "skill"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update(
            {
                "triggers": self.triggers,
                "files": self.files,
                "instructions": self.instructions,
            }
        )
        return data


@dataclass
class MCPPackage(Package):
    """MCP server package."""

    tools: list[str] = field(default_factory=list)
    protocol_version: str = "1.0"
    install_command: str = ""
    config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure package_type is set correctly."""
        self.package_type = "mcp"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data.update(
            {
                "tools": self.tools,
                "protocol_version": self.protocol_version,
                "install_command": self.install_command,
                "config": self.config,
            }
        )
        return data


__all__ = ["MCPPackage", "Package", "SkillPackage"]
