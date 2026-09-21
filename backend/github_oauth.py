import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, GitHubConnection, Repository
from backend.security import (
    SECRET_KEY,
    ALGORITHM,
    get_current_user
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

GITHUB_AUTHORIZE_URL = (
    "https://github.com/login/oauth/authorize"
)

GITHUB_TOKEN_URL = (
    "https://github.com/login/oauth/access_token"
)

GITHUB_API_URL = "https://api.github.com"

GITHUB_REDIRECT_URI = (
    "http://127.0.0.1:8001/auth/github/callback"
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth/github",
    tags=["GitHub OAuth"]
)


# =========================================================
# GITHUB LOGIN
# =========================================================

@router.get("/login")
def github_login(token: str):

    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GitHub Client ID is not configured"
        )

    # -----------------------------------------------------
    # Decode RepoRescue JWT
    # -----------------------------------------------------

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    # -----------------------------------------------------
    # Create OAuth State
    # -----------------------------------------------------

    state_payload = {
        "user_id": user_id,
        "purpose": "github_oauth",
        "exp": (
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        )
    }

    state = jwt.encode(
        state_payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # -----------------------------------------------------
    # GitHub Authorization URL
    # -----------------------------------------------------

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "repo",
        "state": state
    }

    github_url = (
        f"{GITHUB_AUTHORIZE_URL}?"
        f"{urlencode(params)}"
    )

    return RedirectResponse(
        url=github_url
    )


# =========================================================
# GITHUB CALLBACK
# =========================================================

@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):

    if (
        not GITHUB_CLIENT_ID
        or not GITHUB_CLIENT_SECRET
    ):
        raise HTTPException(
            status_code=500,
            detail=(
                "GitHub OAuth credentials "
                "are not configured"
            )
        )

    # -----------------------------------------------------
    # Validate OAuth State
    # -----------------------------------------------------

    try:

        payload = jwt.decode(
            state,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("purpose") != "github_oauth":

            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state"
            )

        user_id = payload.get("user_id")

        if not user_id:

            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state user"
            )

    except JWTError:

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state"
        )

    # -----------------------------------------------------
    # Find RepoRescue User
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id)
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="RepoRescue user not found"
        )

    # -----------------------------------------------------
    # Exchange Authorization Code
    # -----------------------------------------------------

    token_data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI
    }

    async with httpx.AsyncClient() as client:

        token_response = await client.post(
            GITHUB_TOKEN_URL,
            data=token_data,
            headers={
                "Accept": "application/json"
            }
        )

    if token_response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to exchange "
                "GitHub authorization code"
            )
        )

    token_json = token_response.json()

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        raise HTTPException(
            status_code=400,
            detail=(
                "GitHub access token "
                "was not received"
            )
        )

    # -----------------------------------------------------
    # Get GitHub User Information
    # -----------------------------------------------------

    github_headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Accept": (
            "application/vnd.github+json"
        )
    }

    async with httpx.AsyncClient() as client:

        github_user_response = await client.get(
            f"{GITHUB_API_URL}/user",
            headers=github_headers
        )

    if github_user_response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to retrieve "
                "GitHub user"
            )
        )

    github_user = (
        github_user_response.json()
    )

    github_user_id = str(
        github_user.get("id")
    )

    github_username = github_user.get(
        "login"
    )

    if (
        not github_user_id
        or not github_username
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid GitHub user information"
            )
        )

    # -----------------------------------------------------
    # Save / Update GitHub Connection
    # -----------------------------------------------------

    connection = (
        db.query(GitHubConnection)
        .filter(
            GitHubConnection.user_id == user.id
        )
        .first()
    )

    if connection:

        connection.github_user_id = (
            github_user_id
        )

        connection.github_username = (
            github_username
        )

        connection.access_token = (
            access_token
        )

        connection.updated_at = (
            datetime.now(timezone.utc)
        )

    else:

        connection = GitHubConnection(
            user_id=user.id,
            github_user_id=github_user_id,
            github_username=github_username,
            access_token=access_token
        )

        db.add(connection)

    db.commit()

    # -----------------------------------------------------
    # Redirect back to Frontend
    # -----------------------------------------------------
    #
    # GitHub OAuth success → RepoRescue frontend
    #
    # -----------------------------------------------------

    frontend_url = (
        "http://localhost:5174"
        "?github=connected"
    )

    return RedirectResponse(
        url=frontend_url
    )


# =========================================================
# GET AUTHORIZED GITHUB REPOSITORIES
# =========================================================

@router.get("/repositories")
async def get_github_repositories(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Current RepoRescue User
    # -----------------------------------------------------

    user_id = current_user["user_id"]

    # -----------------------------------------------------
    # Get ONLY this user's GitHub connection
    # -----------------------------------------------------

    connection = (
        db.query(GitHubConnection)
        .filter(
            GitHubConnection.user_id == user_id
        )
        .first()
    )

    if not connection:

        raise HTTPException(
            status_code=404,
            detail="GitHub account is not connected"
        )

    # -----------------------------------------------------
    # GitHub Headers
    # -----------------------------------------------------

    github_headers = {
        "Authorization": (
            f"Bearer {connection.access_token}"
        ),
        "Accept": (
            "application/vnd.github+json"
        )
    }

    # -----------------------------------------------------
    # Get Authorized Repositories
    # -----------------------------------------------------

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{GITHUB_API_URL}/user/repos",
            headers=github_headers,
            params={
                "visibility": "all",
                "affiliation": (
                    "owner,collaborator,"
                    "organization_member"
                ),
                "sort": "updated",
                "per_page": 100
            }
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to retrieve "
                "GitHub repositories"
            )
        )

    repositories = response.json()

    # -----------------------------------------------------
    # Safe Repository Response
    # -----------------------------------------------------

    repo_list = []

    for repo in repositories:

        repo_list.append({

            "id": repo.get("id"),

            "name": repo.get("name"),

            "full_name": repo.get(
                "full_name"
            ),

            "private": repo.get(
                "private"
            ),

            "html_url": repo.get(
                "html_url"
            ),

            "owner": (
                repo.get("owner", {})
                .get("login")
            )
        })

    return {
        "github_connected": True,
        "repositories": repo_list
    }


# =========================================================
# SELECT GITHUB REPOSITORY
# =========================================================

@router.post("/select-repository")
async def select_repository(
    github_repo_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Current RepoRescue User
    # -----------------------------------------------------

    user_id = current_user["user_id"]

    # -----------------------------------------------------
    # Get ONLY current user's GitHub connection
    # -----------------------------------------------------

    connection = (
        db.query(GitHubConnection)
        .filter(
            GitHubConnection.user_id == user_id
        )
        .first()
    )

    if not connection:

        raise HTTPException(
            status_code=404,
            detail="GitHub account is not connected"
        )

    # -----------------------------------------------------
    # GitHub Access Token
    # -----------------------------------------------------

    access_token = (
        connection.access_token
    )

    github_headers = {
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Accept": (
            "application/vnd.github+json"
        )
    }

    # -----------------------------------------------------
    # Verify Repository Access
    # -----------------------------------------------------

    async with httpx.AsyncClient() as client:

        repo_response = await client.get(
            f"{GITHUB_API_URL}/repositories/{github_repo_id}",
            headers=github_headers
        )

    if repo_response.status_code != 200:

        raise HTTPException(
            status_code=403,
            detail=(
                "Repository is not accessible "
                "by the connected GitHub account"
            )
        )

    repo = repo_response.json()

    # -----------------------------------------------------
    # Repository Information
    # -----------------------------------------------------

    repo_name = repo.get("name")

    repo_url = repo.get("html_url")

    repo_owner = (
        repo.get("owner", {})
        .get("login")
    )

    if (
        not repo_name
        or not repo_url
        or not repo_owner
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid repository information"
            )
        )

    # -----------------------------------------------------
    # Save Repository
    # -----------------------------------------------------

    existing_repository = (
        db.query(Repository)
        .filter(
            Repository.owner_id == user_id,
            Repository.github_url == repo_url
        )
        .first()
    )

    if existing_repository:

        repository = existing_repository

    else:

        repository = Repository(
            name=repo_name,
            github_url=repo_url,
            owner_id=user_id
        )

        db.add(repository)

        db.commit()

        db.refresh(repository)

    # -----------------------------------------------------
    # Return Workspace Information
    # -----------------------------------------------------

    return {

        "message": (
            "Repository selected successfully"
        ),

        "repository": {

            "id": repository.id,

            "name": repository.name,

            "github_url": (
                repository.github_url
            ),

            "github_owner": repo_owner,

            "owner_id": repository.owner_id
        },

        "workspace": {

            "repository_id": repository.id,

            "repository_name": (
                repository.name
            )
        }
    }