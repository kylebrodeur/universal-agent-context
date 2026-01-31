"""Minimal local package manager for UACS.

Provides simple package management (install, list, validate, remove) without
remote discovery features. Inspired by GitHub CLI extensions pattern.
"""

from uacs.packages.manager import PackageManager
from uacs.packages.models import InstalledPackage, PackageSource
from uacs.packages.sources import (
    GitCloneError,
    InvalidSourceError,
    LocalCopyError,
    PackageSourceError,
    PackageSourceHandler,
)

__all__ = [
    "GitCloneError",
    "InstalledPackage",
    "InvalidSourceError",
    "LocalCopyError",
    "PackageManager",
    "PackageSource",
    "PackageSourceError",
    "PackageSourceHandler",
]
