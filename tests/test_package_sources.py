"""Tests for PackageSourceHandler.

Tests cover source type detection, parsing GitHub shorthand, Git cloning,
and local path copying operations.
"""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from uacs.packages import (
    PackageSource,
    PackageSourceHandler,
    GitCloneError,
    LocalCopyError,
    InvalidSourceError,
)


class TestDetectSourceType:
    """Tests for PackageSourceHandler.detect_source_type()."""

    def test_detect_github_shorthand(self):
        """Test detecting GitHub shorthand format (owner/repo)."""
        assert PackageSourceHandler.detect_source_type("owner/repo") == PackageSource.GITHUB
        assert PackageSourceHandler.detect_source_type("org-name/repo-name") == PackageSource.GITHUB
        assert PackageSourceHandler.detect_source_type("user123/my.repo") == PackageSource.GITHUB

    def test_detect_git_url_https(self):
        """Test detecting HTTPS Git URLs."""
        assert PackageSourceHandler.detect_source_type("https://github.com/owner/repo.git") == PackageSource.GIT_URL
        assert PackageSourceHandler.detect_source_type("https://github.com/owner/repo") == PackageSource.GIT_URL
        assert PackageSourceHandler.detect_source_type("https://gitlab.com/owner/repo.git") == PackageSource.GIT_URL
        assert PackageSourceHandler.detect_source_type("http://example.com/repo.git") == PackageSource.GIT_URL

    def test_detect_git_url_ssh(self):
        """Test detecting SSH Git URLs."""
        assert PackageSourceHandler.detect_source_type("git@github.com:owner/repo.git") == PackageSource.GIT_URL

    def test_detect_local_relative_paths(self):
        """Test detecting local relative paths."""
        assert PackageSourceHandler.detect_source_type("./local/path") == PackageSource.LOCAL
        assert PackageSourceHandler.detect_source_type("../parent/path") == PackageSource.LOCAL

    def test_detect_local_absolute_paths(self):
        """Test detecting local absolute paths."""
        assert PackageSourceHandler.detect_source_type("/absolute/path") == PackageSource.LOCAL

    def test_detect_local_windows_paths(self):
        """Test detecting Windows absolute paths."""
        assert PackageSourceHandler.detect_source_type("C:\\Windows\\Path") == PackageSource.LOCAL
        assert PackageSourceHandler.detect_source_type("D:\\Data\\Folder") == PackageSource.LOCAL

    def test_detect_unknown_source(self):
        """Test detecting unknown source types."""
        assert PackageSourceHandler.detect_source_type("invalid-format") == PackageSource.UNKNOWN
        assert PackageSourceHandler.detect_source_type("not a valid source") == PackageSource.UNKNOWN
        assert PackageSourceHandler.detect_source_type("") == PackageSource.UNKNOWN


class TestParseGitHubShorthand:
    """Tests for PackageSourceHandler.parse_github_shorthand()."""

    def test_parse_valid_shorthand(self):
        """Test parsing valid GitHub shorthand."""
        owner, repo = PackageSourceHandler.parse_github_shorthand("owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_parse_shorthand_with_hyphens(self):
        """Test parsing shorthand with hyphens."""
        owner, repo = PackageSourceHandler.parse_github_shorthand("my-org/my-repo")
        assert owner == "my-org"
        assert repo == "my-repo"

    def test_parse_shorthand_with_dots(self):
        """Test parsing shorthand with dots in repo name."""
        owner, repo = PackageSourceHandler.parse_github_shorthand("owner/repo.js")
        assert owner == "owner"
        assert repo == "repo.js"

    def test_parse_invalid_shorthand_no_slash(self):
        """Test parsing shorthand without slash raises error."""
        with pytest.raises(InvalidSourceError, match="Invalid GitHub shorthand"):
            PackageSourceHandler.parse_github_shorthand("invalid")

    def test_parse_invalid_shorthand_multiple_slashes(self):
        """Test parsing shorthand with multiple slashes raises error."""
        with pytest.raises(InvalidSourceError, match="Invalid GitHub shorthand"):
            PackageSourceHandler.parse_github_shorthand("owner/repo/extra")

    def test_parse_invalid_shorthand_empty(self):
        """Test parsing empty shorthand raises error."""
        with pytest.raises(InvalidSourceError, match="Invalid GitHub shorthand"):
            PackageSourceHandler.parse_github_shorthand("")

    def test_parse_invalid_shorthand_spaces(self):
        """Test parsing shorthand with spaces raises error."""
        with pytest.raises(InvalidSourceError, match="Invalid GitHub shorthand"):
            PackageSourceHandler.parse_github_shorthand("owner with spaces/repo")


class TestFetchFromGitHub:
    """Tests for PackageSourceHandler.fetch_from_github()."""

    def test_fetch_from_github_success(self, tmp_path):
        """Test successful GitHub repository fetch."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Create the directory to simulate successful clone
            target_dir.mkdir(parents=True)
            (target_dir / "README.md").touch()

            result = PackageSourceHandler.fetch_from_github("owner", "repo", target_dir)

            assert result == target_dir
            mock_run.assert_called_once()

            # Verify git clone command
            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "git"
            assert call_args[1] == "clone"
            assert "https://github.com/owner/repo.git" in call_args

    def test_fetch_from_github_constructs_correct_url(self, tmp_path):
        """Test that fetch_from_github constructs correct GitHub URL."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.PackageSourceHandler.fetch_from_git_url") as mock_fetch:
            mock_fetch.return_value = target_dir

            PackageSourceHandler.fetch_from_github("myorg", "myrepo", target_dir)

            mock_fetch.assert_called_once_with("https://github.com/myorg/myrepo.git", target_dir)


class TestFetchFromGitURL:
    """Tests for PackageSourceHandler.fetch_from_git_url()."""

    def test_fetch_from_git_url_success(self, tmp_path):
        """Test successful Git URL fetch."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Create directory to simulate successful clone
            target_dir.mkdir(parents=True)
            (target_dir / "file.txt").touch()

            result = PackageSourceHandler.fetch_from_git_url(
                "https://github.com/owner/repo.git",
                target_dir
            )

            assert result == target_dir
            mock_run.assert_called_once()

    def test_fetch_from_git_url_creates_target_dir(self, tmp_path):
        """Test that fetch creates target directory if it doesn't exist."""
        target_dir = tmp_path / "nested" / "target"

        with patch("uacs.packages.sources.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Create directory to simulate clone
            target_dir.mkdir(parents=True)
            (target_dir / "file.txt").touch()

            PackageSourceHandler.fetch_from_git_url(
                "https://github.com/owner/repo.git",
                target_dir
            )

            assert target_dir.exists()

    def test_fetch_from_git_url_clone_failure(self, tmp_path):
        """Test handling of git clone failure."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=128,
                cmd=["git", "clone"],
                stderr="fatal: repository not found"
            )

            with pytest.raises(GitCloneError, match="Failed to clone repository"):
                PackageSourceHandler.fetch_from_git_url(
                    "https://github.com/invalid/repo.git",
                    target_dir
                )

    def test_fetch_from_git_url_git_not_installed(self, tmp_path):
        """Test handling when git command is not found."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")

            with pytest.raises(GitCloneError, match="git command not found"):
                PackageSourceHandler.fetch_from_git_url(
                    "https://github.com/owner/repo.git",
                    target_dir
                )

    def test_fetch_from_git_url_empty_directory(self, tmp_path):
        """Test handling when cloned directory is empty."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Create empty directory
            target_dir.mkdir(parents=True)

            with pytest.raises(GitCloneError, match="directory is empty"):
                PackageSourceHandler.fetch_from_git_url(
                    "https://github.com/owner/repo.git",
                    target_dir
                )

    def test_fetch_uses_shallow_clone(self, tmp_path):
        """Test that fetch uses shallow clone (--depth 1)."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            target_dir.mkdir(parents=True)
            (target_dir / "file.txt").touch()

            PackageSourceHandler.fetch_from_git_url(
                "https://github.com/owner/repo.git",
                target_dir
            )

            call_args = mock_run.call_args[0][0]
            assert "--depth" in call_args
            assert "1" in call_args


class TestFetchFromLocal:
    """Tests for PackageSourceHandler.fetch_from_local()."""

    def test_fetch_from_local_success(self, tmp_path):
        """Test successful local directory copy."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        (source_dir / "subdir").mkdir()
        (source_dir / "subdir" / "nested.txt").write_text("nested")

        target_dir = tmp_path / "target"

        result = PackageSourceHandler.fetch_from_local(source_dir, target_dir)

        assert result == target_dir
        assert target_dir.exists()
        assert (target_dir / "file.txt").read_text() == "content"
        assert (target_dir / "subdir" / "nested.txt").read_text() == "nested"

    def test_fetch_from_local_nonexistent_source(self, tmp_path):
        """Test handling of non-existent source directory."""
        source_dir = tmp_path / "nonexistent"
        target_dir = tmp_path / "target"

        with pytest.raises(LocalCopyError, match="does not exist"):
            PackageSourceHandler.fetch_from_local(source_dir, target_dir)

    def test_fetch_from_local_source_is_file(self, tmp_path):
        """Test handling when source is a file instead of directory."""
        source_file = tmp_path / "file.txt"
        source_file.write_text("content")
        target_dir = tmp_path / "target"

        with pytest.raises(LocalCopyError, match="not a directory"):
            PackageSourceHandler.fetch_from_local(source_file, target_dir)

    def test_fetch_from_local_creates_target_dir(self, tmp_path):
        """Test that fetch creates target directory if needed."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").touch()

        target_dir = tmp_path / "nested" / "target"

        result = PackageSourceHandler.fetch_from_local(source_dir, target_dir)

        assert target_dir.exists()
        assert result == target_dir

    def test_fetch_from_local_resolves_relative_paths(self, tmp_path):
        """Test that fetch resolves relative paths correctly."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").touch()

        # Use relative path
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            target_dir = tmp_path / "target"

            result = PackageSourceHandler.fetch_from_local(Path("./source"), target_dir)

            assert result == target_dir
            assert (target_dir / "file.txt").exists()
        finally:
            os.chdir(old_cwd)


class TestFetchGeneric:
    """Tests for PackageSourceHandler.fetch() - generic interface."""

    def test_fetch_github_shorthand(self, tmp_path):
        """Test fetch with GitHub shorthand."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.PackageSourceHandler.fetch_from_github") as mock_fetch:
            mock_fetch.return_value = target_dir

            result, source_type = PackageSourceHandler.fetch("owner/repo", target_dir)

            assert result == target_dir
            assert source_type == PackageSource.GITHUB
            mock_fetch.assert_called_once_with("owner", "repo", target_dir)

    def test_fetch_git_url(self, tmp_path):
        """Test fetch with Git URL."""
        target_dir = tmp_path / "target"

        with patch("uacs.packages.sources.PackageSourceHandler.fetch_from_git_url") as mock_fetch:
            mock_fetch.return_value = target_dir

            git_url = "https://github.com/owner/repo.git"
            result, source_type = PackageSourceHandler.fetch(git_url, target_dir)

            assert result == target_dir
            assert source_type == PackageSource.GIT_URL
            mock_fetch.assert_called_once_with(git_url, target_dir)

    def test_fetch_local_path(self, tmp_path):
        """Test fetch with local path."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").touch()

        target_dir = tmp_path / "target"

        result, source_type = PackageSourceHandler.fetch(str(source_dir), target_dir)

        assert result == target_dir
        assert source_type == PackageSource.LOCAL
        assert target_dir.exists()

    def test_fetch_creates_temp_dir_when_none_provided(self, tmp_path):
        """Test that fetch creates temporary directory when target_dir is None."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").touch()

        result, source_type = PackageSourceHandler.fetch(str(source_dir))

        assert result.exists()
        assert source_type == PackageSource.LOCAL
        # Verify it's in a temp location
        assert "uacs-package-" in str(result)

    def test_fetch_unknown_source_raises_error(self, tmp_path):
        """Test that fetch with unknown source raises error."""
        target_dir = tmp_path / "target"

        with pytest.raises(InvalidSourceError, match="Unable to determine source type"):
            PackageSourceHandler.fetch("invalid-source-format", target_dir)

    def test_fetch_unsupported_source_type_raises_error(self, tmp_path):
        """Test handling of unsupported source type."""
        target_dir = tmp_path / "target"

        # This shouldn't happen in practice, but test error handling
        with patch("uacs.packages.sources.PackageSourceHandler.detect_source_type") as mock_detect:
            mock_detect.return_value = PackageSource.UNKNOWN

            with pytest.raises(InvalidSourceError):
                PackageSourceHandler.fetch("some-source", target_dir)


class TestGitHubShorthandPattern:
    """Tests for GitHub shorthand regex pattern matching."""

    def test_valid_github_patterns(self):
        """Test valid GitHub shorthand patterns."""
        pattern = PackageSourceHandler.GITHUB_SHORTHAND_PATTERN

        assert pattern.match("owner/repo")
        assert pattern.match("my-org/my-repo")
        assert pattern.match("user123/repo456")
        assert pattern.match("org/repo.js")
        assert pattern.match("org/repo-name")
        assert pattern.match("org_name/repo_name")

    def test_invalid_github_patterns(self):
        """Test invalid GitHub shorthand patterns."""
        pattern = PackageSourceHandler.GITHUB_SHORTHAND_PATTERN

        assert not pattern.match("no-slash")
        assert not pattern.match("/leading-slash")
        assert not pattern.match("trailing-slash/")
        assert not pattern.match("owner/repo/extra")
        assert not pattern.match("owner with spaces/repo")
        assert not pattern.match("")


class TestGitURLPatterns:
    """Tests for Git URL regex patterns."""

    def test_git_url_patterns_match_valid_urls(self):
        """Test that Git URL patterns match valid URLs."""
        patterns = PackageSourceHandler.GIT_URL_PATTERNS

        # Test HTTPS .git URLs
        assert any(p.match("https://github.com/owner/repo.git") for p in patterns)
        assert any(p.match("http://gitlab.com/owner/repo.git") for p in patterns)

        # Test SSH URLs
        assert any(p.match("git@github.com:owner/repo.git") for p in patterns)

        # Test GitHub HTTPS without .git
        assert any(p.match("https://github.com/owner/repo") for p in patterns)
        assert any(p.match("https://github.com/owner/repo/") for p in patterns)

        # Test GitLab HTTPS
        assert any(p.match("https://gitlab.com/owner/repo") for p in patterns)

    def test_git_url_patterns_reject_invalid_urls(self):
        """Test that Git URL patterns reject invalid URLs."""
        patterns = PackageSourceHandler.GIT_URL_PATTERNS

        assert not any(p.match("owner/repo") for p in patterns)
        assert not any(p.match("./local/path") for p in patterns)
        assert not any(p.match("/absolute/path") for p in patterns)
        assert not any(p.match("not-a-url") for p in patterns)
