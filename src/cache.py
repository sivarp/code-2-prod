"""
In-memory caching for GitHub API responses
"""

import hashlib
import os
import time
from typing import Dict, List, Optional, Tuple

# In-memory cache storage
_cache: Dict[str, Tuple[List[dict], float]] = {}
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # Default: 5 minutes


def get_cache_key(username: str, page: int, per_page: int) -> str:
    """Generate cache key for request parameters"""
    return hashlib.md5(f"{username}-{page}-{per_page}".encode()).hexdigest()


def is_cache_valid(timestamp: float) -> bool:
    """Check if cache entry is still valid"""
    return time.time() - timestamp < CACHE_TTL


def get_cached_gists(username: str, page: int, per_page: int) -> Optional[List[dict]]:
    """Get gists from cache if available and valid"""
    cache_key = get_cache_key(username, page, per_page)

    if cache_key in _cache:
        data, timestamp = _cache[cache_key]
        if is_cache_valid(timestamp):
            return data

    return None


def cache_gists(username: str, page: int, per_page: int, data: List[dict]) -> None:
    """Cache gists data with current timestamp"""
    cache_key = get_cache_key(username, page, per_page)
    _cache[cache_key] = (data, time.time())
