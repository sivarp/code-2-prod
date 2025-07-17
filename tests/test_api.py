"""
Tests for GitHub Gists API
"""

import time
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.cache import (
    cache_gists,
    get_cache_key,
    get_cached_gists,
    is_cache_valid,
    _cache,
)
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "GitHub Gists API", "status": "healthy"}


@patch("src.main.fetch_user_gists")
def test_get_user_gists_success(mock_fetch):
    """Test successful gist retrieval"""
    # Mock data
    mock_fetch.return_value = [
        {
            "id": "abc123",
            "description": "Test gist",
            "public": True,
            "created_at": "2023-01-01T00:00:00Z",
            "html_url": "https://gist.github.com/test/abc123",
            "files": {"test.py": {"language": "Python", "size": 100}},
        }
    ]

    response = client.get("/testuser")
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert data["total_gists"] == 1
    assert len(data["gists"]) == 1

    gist = data["gists"][0]
    assert gist["id"] == "abc123"
    assert gist["description"] == "Test gist"
    assert len(gist["files"]) == 1


@patch("src.main.fetch_user_gists")
def test_get_user_gists_with_pagination(mock_fetch):
    """Test pagination parameters"""
    mock_fetch.return_value = []
    response = client.get("/testuser?page=2&per_page=10")
    assert response.status_code == 200
    mock_fetch.assert_called_once_with("testuser", 2, 10)


def test_cache_key_generation():
    """Test cache key generation"""
    key1 = get_cache_key("user1", 1, 30)
    key2 = get_cache_key("user1", 1, 30)
    key3 = get_cache_key("user2", 1, 30)

    assert key1 == key2  # Same params = same key
    assert key1 != key3  # Different user = different key


def test_cache_validity():
    """Test cache TTL logic"""
    current_time = time.time()
    assert is_cache_valid(current_time) is True
    assert is_cache_valid(current_time - 400) is False  # Older than TTL


def test_cache_operations():
    """Test cache get and set operations"""
    # Clear cache before test
    _cache.clear()

    # Test cache miss
    result = get_cached_gists("testuser", 1, 30)
    assert result is None

    # Test cache hit
    test_data = [{"id": "test", "public": True}]
    cache_gists("testuser", 1, 30, test_data)
    result = get_cached_gists("testuser", 1, 30)
    assert result == test_data
