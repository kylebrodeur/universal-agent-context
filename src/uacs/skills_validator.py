"""Agent Skills SKILL.md validator based on agentskills.io specification.

Validates SKILL.md files against the official Agent Skills format specification:
- YAML frontmatter validation
- Required fields: name, description
- Allowed fields: name, description, license, allowed-tools, metadata, compatibility
- Name constraints: kebab-case, max 64 chars, no leading/trailing hyphens
- Description: max 1024 chars
- Compatibility: max 500 chars
- Directory name must match skill name
"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

import yaml


@dataclass
class ValidationError:
    """A single validation error."""

    field: str
    message: str
    line: int | None = None


@dataclass
class ValidationResult:
    """Result of validating a SKILL.md file."""

    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]
    metadata: dict[str, Any] | None = None


class SkillValidator:
    """Validates Agent Skills SKILL.md files against specification.

    See https://agentskills.io/specification for full format specification.
    """

    # Field constraints from spec
    MAX_NAME_LENGTH: ClassVar[int] = 64
    MAX_DESCRIPTION_LENGTH: ClassVar[int] = 1024
    MAX_COMPATIBILITY_LENGTH: ClassVar[int] = 500

    # Allowed frontmatter fields
    ALLOWED_FIELDS: ClassVar[set[str]] = {
        "name",
        "description",
        "license",
        "allowed-tools",
        "metadata",
        "compatibility",
    }

    # Required fields
    REQUIRED_FIELDS: ClassVar[set[str]] = {"name", "description"}

    # Name pattern: lowercase letters, numbers, hyphens only
    # Must not start or end with hyphen
    NAME_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize Unicode text to NFC form."""
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def validate_name(name: str) -> list[ValidationError]:
        """Validate skill name against spec constraints.

        Constraints:
        - Max 64 characters
        - Lowercase letters, numbers, and hyphens only
        - Must not start or end with a hyphen
        - No consecutive hyphens
        - Unicode normalized (NFC)
        """
        errors = []

        if not name:
            errors.append(ValidationError("name", "Name is required"))
            return errors

        # Normalize Unicode
        normalized = SkillValidator.normalize_unicode(name)
        if name != normalized:
            errors.append(
                ValidationError(
                    "name",
                    f"Name must be Unicode normalized (NFC). "
                    f"Got: {name!r}, expected: {normalized!r}",
                )
            )

        # Length check
        if len(name) > SkillValidator.MAX_NAME_LENGTH:
            errors.append(
                ValidationError(
                    "name",
                    f"Name exceeds maximum length of {SkillValidator.MAX_NAME_LENGTH} "
                    "characters",
                )
            )

        # Pattern check (kebab-case)
        if not SkillValidator.NAME_PATTERN.match(name):
            errors.append(
                ValidationError(
                    "name",
                    "Name must contain only lowercase letters, numbers, and hyphens. "
                    "Must not start or end with a hyphen.",
                )
            )

        # Check for consecutive hyphens
        if "--" in name:
            errors.append(
                ValidationError("name", "Name must not contain consecutive hyphens")
            )

        return errors

    @staticmethod
    def validate_description(description: str) -> list[ValidationError]:
        """Validate skill description against spec constraints.

        Constraints:
        - Required
        - Max 1024 characters
        - Non-empty
        """
        errors = []

        if not description:
            errors.append(ValidationError("description", "Description is required"))
            return errors

        if not description.strip():
            errors.append(
                ValidationError("description", "Description must not be empty")
            )

        if len(description) > SkillValidator.MAX_DESCRIPTION_LENGTH:
            errors.append(
                ValidationError(
                    "description",
                    f"Description exceeds maximum length of "
                    f"{SkillValidator.MAX_DESCRIPTION_LENGTH} characters",
                )
            )

        return errors

    @staticmethod
    def validate_compatibility(compatibility: str | None) -> list[ValidationError]:
        """Validate compatibility field against spec constraints.

        Constraints:
        - Optional
        - Max 500 characters
        """
        errors = []

        if (
            compatibility
            and len(compatibility) > SkillValidator.MAX_COMPATIBILITY_LENGTH
        ):
            errors.append(
                ValidationError(
                    "compatibility",
                    f"Compatibility exceeds maximum length of "
                    f"{SkillValidator.MAX_COMPATIBILITY_LENGTH} characters",
                )
            )

        return errors

    @staticmethod
    def validate_frontmatter_fields(
        frontmatter: dict[str, Any],
    ) -> list[ValidationError]:
        """Validate that only allowed fields are present in frontmatter."""
        errors = []

        extra_fields = set(frontmatter.keys()) - SkillValidator.ALLOWED_FIELDS
        if extra_fields:
            errors.append(
                ValidationError(
                    "frontmatter",
                    f"Unexpected fields in frontmatter: "
                    f"{', '.join(sorted(extra_fields))}. "
                    f"Allowed fields: "
                    f"{', '.join(sorted(SkillValidator.ALLOWED_FIELDS))}",
                )
            )
        missing_fields = SkillValidator.REQUIRED_FIELDS - set(frontmatter.keys())
        if missing_fields:
            errors.append(
                ValidationError(
                    "frontmatter",
                    f"Missing required fields: {', '.join(sorted(missing_fields))}",
                )
            )

        return errors

    @staticmethod
    def validate_directory_name(
        skill_path: Path, skill_name: str
    ) -> list[ValidationError]:
        """Validate that directory name matches skill name.

        Directory name must match the skill name from frontmatter (kebab-case).
        """
        errors = []

        dir_name = skill_path.name
        if dir_name != skill_name:
            errors.append(
                ValidationError(
                    "directory",
                    f"Directory name '{dir_name}' does not match skill name '{skill_name}'",
                )
            )

        return errors

    @staticmethod
    def extract_frontmatter(
        content: str,
    ) -> tuple[dict[str, Any] | None, str | None, list[ValidationError]]:
        """Extract and parse YAML frontmatter from SKILL.md content.

        Returns:
            Tuple of (parsed_frontmatter, remaining_content, errors)
        """
        errors = []

        # Check for YAML frontmatter markers
        if not content.startswith("---\n"):
            errors.append(
                ValidationError(
                    "frontmatter", "SKILL.md must start with YAML frontmatter (---)"
                )
            )
            return None, content, errors

        # Find end of frontmatter
        lines = content.split("\n")
        end_marker_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_marker_idx = i
                break

        if end_marker_idx is None:
            errors.append(
                ValidationError(
                    "frontmatter",
                    "YAML frontmatter not properly closed (missing closing ---)",
                )
            )
            return None, content, errors

        # Extract frontmatter YAML
        frontmatter_text = "\n".join(lines[1:end_marker_idx])

        # Parse YAML
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                errors.append(
                    ValidationError(
                        "frontmatter",
                        "Frontmatter must be a YAML mapping (key-value pairs)",
                    )
                )
                return None, content, errors
        except yaml.YAMLError as e:
            errors.append(
                ValidationError("frontmatter", f"Invalid YAML in frontmatter: {e}")
            )
            return None, content, errors

        # Extract remaining content
        remaining = "\n".join(lines[end_marker_idx + 1 :])

        return frontmatter, remaining, errors

    @staticmethod
    def validate_file(skill_path: Path) -> ValidationResult:
        """Validate a SKILL.md file at the given path.

        Args:
            skill_path: Path to directory containing SKILL.md

        Returns:
            ValidationResult with errors, warnings, and metadata
        """
        errors = []
        warnings = []

        # Check that SKILL.md exists
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            errors.append(
                ValidationError("file", f"SKILL.md file not found in {skill_path}")
            )
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Read file content
        try:
            content = skill_file.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(ValidationError("file", f"Failed to read SKILL.md: {e}"))
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Extract and parse frontmatter
        frontmatter, body, fm_errors = SkillValidator.extract_frontmatter(content)
        errors.extend(fm_errors)

        if not frontmatter:
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Validate frontmatter fields
        errors.extend(SkillValidator.validate_frontmatter_fields(frontmatter))

        # Validate individual fields
        if "name" in frontmatter:
            errors.extend(SkillValidator.validate_name(frontmatter["name"]))

            # Validate directory name matches skill name
            errors.extend(
                SkillValidator.validate_directory_name(skill_path, frontmatter["name"])
            )

        if "description" in frontmatter:
            errors.extend(
                SkillValidator.validate_description(frontmatter["description"])
            )

        if "compatibility" in frontmatter:
            errors.extend(
                SkillValidator.validate_compatibility(frontmatter["compatibility"])
            )

        # Check for body content (warning if empty)
        if body and not body.strip():
            warnings.append(
                ValidationError(
                    "body", "SKILL.md body is empty. Consider adding instructions."
                )
            )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata=frontmatter if len(errors) == 0 else None,
        )
