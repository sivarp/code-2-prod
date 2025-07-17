"""
End-to-end tests for GitHub Gists API
"""

import time
import concurrent.futures
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestE2E:
    """End-to-end test suite for the GitHub Gists API"""

    def test_health_endpoint_e2e(self):
        """Test health endpoint returns expected response"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "GitHub Gists API"
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_octocat_gists_e2e(self):
        """
        End-to-end test using GitHub's official octocat user
        This validates the entire API pipeline including:
        - GitHub API integration
        - Response parsing
        - Pydantic model validation
        - Caching functionality
        """
        response = client.get("/octocat")
        assert response.status_code == 200

        data = response.json()

        # Validate response structure
        assert "username" in data
        assert "total_gists" in data
        assert "gists" in data

        # Validate octocat user
        assert data["username"] == "octocat"
        assert isinstance(data["total_gists"], int)
        assert data["total_gists"] >= 0
        assert isinstance(data["gists"], list)

        # If gists exist, validate structure
        if data["gists"]:
            gist = data["gists"][0]

            # Validate required gist fields
            required_fields = ["id", "public", "created_at", "files", "html_url"]
            for field in required_fields:
                assert field in gist, f"Missing required field: {field}"

            # Validate gist data types
            assert isinstance(gist["id"], str)
            assert isinstance(gist["public"], bool)
            assert isinstance(gist["created_at"], str)
            assert isinstance(gist["files"], list)
            assert isinstance(gist["html_url"], str)

            # Validate file structure if files exist
            if gist["files"]:
                file_obj = gist["files"][0]
                assert "filename" in file_obj
                assert "size" in file_obj
                assert isinstance(file_obj["filename"], str)
                assert isinstance(file_obj["size"], int)
                # language can be null for some files
                if "language" in file_obj and file_obj["language"] is not None:
                    assert isinstance(file_obj["language"], str)

    @pytest.mark.e2e
    def test_octocat_gists_pagination_e2e(self):
        """Test pagination functionality with octocat user"""
        # Test first page
        response = client.get("/octocat?page=1&per_page=5")
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "octocat"
        assert len(data["gists"]) <= 5  # Should not exceed requested per_page

        # Test second page (if first page has results)
        if data["gists"]:
            response = client.get("/octocat?page=2&per_page=5")
            assert response.status_code == 200

            data_page2 = response.json()
            assert data_page2["username"] == "octocat"

    @pytest.mark.e2e
    def test_octocat_gists_caching_e2e(self):
        """Test that caching works by making multiple requests"""
        # First request - should hit GitHub API
        response1 = client.get("/octocat?page=1&per_page=3")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - should hit cache
        response2 = client.get("/octocat?page=1&per_page=3")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical (from cache)
        assert data1 == data2
        assert data1["username"] == "octocat"

    @pytest.mark.e2e
    def test_nonexistent_user_e2e(self):
        """Test error handling for non-existent user"""
        # Use a username that's very unlikely to exist
        nonexistent_user = "thisusershouldnotexist12345"
        response = client.get(f"/{nonexistent_user}")

        # Should return 404 for non-existent user
        assert response.status_code == 404

        error_data = response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "User not found"

    @pytest.mark.e2e
    def test_pagination_parameters_validation_e2e(self):
        """Test pagination parameter validation"""
        # Test invalid page number (too low)
        response = client.get("/octocat?page=0")
        assert response.status_code == 422  # Validation error

        # Test invalid per_page (too high)
        response = client.get("/octocat?per_page=101")
        assert response.status_code == 422  # Validation error

        # Test valid parameters
        response = client.get("/octocat?page=1&per_page=50")
        assert response.status_code == 200
