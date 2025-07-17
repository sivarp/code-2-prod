"""
FastAPI GitHub Gists API
"""

import uvicorn
from fastapi import FastAPI, Query

from .github_client import fetch_user_gists
from .models import Gist, GistFile, UserGistsResponse

app = FastAPI(title="GitHub Gists API", version="1.0.0")


@app.get("/")
async def health():
    """Health check endpoint"""
    return {"message": "GitHub Gists API", "status": "healthy"}


@app.get("/{username}", response_model=UserGistsResponse)
async def get_user_gists(
    username: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
):
    """Get user's gists with pagination"""
    gists_data = await fetch_user_gists(username, page, per_page)

    gists = []
    for gist_data in gists_data:
        files = [
            GistFile(
                filename=filename,
                language=file_info.get("language"),
                size=file_info.get("size", 0),
            )
            for filename, file_info in gist_data.get("files", {}).items()
        ]

        gist = Gist(
            id=gist_data["id"],
            description=gist_data.get("description"),
            public=gist_data["public"],
            created_at=gist_data["created_at"],
            files=files,
            html_url=gist_data["html_url"],
        )
        gists.append(gist)

    return UserGistsResponse(
        username=username,
        total_gists=len(gists),
        gists=gists,
    )


def main():
    """Entry point"""
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
