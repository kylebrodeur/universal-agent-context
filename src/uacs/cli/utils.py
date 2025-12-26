"""Shared CLI utilities for UACS commands."""

import os
from pathlib import Path


def get_project_root() -> Path:
    """Get the effective project root directory.

    Prioritizes PWD environment variable to handle cases where the tool
    is invoked via 'uv run --directory ...' which changes the process CWD.
    """
    # Check if PWD is set and valid
    pwd = os.environ.get("PWD")
    if pwd:
        path = Path(pwd)
        if path.exists() and path.is_dir():
            return path

    # Fallback to current working directory
    return Path.cwd()


__all__ = ["get_project_root"]
