"""Data models for package management."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class PackageSource(Enum):
    """Source type for package installation."""

    GITHUB = "github"  # owner/repo format
    GIT_URL = "git_url"  # Full git URL
    LOCAL = "local"  # Local filesystem path
    UNKNOWN = "unknown"


@dataclass
class InstalledPackage:
    """Represents an installed package in .agent/skills/"""

    name: str
    source: str  # Original source string (e.g., "owner/repo")
    source_type: PackageSource
    version: str | None = None
    install_date: datetime = field(default_factory=datetime.now)
    location: Path | None = None
    is_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "source": self.source,
            "source_type": self.source_type.value,
            "version": self.version,
            "install_date": self.install_date.isoformat(),
            "location": str(self.location) if self.location else None,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InstalledPackage":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            source=data["source"],
            source_type=PackageSource(data["source_type"]),
            version=data.get("version"),
            install_date=datetime.fromisoformat(data["install_date"]),
            location=Path(data["location"]) if data.get("location") else None,
            is_valid=data.get("is_valid", True),
            validation_errors=data.get("validation_errors", []),
            metadata=data.get("metadata", {}),
        )
