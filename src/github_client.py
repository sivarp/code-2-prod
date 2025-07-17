"""
GitHub API client for fetching gists
"""

from typing import List

import httpx
from fastapi import HTTPException

from .cache import cache_gists, get_cached_gists


async def fetch_user_gists(username: str, page: int, per_page: int) -> List[dict]:
    """
    Fetch user gists from GitHub API with caching

    Args:
        username: GitHub username
        page: Page number (1-based)
        per_page: Number of items per page (1-100)

    Returns:
        List of gist data dictionaries

    Raises:
        HTTPException: If user not found or API error
    """
    # Check cache first
    cached_data = get_cached_gists(username, page, per_page)
    if cached_data is not None:
        return cached_data

    # Fetch from GitHub API
    url = f"https://api.github.com/users/{username}/gists"
    params = {"page": page, "per_page": per_page}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        response.raise_for_status()
        data = response.json()

        # Cache the result
        cache_gists(username, page, per_page, data)

        return data
