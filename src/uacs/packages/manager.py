"""Package manager for installing and managing UACS skills.

Provides a minimal feature set similar to GitHub CLI extensions:
- Install packages from GitHub, Git URLs, or local paths
- List installed packages
- Validate packages
- Uninstall packages
- Update packages
"""

import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from uacs.packages.models import InstalledPackage, PackageSource
from uacs.skills_validator import SkillValidator, ValidationResult


class PackageManagerError(Exception):
    """Base exception for package manager errors."""

    pass


class PackageSourceHandler:
    """Handles parsing and fetching package sources."""

    GITHUB_PATTERN = re.compile(r"^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)$")
    GIT_URL_PATTERN = re.compile(r"^(https?://|git@|git://)")

    @staticmethod
    def parse_source(source: str) -> tuple[PackageSource, str]:
        """Parse source string and determine type.

        Args:
            source: Source string (e.g., "owner/repo", "https://...", "/path/to/skill")

        Returns:
            Tuple of (PackageSource, normalized_source)
        """
        source = source.strip()

        # Check if it's a GitHub shorthand (owner/repo)
        if PackageSourceHandler.GITHUB_PATTERN.match(source):
            return PackageSource.GITHUB, source

        # Check if it's a Git URL
        if PackageSourceHandler.GIT_URL_PATTERN.match(source):
            return PackageSource.GIT_URL, source

        # Check if it's a local path
        path = Path(source).expanduser().resolve()
        if path.exists():
            return PackageSource.LOCAL, str(path)

        return PackageSource.UNKNOWN, source

    @staticmethod
    def fetch(source: str, source_type: PackageSource, temp_dir: Path) -> Path:
        """Fetch package source to temporary directory.

        Args:
            source: Source string
            source_type: Type of source
            temp_dir: Temporary directory to fetch to

        Returns:
            Path to fetched package directory
        """
        if source_type == PackageSource.LOCAL:
            source_path = Path(source)
            if not source_path.exists():
                raise PackageManagerError(f"Local path does not exist: {source}")
            # Copy local directory to temp
            dest = temp_dir / source_path.name
            shutil.copytree(source_path, dest, symlinks=False)
            return dest

        elif source_type == PackageSource.GITHUB:
            # Convert GitHub shorthand to full URL
            git_url = f"https://github.com/{source}.git"
            return PackageSourceHandler._git_clone(git_url, temp_dir)

        elif source_type == PackageSource.GIT_URL:
            return PackageSourceHandler._git_clone(source, temp_dir)

        else:
            raise PackageManagerError(f"Unsupported source type: {source_type}")

    @staticmethod
    def _git_clone(url: str, temp_dir: Path) -> Path:
        """Clone a git repository.

        Args:
            url: Git URL
            temp_dir: Directory to clone into

        Returns:
            Path to cloned repository
        """
        import subprocess

        # Extract repo name from URL
        repo_name = url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        dest = temp_dir / repo_name

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(dest)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise PackageManagerError(
                f"Failed to clone repository: {e.stderr or e.stdout}"
            )
        except FileNotFoundError:
            raise PackageManagerError(
                "git command not found. Please install git to use git sources."
            )

        return dest


class PackageManager:
    """Manages installation and lifecycle of UACS skill packages.

    Packages are stored in .agent/skills/ directory with metadata in
    .agent/skills/.packages.json.
    """

    def __init__(self, base_path: Path | None = None):
        """Initialize package manager.

        Args:
            base_path: Base path for package storage. Defaults to current directory.
        """
        self.base_path = base_path or Path.cwd()
        self.skills_dir = self.base_path / ".agent" / "skills"
        self.metadata_file = self.skills_dir / ".packages.json"
        self.validator = SkillValidator()

        # Ensure directories exist
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self) -> dict[str, Any]:
        """Load package metadata from .packages.json."""
        if not self.metadata_file.exists():
            return {"packages": {}}

        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise PackageManagerError(f"Failed to parse metadata file: {e}")

    def _save_metadata(self, metadata: dict[str, Any]) -> None:
        """Save package metadata to .packages.json."""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def install(self, source: str, validate: bool = True, force: bool = False) -> InstalledPackage:
        """Install a package from a source.

        Installation flow:
        1. Parse source to determine type
        2. Fetch to temporary directory
        3. Validate using SkillValidator (if validate=True)
        4. Copy to .agent/skills/{name}/
        5. Save metadata

        Args:
            source: Package source (GitHub repo, Git URL, or local path)
            validate: Whether to validate before installing (default: True)
            force: Whether to overwrite existing package (default: False)

        Returns:
            InstalledPackage with installation details

        Raises:
            PackageManagerError: If installation fails
        """
        # Parse source
        source_type, normalized_source = PackageSourceHandler.parse_source(source)

        if source_type == PackageSource.UNKNOWN:
            raise PackageManagerError(
                f"Unable to determine package source type: {source}\n"
                "Supported formats:\n"
                "  - GitHub: owner/repo\n"
                "  - Git URL: https://... or git@...\n"
                "  - Local path: /path/to/skill"
            )

        # Create temporary directory for fetching
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Fetch package to temp directory
            try:
                fetched_path = PackageSourceHandler.fetch(
                    normalized_source, source_type, temp_path
                )
            except Exception as e:
                raise PackageManagerError(f"Failed to fetch package: {e}")

            # Validate package if requested
            if validate:
                validation_result = self.validator.validate_file(fetched_path)

                if not validation_result.valid:
                    error_messages = [
                        f"{err.field}: {err.message}" for err in validation_result.errors
                    ]
                    raise PackageManagerError(
                        f"Package validation failed:\n" + "\n".join(error_messages)
                    )

                # Extract package name from metadata
                if not validation_result.metadata or "name" not in validation_result.metadata:
                    raise PackageManagerError(
                        "Package validation succeeded but no name found in metadata"
                    )

                package_name = validation_result.metadata["name"]
                package_metadata = validation_result.metadata
            else:
                # Try to extract name from SKILL.md manually
                skill_md = fetched_path / "SKILL.md"
                if skill_md.exists():
                    import re
                    content = skill_md.read_text()
                    match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
                    if match:
                        package_name = match.group(1).strip()
                        package_metadata = {"name": package_name}
                    else:
                        raise PackageManagerError(
                            "Could not determine package name. Enable validation or ensure SKILL.md has a 'name' field."
                        )
                else:
                    raise PackageManagerError(
                        "No SKILL.md found. Enable validation to install this package."
                    )

            # Check if already installed
            metadata = self._load_metadata()
            if package_name in metadata.get("packages", {}):
                if not force:
                    raise PackageManagerError(
                        f"Package '{package_name}' is already installed. "
                        f"Use force=True to overwrite or update() to update it."
                    )
                # Remove existing package if force=True
                self.uninstall(package_name)

            # Copy to skills directory
            dest_path = self.skills_dir / package_name
            if dest_path.exists():
                raise PackageManagerError(
                    f"Directory already exists: {dest_path}. "
                    f"Remove it before installing."
                )

            try:
                shutil.copytree(fetched_path, dest_path, symlinks=False)
            except Exception as e:
                raise PackageManagerError(f"Failed to copy package: {e}")

        # Create installed package record
        installed_pkg = InstalledPackage(
            name=package_name,
            source=source,
            source_type=source_type,
            version=package_metadata.get("version"),
            location=dest_path,
            is_valid=True,
            validation_errors=[],
            metadata=package_metadata,
        )

        # Save to metadata
        metadata["packages"][package_name] = installed_pkg.to_dict()
        self._save_metadata(metadata)

        return installed_pkg

    def list_installed(self) -> list[InstalledPackage]:
        """List all installed packages.

        Returns:
            List of InstalledPackage objects
        """
        metadata = self._load_metadata()
        packages = []

        for pkg_data in metadata.get("packages", {}).values():
            try:
                packages.append(InstalledPackage.from_dict(pkg_data))
            except Exception:
                # Skip malformed entries
                continue

        return packages

    def validate(self, package_name: str) -> ValidationResult:
        """Validate an installed package.

        Args:
            package_name: Name of package to validate

        Returns:
            ValidationResult

        Raises:
            PackageManagerError: If package not found
        """
        metadata = self._load_metadata()
        packages = metadata.get("packages", {})

        if package_name not in packages:
            raise PackageManagerError(f"Package not found: {package_name}")

        pkg_data = packages[package_name]
        location = Path(pkg_data["location"]) if pkg_data.get("location") else None

        if not location or not location.exists():
            raise PackageManagerError(
                f"Package directory not found: {location}. Package may be corrupted."
            )

        return self.validator.validate_file(location)

    def uninstall(self, package_name: str) -> bool:
        """Uninstall a package.

        Args:
            package_name: Name of package to uninstall

        Returns:
            True if successful

        Raises:
            PackageManagerError: If uninstallation fails
        """
        metadata = self._load_metadata()
        packages = metadata.get("packages", {})

        if package_name not in packages:
            raise PackageManagerError(f"Package not found: {package_name}")

        # Get package location
        pkg_data = packages[package_name]
        location = Path(pkg_data["location"]) if pkg_data.get("location") else None

        # Remove directory
        if location and location.exists():
            try:
                shutil.rmtree(location)
            except Exception as e:
                raise PackageManagerError(
                    f"Failed to remove package directory: {e}"
                )

        # Remove from metadata
        del packages[package_name]
        self._save_metadata(metadata)

        return True

    def update(self, package_name: str) -> InstalledPackage:
        """Update an installed package.

        Args:
            package_name: Name of package to update

        Returns:
            Updated InstalledPackage

        Raises:
            PackageManagerError: If update fails
        """
        metadata = self._load_metadata()
        packages = metadata.get("packages", {})

        if package_name not in packages:
            raise PackageManagerError(f"Package not found: {package_name}")

        pkg_data = packages[package_name]
        source = pkg_data["source"]
        source_type = PackageSource(pkg_data["source_type"])

        # For local sources, we can't update
        if source_type == PackageSource.LOCAL:
            raise PackageManagerError(
                "Cannot update local packages. Use uninstall and install instead."
            )

        # Uninstall existing
        self.uninstall(package_name)

        # Reinstall from source
        try:
            return self.install(source)
        except Exception as e:
            raise PackageManagerError(f"Failed to update package: {e}")
