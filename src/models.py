"""
Data models for GitHub Gists API
"""

from typing import List, Optional
from pydantic import BaseModel


class GistFile(BaseModel):
    """Represents a file within a gist"""

    filename: str
    language: Optional[str] = None
    size: int


class Gist(BaseModel):
    """Represents a GitHub gist"""

    id: str
    description: Optional[str] = None
    public: bool
    created_at: str
    files: List[GistFile]
    html_url: str


class UserGistsResponse(BaseModel):
    """Response model for user gists endpoint"""

    username: str
    total_gists: int
    gists: List[Gist]
