"""Tests for PackageManager.

Tests cover installation, listing, validation, and removal of packages
from different sources (GitHub, Git URLs, local paths).
"""

import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from uacs.packages import (
    PackageManager,
    PackageSource,
    InstalledPackage,
)
from uacs.packages.manager import PackageManagerError


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory."""
    return tmp_path


@pytest.fixture
def package_manager(tmp_project):
    """Create PackageManager instance."""
    return PackageManager(tmp_project)


@pytest.fixture
def sample_skill_dir(tmp_path):
    """Create a sample skill directory for testing."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    # Create a valid SKILL.md file
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("""---
name: test-skill
description: A test skill for unit testing
metadata:
  version: 1.0.0
---
# Test Skill

## Triggers
- test
- testing

## Instructions
This is a test skill for unit testing the package manager.
""")

    return skill_dir


@pytest.fixture
def mock_validator():
    """Create a mock SkillValidator."""
    with patch("uacs.packages.manager.SkillValidator") as mock:
        validator = mock.return_value
        # Default to valid validation
        validation_result = Mock()
        validation_result.valid = True
        validation_result.errors = []
        validation_result.metadata = {
            "name": "test-skill",
            "description": "A test skill",
            "version": "1.0.0"
        }
        validator.validate_file.return_value = validation_result
        yield validator


class TestPackageManagerInit:
    """Tests for PackageManager initialization."""

    def test_init_creates_directories(self, tmp_project):
        """Test that initialization creates necessary directories."""
        pm = PackageManager(tmp_project)

        assert pm.base_path == tmp_project
        assert pm.skills_dir == tmp_project / ".agent" / "skills"
        assert pm.skills_dir.exists()
        assert pm.metadata_file == pm.skills_dir / ".packages.json"

    def test_init_with_no_path_uses_cwd(self):
        """Test that initialization without path uses current directory."""
        pm = PackageManager()

        assert pm.base_path == Path.cwd()


class TestPackageManagerInstall:
    """Tests for PackageManager.install()."""

    def test_install_from_local_path(self, package_manager, sample_skill_dir, mock_validator):
        """Test installing package from local path."""
        source = str(sample_skill_dir)

        package = package_manager.install(source)

        assert package.name == "test-skill"
        assert package.source == source
        assert package.source_type == PackageSource.LOCAL
        # Version is nested in metadata.metadata
        assert package.metadata.get("metadata", {}).get("version") == "1.0.0"
        assert package.is_valid is True
        assert package.location == package_manager.skills_dir / "test-skill"

        # Verify package was copied to skills directory
        assert package.location.exists()
        assert (package.location / "SKILL.md").exists()

    def test_install_from_github_shorthand(self, package_manager, sample_skill_dir, mock_validator):
        """Test installing package from GitHub shorthand (owner/repo)."""
        with patch("uacs.packages.manager.PackageSourceHandler.fetch") as mock_fetch:
            mock_fetch.return_value = sample_skill_dir

            package = package_manager.install("owner/repo")

            assert package.name == "test-skill"
            assert package.source == "owner/repo"
            assert package.source_type == PackageSource.GITHUB
            mock_fetch.assert_called_once()

    def test_install_from_git_url(self, package_manager, sample_skill_dir, mock_validator):
        """Test installing package from Git URL."""
        with patch("uacs.packages.manager.PackageSourceHandler.fetch") as mock_fetch:
            mock_fetch.return_value = sample_skill_dir

            git_url = "https://github.com/owner/repo.git"
            package = package_manager.install(git_url)

            assert package.name == "test-skill"
            assert package.source == git_url
            assert package.source_type == PackageSource.GIT_URL

    def test_install_duplicate_raises_error(self, package_manager, sample_skill_dir, mock_validator):
        """Test that installing duplicate package raises error."""
        source = str(sample_skill_dir)

        # Install first time
        package_manager.install(source)

        # Try to install again
        with pytest.raises(PackageManagerError, match="already installed"):
            package_manager.install(source)

    def test_install_invalid_source_raises_error(self, package_manager):
        """Test that invalid source raises error."""
        with pytest.raises(PackageManagerError, match="Unable to determine package source type"):
            package_manager.install("invalid-source")

    def test_install_validation_failure_raises_error(self, package_manager, sample_skill_dir):
        """Test that validation failure raises error."""
        with patch("uacs.packages.manager.SkillValidator") as mock_validator_class:
            validator = mock_validator_class.return_value
            validation_result = Mock()
            validation_result.valid = False
            validation_result.errors = [
                Mock(field="name", message="Name is required"),
                Mock(field="triggers", message="At least one trigger is required")
            ]
            validator.validate_file.return_value = validation_result

            pm = PackageManager(package_manager.base_path)

            with pytest.raises(PackageManagerError, match="validation failed"):
                pm.install(str(sample_skill_dir))

    def test_install_no_name_in_metadata_raises_error(self, package_manager, sample_skill_dir):
        """Test that missing name in metadata raises error."""
        with patch("uacs.packages.manager.SkillValidator") as mock_validator_class:
            validator = mock_validator_class.return_value
            validation_result = Mock()
            validation_result.valid = True
            validation_result.errors = []
            validation_result.metadata = {}  # No name
            validator.validate_file.return_value = validation_result

            pm = PackageManager(package_manager.base_path)

            with pytest.raises(PackageManagerError, match="no name found"):
                pm.install(str(sample_skill_dir))


class TestPackageManagerList:
    """Tests for PackageManager.list_installed()."""

    def test_list_empty(self, package_manager):
        """Test listing when no packages are installed."""
        packages = package_manager.list_installed()

        assert packages == []

    def test_list_installed_packages(self, package_manager, sample_skill_dir, mock_validator):
        """Test listing installed packages."""
        # Install a package
        package_manager.install(str(sample_skill_dir))

        packages = package_manager.list_installed()

        assert len(packages) == 1
        assert packages[0].name == "test-skill"
        assert packages[0].source_type == PackageSource.LOCAL

    def test_list_skips_malformed_entries(self, package_manager):
        """Test that list_installed skips malformed metadata entries."""
        # Create malformed metadata
        metadata = {
            "packages": {
                "bad-package": {
                    "name": "bad-package",
                    # Missing required fields
                }
            }
        }
        package_manager._save_metadata(metadata)

        # Should not raise error, just skip the bad entry
        packages = package_manager.list_installed()
        assert packages == []


class TestPackageManagerValidate:
    """Tests for PackageManager.validate()."""

    def test_validate_installed_package(self, package_manager, sample_skill_dir):
        """Test validating an installed package."""
        # Install package
        package_manager.install(str(sample_skill_dir))

        # Validate (uses real validator this time, not the mock)
        result = package_manager.validate("test-skill")

        assert result.valid is True

    def test_validate_nonexistent_package_raises_error(self, package_manager):
        """Test that validating non-existent package raises error."""
        with pytest.raises(PackageManagerError, match="Package not found"):
            package_manager.validate("nonexistent")

    def test_validate_missing_directory_raises_error(self, package_manager):
        """Test that validating package with missing directory raises error."""
        # Create metadata for package that doesn't exist
        metadata = {
            "packages": {
                "ghost-package": {
                    "name": "ghost-package",
                    "source": "owner/repo",
                    "source_type": "github",
                    "location": str(package_manager.skills_dir / "ghost-package"),
                    "install_date": "2024-01-01T00:00:00"
                }
            }
        }
        package_manager._save_metadata(metadata)

        with pytest.raises(PackageManagerError, match="directory not found"):
            package_manager.validate("ghost-package")


class TestPackageManagerUninstall:
    """Tests for PackageManager.uninstall()."""

    def test_uninstall_package(self, package_manager, sample_skill_dir, mock_validator):
        """Test uninstalling a package."""
        # Install package
        package_manager.install(str(sample_skill_dir))

        # Verify it exists
        packages = package_manager.list_installed()
        assert len(packages) == 1

        # Uninstall
        result = package_manager.uninstall("test-skill")

        assert result is True

        # Verify it's gone
        packages = package_manager.list_installed()
        assert len(packages) == 0

        # Verify directory was removed
        assert not (package_manager.skills_dir / "test-skill").exists()

    def test_uninstall_nonexistent_package_raises_error(self, package_manager):
        """Test that uninstalling non-existent package raises error."""
        with pytest.raises(PackageManagerError, match="Package not found"):
            package_manager.uninstall("nonexistent")

    def test_uninstall_removes_from_metadata(self, package_manager, sample_skill_dir, mock_validator):
        """Test that uninstall removes package from metadata file."""
        # Install package
        package_manager.install(str(sample_skill_dir))

        # Verify metadata
        metadata = package_manager._load_metadata()
        assert "test-skill" in metadata["packages"]

        # Uninstall
        package_manager.uninstall("test-skill")

        # Verify removed from metadata
        metadata = package_manager._load_metadata()
        assert "test-skill" not in metadata.get("packages", {})


class TestPackageManagerUpdate:
    """Tests for PackageManager.update()."""

    def test_update_github_package(self, package_manager, sample_skill_dir, mock_validator):
        """Test updating a GitHub package."""
        with patch("uacs.packages.manager.PackageSourceHandler.fetch") as mock_fetch:
            mock_fetch.return_value = sample_skill_dir

            # Install package
            package_manager.install("owner/repo")

            # Update package (should uninstall and reinstall)
            updated = package_manager.update("test-skill")

            assert updated.name == "test-skill"
            assert mock_fetch.call_count == 2  # Once for install, once for update

    def test_update_git_url_package(self, package_manager, sample_skill_dir, mock_validator):
        """Test updating a Git URL package."""
        with patch("uacs.packages.manager.PackageSourceHandler.fetch") as mock_fetch:
            mock_fetch.return_value = sample_skill_dir

            git_url = "https://github.com/owner/repo.git"

            # Install package
            package_manager.install(git_url)

            # Update package
            updated = package_manager.update("test-skill")

            assert updated.name == "test-skill"

    def test_update_local_package_raises_error(self, package_manager, sample_skill_dir, mock_validator):
        """Test that updating local package raises error."""
        # Install from local path
        package_manager.install(str(sample_skill_dir))

        # Try to update
        with pytest.raises(PackageManagerError, match="Cannot update local packages"):
            package_manager.update("test-skill")

    def test_update_nonexistent_package_raises_error(self, package_manager):
        """Test that updating non-existent package raises error."""
        with pytest.raises(PackageManagerError, match="Package not found"):
            package_manager.update("nonexistent")


class TestPackageManagerMetadata:
    """Tests for metadata file handling."""

    def test_load_metadata_creates_default(self, package_manager):
        """Test that loading non-existent metadata returns default."""
        metadata = package_manager._load_metadata()

        assert metadata == {"packages": {}}

    def test_load_metadata_handles_invalid_json(self, package_manager):
        """Test that loading invalid JSON raises error."""
        # Write invalid JSON
        package_manager.metadata_file.write_text("{ invalid json")

        with pytest.raises(PackageManagerError, match="Failed to parse"):
            package_manager._load_metadata()

    def test_save_and_load_metadata(self, package_manager):
        """Test saving and loading metadata."""
        metadata = {
            "packages": {
                "test-pkg": {
                    "name": "test-pkg",
                    "source": "owner/repo",
                    "source_type": "github"
                }
            }
        }

        package_manager._save_metadata(metadata)

        loaded = package_manager._load_metadata()
        assert loaded == metadata

    def test_metadata_persistence(self, tmp_project):
        """Test that metadata persists across PackageManager instances."""
        # Create first instance and add data
        pm1 = PackageManager(tmp_project)
        metadata = {
            "packages": {
                "test-pkg": {
                    "name": "test-pkg",
                    "source": "owner/repo",
                    "source_type": "github",
                    "install_date": "2024-01-01T00:00:00"
                }
            }
        }
        pm1._save_metadata(metadata)

        # Create second instance and verify data
        pm2 = PackageManager(tmp_project)
        loaded = pm2._load_metadata()

        assert loaded == metadata


class TestInstalledPackageModel:
    """Tests for InstalledPackage data model."""

    def test_to_dict(self):
        """Test converting InstalledPackage to dictionary."""
        package = InstalledPackage(
            name="test-skill",
            source="owner/repo",
            source_type=PackageSource.GITHUB,
            version="1.0.0",
            location=Path("/path/to/skill"),
            is_valid=True,
            validation_errors=[],
            metadata={"key": "value"}
        )

        data = package.to_dict()

        assert data["name"] == "test-skill"
        assert data["source"] == "owner/repo"
        assert data["source_type"] == "github"
        assert data["version"] == "1.0.0"
        assert data["location"] == "/path/to/skill"
        assert data["is_valid"] is True
        assert data["metadata"] == {"key": "value"}

    def test_from_dict(self):
        """Test creating InstalledPackage from dictionary."""
        data = {
            "name": "test-skill",
            "source": "owner/repo",
            "source_type": "github",
            "version": "1.0.0",
            "install_date": "2024-01-01T12:00:00",
            "location": "/path/to/skill",
            "is_valid": True,
            "validation_errors": [],
            "metadata": {"key": "value"}
        }

        package = InstalledPackage.from_dict(data)

        assert package.name == "test-skill"
        assert package.source == "owner/repo"
        assert package.source_type == PackageSource.GITHUB
        assert package.version == "1.0.0"
        assert package.location == Path("/path/to/skill")
        assert package.is_valid is True
        assert package.metadata == {"key": "value"}

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are reversible."""
        original = InstalledPackage(
            name="test-skill",
            source="owner/repo",
            source_type=PackageSource.GITHUB,
            version="1.0.0",
            location=Path("/path/to/skill")
        )

        data = original.to_dict()
        restored = InstalledPackage.from_dict(data)

        assert restored.name == original.name
        assert restored.source == original.source
        assert restored.source_type == original.source_type
        assert restored.version == original.version
        assert restored.location == original.location
