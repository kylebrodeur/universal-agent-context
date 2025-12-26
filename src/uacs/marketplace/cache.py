"""Marketplace cache management system.

Provides TTL-based caching for repository indexes and search results
to reduce GitHub API calls and improve performance.
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""

    key: str
    data: Any
    cached_at: float  # Unix timestamp
    expires_at: float  # Unix timestamp
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() > self.expires_at

    def is_valid(self) -> bool:
        """Check if cache entry is valid (exists and not expired)."""
        return not self.is_expired()


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int = 0
    total_size_bytes: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_refresh: float = 0.0
    repos_cached: list[str] | None = None

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0

    @property
    def size_mb(self) -> float:
        """Get cache size in megabytes."""
        return self.total_size_bytes / (1024 * 1024)


class MarketplaceCache:
    """Manages caching for marketplace data."""

    DEFAULT_TTL = 86400  # 24 hours in seconds

    def __init__(self, cache_dir: Path | None = None):
        """Initialize marketplace cache.

        Args:
            cache_dir: Directory to store cache files (defaults to ~/.cache/multi-agent-cli/marketplace/)
        """
        self.cache_dir = (
            cache_dir or Path.home() / ".cache" / "multi-agent-cli" / "marketplace"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.repo_indexes_dir = self.cache_dir / "repo_indexes"
        self.search_results_dir = self.cache_dir / "search_results"
        self.metadata_file = self.cache_dir / "metadata.json"

        # Create subdirectories
        self.repo_indexes_dir.mkdir(exist_ok=True)
        self.search_results_dir.mkdir(exist_ok=True)

        # Load metadata
        self._stats = self._load_metadata()

    def _load_metadata(self) -> CacheStats:
        """Load cache metadata from disk."""
        if not self.metadata_file.exists():
            return CacheStats()

        try:
            with open(self.metadata_file) as f:
                data = json.load(f)
                return CacheStats(**data)
        except Exception as e:
            logger.warning(f"Failed to load cache metadata: {e}")
            return CacheStats()

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(asdict(self._stats), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {e}")

    def _get_cache_path(self, cache_type: str, key: str) -> Path:
        """Get path to cache file.

        Args:
            cache_type: Type of cache ('repo_index' or 'search_result')
            key: Cache key

        Returns:
            Path to cache file
        """
        if cache_type == "repo_index":
            return self.repo_indexes_dir / f"{key}.json"
        if cache_type == "search_result":
            return self.search_results_dir / f"{key}.json"
        raise ValueError(f"Unknown cache type: {cache_type}")

    def _read_cache_file(self, path: Path) -> CacheEntry | None:
        """Read cache entry from file.

        Args:
            path: Path to cache file

        Returns:
            CacheEntry if valid, None otherwise
        """
        if not path.exists():
            return None

        try:
            with open(path) as f:
                data = json.load(f)
                entry = CacheEntry(**data)

                # Update access stats
                entry.access_count += 1
                entry.last_accessed = time.time()

                # Check if expired
                if entry.is_expired():
                    logger.debug(f"Cache expired: {path.name}")
                    return None

                # Write back updated stats
                self._write_cache_file(path, entry)

                self._stats.cache_hits += 1
                return entry

        except Exception as e:
            logger.warning(f"Failed to read cache file {path}: {e}")
            return None

    def _write_cache_file(self, path: Path, entry: CacheEntry) -> None:
        """Write cache entry to file atomically.

        Args:
            path: Path to cache file
            entry: Cache entry to write
        """
        try:
            # Write to temporary file first
            temp_path = path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(asdict(entry), f, indent=2)

            # Atomic rename
            temp_path.replace(path)

        except Exception as e:
            logger.error(f"Failed to write cache file {path}: {e}")
            if temp_path.exists():
                temp_path.unlink()

    def get_repo_cache_key(self, owner: str, repo: str) -> str:
        """Generate cache key for repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Cache key string
        """
        return f"{owner}_{repo}".replace("/", "_").lower()

    def get_search_cache_key(self, query: str, asset_type: str | None = None) -> str:
        """Generate cache key for search query.

        Args:
            query: Search query string
            asset_type: Asset type filter (optional)

        Returns:
            Cache key (hash of query + type)
        """
        key_data = f"{query.lower()}|{asset_type or 'all'}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    def get_repo_index(self, owner: str, repo: str) -> dict[str, Any] | None:
        """Get cached repository index.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Cached index data or None if not cached/expired
        """
        key = self.get_repo_cache_key(owner, repo)
        path = self._get_cache_path("repo_index", key)
        entry = self._read_cache_file(path)

        if entry and entry.is_valid():
            logger.debug(f"Cache hit: repo_index/{key}")
            return entry.data

        logger.debug(f"Cache miss: repo_index/{key}")
        self._stats.cache_misses += 1
        return None

    def set_repo_index(
        self,
        owner: str,
        repo: str,
        packages: list[dict[str, Any]],
        ttl: int = DEFAULT_TTL,
    ) -> None:
        """Cache repository index.

        Args:
            owner: Repository owner
            repo: Repository name
            packages: List of packages to cache
            ttl: Time-to-live in seconds (default: 24 hours)
        """
        key = self.get_repo_cache_key(owner, repo)
        path = self._get_cache_path("repo_index", key)

        now = time.time()
        entry = CacheEntry(
            key=key,
            data={
                "owner": owner,
                "repo": repo,
                "packages": packages,
                "total_count": len(packages),
            },
            cached_at=now,
            expires_at=now + ttl,
            access_count=0,
            last_accessed=now,
        )

        self._write_cache_file(path, entry)
        logger.info(f"Cached {len(packages)} packages for {owner}/{repo}")

        # Update metadata
        self._stats.last_refresh = now
        self._save_metadata()

    def get_search_results(
        self, query: str, asset_type: str | None = None
    ) -> list[dict[str, Any]] | None:
        """Get cached search results.

        Args:
            query: Search query
            asset_type: Asset type filter

        Returns:
            Cached results or None if not cached/expired
        """
        key = self.get_search_cache_key(query, asset_type)
        path = self._get_cache_path("search_result", key)
        entry = self._read_cache_file(path)

        if entry and entry.is_valid():
            logger.debug(f"Cache hit: search_result/{key}")
            return entry.data.get("results", [])

        logger.debug(f"Cache miss: search_result/{key}")
        self._stats.cache_misses += 1
        return None

    def set_search_results(
        self,
        query: str,
        asset_type: str | None,
        results: list[dict[str, Any]],
        ttl: int = DEFAULT_TTL,
    ) -> None:
        """Cache search results.

        Args:
            query: Search query
            asset_type: Asset type filter
            results: Search results to cache
            ttl: Time-to-live in seconds
        """
        key = self.get_search_cache_key(query, asset_type)
        path = self._get_cache_path("search_result", key)

        now = time.time()
        entry = CacheEntry(
            key=key,
            data={"query": query, "asset_type": asset_type, "results": results},
            cached_at=now,
            expires_at=now + ttl,
            access_count=0,
            last_accessed=now,
        )

        self._write_cache_file(path, entry)
        logger.info(f"Cached {len(results)} search results for query: {query}")

    def clear(self, cache_key: str | None = None) -> int:
        """Clear cache entries.

        Args:
            cache_key: Specific key to clear (None = clear all)

        Returns:
            Number of entries cleared
        """
        cleared = 0

        if cache_key:
            # Clear specific entry
            for subdir in [self.repo_indexes_dir, self.search_results_dir]:
                cache_file = subdir / f"{cache_key}.json"
                if cache_file.exists():
                    cache_file.unlink()
                    cleared += 1
                    logger.info(f"Cleared cache: {cache_key}")
        else:
            # Clear all
            for subdir in [self.repo_indexes_dir, self.search_results_dir]:
                for cache_file in subdir.glob("*.json"):
                    cache_file.unlink()
                    cleared += 1

            logger.info(f"Cleared all cache entries ({cleared} files)")

        # Reset stats
        if not cache_key:
            self._stats = CacheStats()
            self._save_metadata()

        return cleared

    def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats object
        """
        # Update current stats
        self._stats.total_entries = sum(
            1
            for d in [self.repo_indexes_dir, self.search_results_dir]
            for _ in d.glob("*.json")
        )

        self._stats.total_size_bytes = sum(
            f.stat().st_size
            for d in [self.repo_indexes_dir, self.search_results_dir]
            for f in d.glob("*.json")
        )

        # List cached repos
        repos = []
        for cache_file in self.repo_indexes_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    entry = CacheEntry(**data)
                    if entry.is_valid():
                        repo_data = entry.data
                        repos.append(f"{repo_data['owner']}/{repo_data['repo']}")
            except Exception:
                continue

        self._stats.repos_cached = repos

        return self._stats

    def is_expired(self, cache_key: str, cache_type: str = "repo_index") -> bool:
        """Check if cache entry is expired.

        Args:
            cache_key: Cache key
            cache_type: Type of cache entry

        Returns:
            True if expired or doesn't exist
        """
        path = self._get_cache_path(cache_type, cache_key)
        if not path.exists():
            return True

        try:
            with open(path) as f:
                data = json.load(f)
                entry = CacheEntry(**data)
                return entry.is_expired()
        except Exception:
            return True


def paginate(items: list[Any], offset: int = 0, limit: int = 20) -> dict[str, Any]:
    """Paginate a list of items.

    Args:
        items: List to paginate
        offset: Starting index
        limit: Items per page

    Returns:
        Dictionary with paginated items and pagination metadata
    """
    total = len(items)
    start = max(0, offset)
    end = min(offset + limit, total)

    return {
        "items": items[start:end],
        "pagination": {
            "offset": offset,
            "limit": limit,
            "total": total,
            "count": end - start,
            "has_next": end < total,
            "has_prev": offset > 0,
            "current_page": (offset // limit) + 1,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
        },
    }


__all__ = ["CacheEntry", "CacheStats", "MarketplaceCache", "paginate"]
