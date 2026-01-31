"""Package source handlers for fetching packages from different sources.

Handles fetching packages from GitHub shorthand, Git URLs, and local paths.
Inspired by GitHub CLI extensions pattern.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from uacs.packages.models import PackageSource


class PackageSourceError(Exception):
    """Base exception for package source operations."""

    pass


class GitCloneError(PackageSourceError):
    """Raised when git clone operation fails."""

    pass


class LocalCopyError(PackageSourceError):
    """Raised when local copy operation fails."""

    pass


class InvalidSourceError(PackageSourceError):
    """Raised when source format is invalid."""

    pass


class PackageSourceHandler:
    """Handles fetching packages from different source types."""

    # GitHub shorthand pattern: owner/repo
    GITHUB_SHORTHAND_PATTERN = re.compile(r"^[a-zA-Z0-9][\w-]*/[\w.-]+$")

    # Git URL patterns
    GIT_URL_PATTERNS = [
        re.compile(r"^https?://.*\.git$"),  # HTTPS URLs ending in .git
        re.compile(r"^git@.*:.*\.git$"),  # SSH URLs
        re.compile(r"^https?://github\.com/[\w-]+/[\w.-]+/?$"),  # GitHub HTTPS
        re.compile(r"^https?://gitlab\.com/[\w-]+/[\w.-]+/?$"),  # GitLab HTTPS
    ]

    @staticmethod
    def detect_source_type(source: str) -> PackageSource:
        """Detect the type of package source.

        Args:
            source: Source string (GitHub shorthand, Git URL, or local path)

        Returns:
            PackageSource enum value
        """
        # Check for local paths first
        if (
            source.startswith("./")
            or source.startswith("../")
            or source.startswith("/")
        ):
            return PackageSource.LOCAL

        # Check for absolute Windows paths
        if len(source) >= 3 and source[1:3] == ":\\":
            return PackageSource.LOCAL

        # Check for GitHub shorthand (owner/repo)
        if PackageSourceHandler.GITHUB_SHORTHAND_PATTERN.match(source):
            return PackageSource.GITHUB

        # Check for Git URLs
        for pattern in PackageSourceHandler.GIT_URL_PATTERNS:
            if pattern.match(source):
                return PackageSource.GIT_URL

        # Try parsing as URL
        try:
            parsed = urlparse(source)
            if parsed.scheme in ("http", "https", "git", "ssh"):
                return PackageSource.GIT_URL
        except Exception:
            pass

        return PackageSource.UNKNOWN

    @staticmethod
    def parse_github_shorthand(shorthand: str) -> tuple[str, str]:
        """Parse GitHub shorthand into owner and repo.

        Args:
            shorthand: GitHub shorthand string (e.g., "owner/repo")

        Returns:
            Tuple of (owner, repo)

        Raises:
            InvalidSourceError: If shorthand format is invalid
        """
        if not PackageSourceHandler.GITHUB_SHORTHAND_PATTERN.match(shorthand):
            raise InvalidSourceError(
                f"Invalid GitHub shorthand format: {shorthand}. "
                "Expected format: owner/repo"
            )

        parts = shorthand.split("/")
        if len(parts) != 2:
            raise InvalidSourceError(f"Invalid GitHub shorthand format: {shorthand}")

        owner, repo = parts
        return owner, repo

    @staticmethod
    def fetch_from_github(owner: str, repo: str, target_dir: Path) -> Path:
        """Clone GitHub repository to target directory.

        Args:
            owner: GitHub repository owner
            repo: GitHub repository name
            target_dir: Directory to clone into

        Returns:
            Path to cloned repository

        Raises:
            GitCloneError: If git clone operation fails
        """
        url = f"https://github.com/{owner}/{repo}.git"
        return PackageSourceHandler.fetch_from_git_url(url, target_dir)

    @staticmethod
    def fetch_from_git_url(url: str, target_dir: Path) -> Path:
        """Clone git repository from URL to target directory.

        Args:
            url: Git repository URL
            target_dir: Directory to clone into

        Returns:
            Path to cloned repository

        Raises:
            GitCloneError: If git clone operation fails
        """
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Run git clone command
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(target_dir)],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            raise GitCloneError(
                f"Failed to clone repository from {url}: {error_msg}"
            ) from e
        except FileNotFoundError:
            raise GitCloneError(
                "git command not found. Please ensure git is installed and in PATH."
            )

        # Verify the directory exists and has content
        if not target_dir.exists() or not any(target_dir.iterdir()):
            raise GitCloneError(f"Clone succeeded but directory is empty: {target_dir}")

        return target_dir

    @staticmethod
    def fetch_from_local(source_path: Path, target_dir: Path) -> Path:
        """Copy local directory to target directory.

        Args:
            source_path: Source directory path
            target_dir: Target directory to copy to

        Returns:
            Path to copied directory

        Raises:
            LocalCopyError: If copy operation fails
        """
        # Resolve source path
        try:
            source_path = source_path.resolve()
        except Exception as e:
            raise LocalCopyError(f"Failed to resolve source path: {e}") from e

        # Verify source exists
        if not source_path.exists():
            raise LocalCopyError(f"Source path does not exist: {source_path}")

        if not source_path.is_dir():
            raise LocalCopyError(f"Source path is not a directory: {source_path}")

        # Create target directory
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise LocalCopyError(f"Failed to create target directory: {e}") from e

        # Copy directory contents
        try:
            shutil.copytree(source_path, target_dir, dirs_exist_ok=True)
        except Exception as e:
            raise LocalCopyError(
                f"Failed to copy from {source_path} to {target_dir}: {e}"
            ) from e

        return target_dir

    @staticmethod
    def fetch(
        source: str, target_dir: Path | None = None
    ) -> tuple[Path, PackageSource]:
        """Fetch package from source to target directory.

        Args:
            source: Package source (GitHub shorthand, Git URL, or local path)
            target_dir: Target directory (creates temp dir if None)

        Returns:
            Tuple of (package_path, source_type)

        Raises:
            InvalidSourceError: If source type cannot be determined
            GitCloneError: If git clone operation fails
            LocalCopyError: If local copy operation fails
        """
        source_type = PackageSourceHandler.detect_source_type(source)

        if source_type == PackageSource.UNKNOWN:
            raise InvalidSourceError(
                f"Unable to determine source type for: {source}. "
                "Expected GitHub shorthand (owner/repo), Git URL, or local path."
            )

        # Create temp directory if not provided
        if target_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="uacs-package-")
            target_dir = Path(temp_dir)

        # Fetch based on source type
        if source_type == PackageSource.GITHUB:
            owner, repo = PackageSourceHandler.parse_github_shorthand(source)
            package_path = PackageSourceHandler.fetch_from_github(
                owner, repo, target_dir
            )
        elif source_type == PackageSource.GIT_URL:
            package_path = PackageSourceHandler.fetch_from_git_url(source, target_dir)
        elif source_type == PackageSource.LOCAL:
            source_path = Path(source)
            package_path = PackageSourceHandler.fetch_from_local(
                source_path, target_dir
            )
        else:
            raise InvalidSourceError(f"Unsupported source type: {source_type}")

        return package_path, source_type
