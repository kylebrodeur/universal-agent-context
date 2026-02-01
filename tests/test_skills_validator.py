"""Tests for Agent Skills SKILL.md validator."""

import pytest
from pathlib import Path
from uacs.skills_validator import SkillValidator, ValidationError


class TestSkillValidator:
    """Test suite for SkillValidator."""

    def test_validate_name_valid(self):
        """Test valid skill names."""
        valid_names = [
            "pdf-processing",
            "python-test",
            "code-review",
            "api-integration",
            "my-skill-123",
            "a",  # Single character
            "abc123",  # No hyphens
        ]

        for name in valid_names:
            errors = SkillValidator.validate_name(name)
            assert len(errors) == 0, f"Expected {name!r} to be valid, got errors: {errors}"

    def test_validate_name_invalid_format(self):
        """Test invalid skill name formats."""
        invalid_names = [
            "PDF-Processing",  # Uppercase
            "pdf_processing",  # Underscore
            "-pdf-processing",  # Leading hyphen
            "pdf-processing-",  # Trailing hyphen
            "pdf--processing",  # Consecutive hyphens
            "pdf.processing",  # Period
            "pdf processing",  # Space
            "café",  # Non-ASCII
        ]

        for name in invalid_names:
            errors = SkillValidator.validate_name(name)
            assert len(errors) > 0, f"Expected {name!r} to be invalid"

    def test_validate_name_too_long(self):
        """Test name exceeds maximum length."""
        name = "a" * 65  # 65 characters
        errors = SkillValidator.validate_name(name)
        assert any("maximum length" in e.message for e in errors)

    def test_validate_name_empty(self):
        """Test empty name."""
        errors = SkillValidator.validate_name("")
        assert any("required" in e.message.lower() for e in errors)

    def test_validate_description_valid(self):
        """Test valid description."""
        desc = "Extract text and tables from PDF files"
        errors = SkillValidator.validate_description(desc)
        assert len(errors) == 0

    def test_validate_description_empty(self):
        """Test empty description."""
        errors = SkillValidator.validate_description("")
        assert any("required" in e.message.lower() for e in errors)

    def test_validate_description_whitespace_only(self):
        """Test description with only whitespace."""
        errors = SkillValidator.validate_description("   \n\t  ")
        assert any("empty" in e.message.lower() for e in errors)

    def test_validate_description_too_long(self):
        """Test description exceeds maximum length."""
        desc = "a" * 1025  # 1025 characters
        errors = SkillValidator.validate_description(desc)
        assert any("maximum length" in e.message for e in errors)

    def test_validate_compatibility_valid(self):
        """Test valid compatibility field."""
        compat = "Requires Python 3.8+ and pdfplumber package"
        errors = SkillValidator.validate_compatibility(compat)
        assert len(errors) == 0

    def test_validate_compatibility_too_long(self):
        """Test compatibility exceeds maximum length."""
        compat = "a" * 501  # 501 characters
        errors = SkillValidator.validate_compatibility(compat)
        assert any("maximum length" in e.message for e in errors)

    def test_validate_compatibility_none(self):
        """Test compatibility field is optional."""
        errors = SkillValidator.validate_compatibility(None)
        assert len(errors) == 0

    def test_validate_frontmatter_fields_valid(self):
        """Test valid frontmatter with all allowed fields."""
        frontmatter = {
            "name": "pdf-processing",
            "description": "Process PDF files",
            "license": "Apache-2.0",
            "metadata": {"author": "test"},
            "compatibility": "Python 3.8+",
            "allowed-tools": "pdfplumber pypdf2"
        }
        errors = SkillValidator.validate_frontmatter_fields(frontmatter)
        assert len(errors) == 0

    def test_validate_frontmatter_fields_missing_required(self):
        """Test frontmatter with missing required fields."""
        frontmatter = {
            "name": "pdf-processing"
            # Missing description
        }
        errors = SkillValidator.validate_frontmatter_fields(frontmatter)
        assert any("description" in e.message.lower() for e in errors)

    def test_validate_frontmatter_fields_extra_fields(self):
        """Test frontmatter with extra unexpected fields."""
        frontmatter = {
            "name": "pdf-processing",
            "description": "Process PDF files",
            "extra_field": "unexpected",
            "another_one": "also unexpected"
        }
        errors = SkillValidator.validate_frontmatter_fields(frontmatter)
        assert any("unexpected" in e.message.lower() for e in errors)
        assert any("extra_field" in e.message for e in errors)

    def test_extract_frontmatter_valid(self):
        """Test extracting valid YAML frontmatter."""
        content = """---
name: pdf-processing
description: Process PDF files
---

# PDF Processing

Instructions here.
"""
        frontmatter, body, errors = SkillValidator.extract_frontmatter(content)

        assert len(errors) == 0
        assert frontmatter is not None
        assert frontmatter["name"] == "pdf-processing"
        assert frontmatter["description"] == "Process PDF files"
        assert "# PDF Processing" in body

    def test_extract_frontmatter_missing_start_marker(self):
        """Test content without starting --- marker."""
        content = """name: pdf-processing
description: Process PDF files
---

Instructions here.
"""
        frontmatter, body, errors = SkillValidator.extract_frontmatter(content)

        assert len(errors) > 0
        assert any("must start with" in e.message.lower() for e in errors)

    def test_extract_frontmatter_missing_end_marker(self):
        """Test content without closing --- marker."""
        content = """---
name: pdf-processing
description: Process PDF files

Instructions here.
"""
        frontmatter, body, errors = SkillValidator.extract_frontmatter(content)

        assert len(errors) > 0
        assert any("not properly closed" in e.message.lower() for e in errors)

    def test_extract_frontmatter_invalid_yaml(self):
        """Test content with invalid YAML in frontmatter."""
        content = """---
name: pdf-processing
description: [unclosed list
---

Instructions here.
"""
        frontmatter, body, errors = SkillValidator.extract_frontmatter(content)

        assert len(errors) > 0
        assert any("invalid yaml" in e.message.lower() for e in errors)

    def test_extract_frontmatter_not_dict(self):
        """Test frontmatter that's not a dictionary."""
        content = """---
- item1
- item2
---

Instructions here.
"""
        frontmatter, body, errors = SkillValidator.extract_frontmatter(content)

        assert len(errors) > 0
        assert any("mapping" in e.message.lower() for e in errors)

    def test_validate_directory_name_match(self):
        """Test directory name matches skill name."""
        skill_path = Path("/path/to/.agent/skills/pdf-processing")
        skill_name = "pdf-processing"
        errors = SkillValidator.validate_directory_name(skill_path, skill_name)
        assert len(errors) == 0

    def test_validate_directory_name_mismatch(self):
        """Test directory name doesn't match skill name."""
        skill_path = Path("/path/to/.agent/skills/pdf-processor")
        skill_name = "pdf-processing"
        errors = SkillValidator.validate_directory_name(skill_path, skill_name)
        assert len(errors) > 0
        assert any("does not match" in e.message for e in errors)

    def test_validate_file_valid_skill(self, tmp_path):
        """Test validating a complete valid skill."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        skill_content = """---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
metadata:
  author: test-org
  version: "1.0"
compatibility: Requires Python 3.8+ and pdfplumber
allowed-tools: pdfplumber pypdf2
---

# PDF Processing

## When to use this skill
Use this skill when the user needs to work with PDF files...

## How to extract text
1. Use pdfplumber for text extraction...
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert result.valid
        assert len(result.errors) == 0
        assert result.metadata is not None
        assert result.metadata["name"] == "pdf-processing"

    def test_validate_file_missing_skill_md(self, tmp_path):
        """Test validating directory without SKILL.md."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        result = SkillValidator.validate_file(skill_dir)

        assert not result.valid
        assert any("not found" in e.message for e in result.errors)

    def test_validate_file_invalid_name_format(self, tmp_path):
        """Test skill with invalid name format."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        skill_content = """---
name: PDF-Processing
description: Process PDF files
---

Instructions here.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert not result.valid
        assert any("lowercase" in e.message.lower() for e in result.errors)

    def test_validate_file_directory_name_mismatch(self, tmp_path):
        """Test skill where directory name doesn't match skill name."""
        skill_dir = tmp_path / "pdf-processor"  # Different from name in frontmatter
        skill_dir.mkdir()

        skill_content = """---
name: pdf-processing
description: Process PDF files
---

Instructions here.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert not result.valid
        assert any("does not match" in e.message for e in result.errors)

    def test_validate_file_missing_required_fields(self, tmp_path):
        """Test skill with missing required fields."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        skill_content = """---
name: pdf-processing
---

Instructions here.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert not result.valid
        assert any("description" in e.message.lower() for e in result.errors)

    def test_validate_file_extra_fields(self, tmp_path):
        """Test skill with extra unexpected fields."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        skill_content = """---
name: pdf-processing
description: Process PDF files
custom_field: unexpected
---

Instructions here.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert not result.valid
        assert any("unexpected" in e.message.lower() for e in result.errors)

    def test_validate_file_empty_body_warning(self, tmp_path):
        """Test skill with empty body generates warning."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        skill_content = """---
name: pdf-processing
description: Process PDF files
---

"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert result.valid  # Valid but has warnings
        assert len(result.warnings) > 0
        assert any("empty" in w.message.lower() for w in result.warnings)

    def test_validate_file_overlength_fields(self, tmp_path):
        """Test skill with fields exceeding length limits."""
        skill_dir = tmp_path / ("a" * 65)  # Name too long as directory
        skill_dir.mkdir()

        skill_content = f"""---
name: {'a' * 65}
description: {'a' * 1025}
compatibility: {'a' * 501}
---

Instructions here.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert not result.valid
        # Should have errors for name, description, and compatibility length
        assert len([e for e in result.errors if "maximum length" in e.message]) >= 3

    def test_validate_file_allowed_tools_handling(self, tmp_path):
        """Test skill with allowed-tools field."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        skill_content = """---
name: pdf-processing
description: Process PDF files
allowed-tools: pdfplumber pypdf2 reportlab
---

Instructions here.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert result.valid
        assert result.metadata["allowed-tools"] == "pdfplumber pypdf2 reportlab"

    def test_validate_file_metadata_handling(self, tmp_path):
        """Test skill with metadata field."""
        skill_dir = tmp_path / "pdf-processing"
        skill_dir.mkdir()

        skill_content = """---
name: pdf-processing
description: Process PDF files
metadata:
  author: test-org
  version: "2.1"
  tags:
    - pdf
    - documents
---

Instructions here.
"""
        (skill_dir / "SKILL.md").write_text(skill_content)

        result = SkillValidator.validate_file(skill_dir)

        assert result.valid
        assert result.metadata["metadata"]["author"] == "test-org"
        assert result.metadata["metadata"]["version"] == "2.1"
